
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import Home from './pages/Home'
import Companies from './pages/Companies'
import Drives from './pages/Drives'
import DriveDetails from './pages/DriveDetails'
import Intelligence from './pages/Intelligence'
import Register from './pages/Register'
import Login from './pages/Login'
import SubmitExperience from './pages/submitExperience'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/companies" element={<Companies />} />

        <Route path="/drives" element={<Drives />} />
        <Route path="/drives/:driveId" element={<DriveDetails />} />

        <Route path="/intelligence" element={<Intelligence />} />

        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        <Route
          path="/experiences"
          element={<Navigate to="/experiences/new" replace />}
        />

        <Route
          path="/experiences/new"
          element={<SubmitExperience />}
        />

        <Route
          path="*"
          element={
            <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-6">
              <h1 className="text-3xl font-bold text-gray-900">
                Page not found
              </h1>
              <p className="mt-2 text-gray-600">
                The page you requested doesn't exist.
              </p>
              <a href="/" className="mt-4 text-blue-700 underline">
                Return home
              </a>
            </main>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App

