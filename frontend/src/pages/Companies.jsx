import { useEffect, useState } from 'react'
import api from '../services/api'

function Companies() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const response = await api.get('/companies/')
        setCompanies(response.data)
      } catch (err) {
        setError('Unable to load companies.')
      } finally {
        setLoading(false)
      }
    }

    fetchCompanies()
  }, [])

  return (
    <main className="min-h-screen bg-gray-50">
      <section className="mx-auto max-w-6xl px-6 py-12">
        <h1 className="text-3xl font-bold text-gray-900">
          Companies
        </h1>

        <p className="mt-2 text-gray-600">
          Explore companies that have appeared in placement drives.
        </p>

        {loading && (
          <p className="mt-8 text-gray-600">
            Loading companies...
          </p>
        )}

        {error && (
          <p className="mt-8 text-red-600">
            {error}
          </p>
        )}

        {!loading && !error && (
          <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {companies.map((company) => (
              <div
                key={company.id}
                className="rounded-lg border border-gray-200 bg-white p-6"
              >
                <h2 className="text-lg font-semibold text-gray-900">
                  {company.name}
                </h2>

                <p className="mt-2 text-sm text-gray-500">
                  {company.industry || 'Industry not specified'}
                </p>

                {company.description && (
                  <p className="mt-4 text-sm leading-6 text-gray-600">
                    {company.description}
                  </p>
                )}

                <button className="mt-5 text-sm font-medium text-blue-700 hover:text-blue-800">
                  View placement drives →
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  )
}

export default Companies