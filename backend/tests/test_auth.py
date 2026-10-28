
from datetime import timedelta

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import auth
from app.core.permissions import require_reviewer
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User

auth_test_app = FastAPI()
auth_test_app.include_router(auth.router, prefix="/api/v1")


@auth_test_app.get("/protected")
async def protected_route(
    user: User = Depends(get_current_user),
):
    return {"user_id": user.id}


@auth_test_app.get("/reviewer")
async def reviewer_route(
    user: User = Depends(require_reviewer),
):
    return {"role": user.role}


class FakeResult:
    def __init__(self, user=None):
        self.user = user

    def scalar_one_or_none(self):
        return self.user


class FakeDB:
    """Small database mock for authentication endpoint tests."""

    def __init__(self, user=None):
        self.user_to_return = user
        self.added_user = None

    async def execute(self, query):
        return FakeResult(self.user_to_return)

    def add(self, user):
        self.added_user = user

    async def commit(self):
        pass

    async def refresh(self, user):
        if user.id is None:
            user.id = 2


client = TestClient(auth_test_app)


def make_user(
    role: str = "STUDENT",
    is_active: bool = True,
    password: str = "TestPassword123!",
) -> User:
    return User(
        id=1,
        name="Test User",
        email="test@example.com",
        password_hash=hash_password(password),
        role=role,
        verification_status="PENDING",
        is_active=is_active,
    )


def use_fake_db(fake_db):
    auth_test_app.dependency_overrides[get_db] = lambda: fake_db


def clear_overrides():
    auth_test_app.dependency_overrides.clear()


# --------------------------------------------------
# Existing authentication and permission tests
# --------------------------------------------------

def test_missing_token_returns_401():
    response = client.get("/protected")

    assert response.status_code == 401


def test_invalid_token_returns_401():
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_password_hash_and_verification():
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_access_token_contains_user_data():
    token = create_access_token(
        {"sub": "1", "role": "STUDENT"}
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["role"] == "STUDENT"
    assert "exp" in payload


def test_expired_token_is_rejected():
    token = create_access_token(
        {"sub": "1", "role": "STUDENT"},
        expires_delta=timedelta(seconds=-1),
    )

    try:
        decode_access_token(token)
    except jwt.ExpiredSignatureError:
        pass
    else:
        raise AssertionError("Expected expired token to be rejected")


def test_student_cannot_access_reviewer_route():
    auth_test_app.dependency_overrides[get_current_user] = (
        lambda: make_user(role="STUDENT")
    )

    try:
        response = client.get("/reviewer")

        assert response.status_code == 403
        assert response.json()["detail"] == "Reviewer access required"
    finally:
        clear_overrides()


def test_reviewer_can_access_reviewer_route():
    auth_test_app.dependency_overrides[get_current_user] = (
        lambda: make_user(role="REVIEWER")
    )

    try:
        response = client.get("/reviewer")

        assert response.status_code == 200
        assert response.json()["role"] == "REVIEWER"
    finally:
        clear_overrides()


# --------------------------------------------------
# Registration endpoint tests
# --------------------------------------------------

def test_registration_succeeds():
    fake_db = FakeDB()
    use_fake_db(fake_db)

    try:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "New Student",
                "email": "newstudent@example.com",
                "password": "StudentPass123!",
                "role": "STUDENT",
            },
        )

        assert response.status_code == 201
        assert response.json()["message"] == "Registration successful"
        assert response.json()["user_id"] == 2
        assert response.json()["role"] == "STUDENT"
        assert response.json()["verification_status"] == "PENDING"

        assert fake_db.added_user is not None
        assert fake_db.added_user.password_hash != "StudentPass123!"
        assert verify_password(
            "StudentPass123!",
            fake_db.added_user.password_hash,
        )
    finally:
        clear_overrides()


def test_registration_rejects_duplicate_email():
    existing_user = make_user()
    fake_db = FakeDB(user=existing_user)
    use_fake_db(fake_db)

    try:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Another Student",
                "email": "test@example.com",
                "password": "StudentPass123!",
                "role": "STUDENT",
            },
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already registered"
    finally:
        clear_overrides()


def test_registration_rejects_reviewer_role():
    fake_db = FakeDB()
    use_fake_db(fake_db)

    try:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Reviewer User",
                "email": "reviewer@example.com",
                "password": "ReviewerPass123!",
                "role": "REVIEWER",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Only STUDENT or ALUMNI registration is allowed"
        )
        assert fake_db.added_user is None
    finally:
        clear_overrides()


# --------------------------------------------------
# Login endpoint tests
# --------------------------------------------------

def test_login_succeeds_with_correct_password():
    user = make_user()
    fake_db = FakeDB(user=user)
    use_fake_db(fake_db)

    try:
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 200

        body = response.json()
        assert body["access_token"]
        assert body["token_type"] == "bearer"

        payload = decode_access_token(body["access_token"])
        assert payload["sub"] == "1"
        assert payload["role"] == "STUDENT"
    finally:
        clear_overrides()


def test_login_rejects_incorrect_password():
    user = make_user()
    fake_db = FakeDB(user=user)
    use_fake_db(fake_db)

    try:
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"
    finally:
        clear_overrides()


def test_login_rejects_inactive_account():
    user = make_user(is_active=False)
    fake_db = FakeDB(user=user)
    use_fake_db(fake_db)

    try:
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "User account is inactive"
    finally:
        clear_overrides()
