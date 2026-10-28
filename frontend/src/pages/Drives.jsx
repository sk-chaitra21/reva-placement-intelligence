import { useEffect, useState } from 'react'
import api from '../services/api'
import { Link } from 'react-router-dom'

function Drives() {
  const [drives, setDrives] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDrives = async () => {
      try {
        const response = await api.get('/placement-drives/search')
        setDrives(response.data)
      } catch (err) {
        setError('Unable to load placement drives.')
      } finally {
        setLoading(false)
      }
    }

    fetchDrives()
  }, [])

  return (
    <main className="min-h-screen bg-gray-50">
      <section className="mx-auto max-w-6xl px-6 py-12">
        <h1 className="text-3xl font-bold text-gray-900">
          Placement Drives
        </h1>

        <p className="mt-2 text-gray-600">
          Explore placement drives, eligibility, and selection information.
        </p>

        {loading && (
          <p className="mt-8 text-gray-600">
            Loading placement drives...
          </p>
        )}

        {error && (
          <p className="mt-8 text-red-600">
            {error}
          </p>
        )}

        {!loading && !error && (
          <div className="mt-8 space-y-4">
            {drives.map((item) => (
              <div
                key={item.placement_drive.id}
                className="rounded-lg border border-gray-200 bg-white p-6"
              >
                <div className="flex flex-col justify-between gap-4 md:flex-row">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {item.company.name}
                    </h2>

                    <p className="mt-1 text-sm text-gray-500">
                      {item.placement_drive.academic_year}
                    </p>

                    <p className="mt-3 text-gray-700">
                      {item.placement_drive.title}
                    </p>
                  </div>

                  <div className="text-sm text-gray-600">
                    <p>
                      CGPA:{' '}
                      {item.eligibility?.minimum_cgpa ?? 'Not specified'}
                    </p>

                    <p className="mt-1">
                      Branches:{' '}
                      {item.eligibility?.eligible_branches ??
                        'Not specified'}
                    </p>
                  </div>
                </div>

                <Link
  to={`/drives/${item.placement_drive.id}`}
  className="mt-5 inline-block text-sm font-medium text-blue-700 hover:text-blue-800"
>
  View placement intelligence →
</Link>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  )
}

export default Drives