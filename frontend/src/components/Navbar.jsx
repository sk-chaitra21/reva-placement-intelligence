import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        
        <Link
          to="/"
          className="text-lg font-semibold text-gray-900"
        >
          REVA Placement Intelligence
        </Link>

        <div className="flex items-center gap-6 text-sm">
          
          <Link
            to="/"
            className="text-gray-600 hover:text-gray-900"
          >
            Home
          </Link>

          <Link
            to="/companies"
            className="text-gray-600 hover:text-gray-900"
          >
            Companies
          </Link>

          <Link
            to="/drives"
            className="text-gray-600 hover:text-gray-900"
          >
            Placement Drives
          </Link>

          <Link
            to="/intelligence"
            className="text-gray-600 hover:text-gray-900"
          >
            Intelligence
          </Link>

          <Link
            to="/experiences"
            className="text-gray-600 hover:text-gray-900"
          >
            Experiences
          </Link>

          <Link
            to="/login"
            className="rounded-md bg-blue-700 px-4 py-2 font-medium text-white hover:bg-blue-800"
          >
            Login
          </Link>

        </div>
      </div>
    </nav>
  )
}

export default Navbar