
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

function Home() {
  return (
    <>
      <Navbar />

      <main className="min-h-screen bg-gray-50">
        <section className="mx-auto max-w-6xl px-6 py-16">
          <div className="max-w-3xl">
            <p className="mb-3 text-sm font-semibold text-blue-700">
              REVA Placement Intelligence
            </p>

            <h1 className="text-4xl font-bold tracking-tight text-gray-900 md:text-5xl">
              Understand placements before placement season.
            </h1>

            <p className="mt-5 text-lg leading-8 text-gray-600">
              Explore placement drives, eligibility criteria, selection rounds,
              and verified experiences from students and alumni.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/drives"
                className="rounded-md bg-blue-700 px-5 py-3 font-medium text-white hover:bg-blue-800"
              >
                Explore Placement Drives
              </Link>

              <Link
                to="/companies"
                className="rounded-md border border-gray-300 bg-white px-5 py-3 font-medium text-gray-700 hover:bg-gray-100"
              >
                Explore Companies
              </Link>
            </div>
          </div>
        </section>

        <section className="border-t border-gray-200 bg-white">
          <div className="mx-auto grid max-w-6xl gap-6 px-6 py-12 md:grid-cols-3">
            <Link
              to="/drives"
              className="rounded-lg border border-gray-200 p-5 transition hover:border-blue-300 hover:shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-900">
                Placement Drives
              </h2>
              <p className="mt-2 leading-6 text-gray-600">
                Discover historical and available placement drives.
              </p>
              <span className="mt-4 inline-block text-sm font-semibold text-blue-700">
                Browse drives →
              </span>
            </Link>

            <Link
              to="/experiences"
              className="rounded-lg border border-gray-200 p-5 transition hover:border-blue-300 hover:shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-900">
                Share Your Experience
              </h2>
              <p className="mt-2 leading-6 text-gray-600">
                Contribute placement experiences and preparation strategies.
              </p>
              <span className="mt-4 inline-block text-sm font-semibold text-blue-700">
                Share experience →
              </span>
            </Link>

            <Link
              to="/intelligence"
              className="rounded-lg border border-gray-200 p-5 transition hover:border-blue-300 hover:shadow-sm"
            >
              <h2 className="text-lg font-semibold text-gray-900">
                Placement Intelligence
              </h2>
              <p className="mt-2 leading-6 text-gray-600">
                Ask questions and explore answers grounded in verified evidence.
              </p>
              <span className="mt-4 inline-block text-sm font-semibold text-blue-700">
                Explore intelligence →
              </span>
            </Link>
          </div>
        </section>
      </main>
    </>
  )
}

export default Home
