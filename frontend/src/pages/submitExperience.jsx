
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function SubmitExperience() {
  const navigate = useNavigate()

  const [drives, setDrives] = useState([])
  const [placementDriveId, setPlacementDriveId] = useState('')
  const [experienceType, setExperienceType] = useState(
    'PLACEMENT_EXPERIENCE',
  )
  const [content, setContent] = useState('')
  const [loadingDrives, setLoadingDrives] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    async function loadDrives() {
      try {
        const response = await api.get('/placement-drives/search')
        const data = response.data

        setDrives(Array.isArray(data) ? data : [])
      } catch (err) {
        console.error(
          'Failed to load placement drives:',
          err.response?.data || err.message,
        )
        setError(
          'Unable to load placement drives. Please refresh and try again.',
        )
      } finally {
        setLoadingDrives(false)
      }
    }

    loadDrives()
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (!placementDriveId) {
      setError('Please select a placement drive.')
      return
    }

    if (content.trim().length < 10) {
      setError('Please describe your experience using at least 10 characters.')
      return
    }

    const token = localStorage.getItem('access_token')

    if (!token) {
      navigate('/login')
      return
    }

    setSubmitting(true)

    try {
      const response = await api.post(
        '/experiences/',
        {
          placement_drive_id: Number(placementDriveId),
          experience_type: experienceType,
          content: content.trim(),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      setSuccess(
        `Experience submitted successfully! Submission ID: ${response.data.id}. Status: ${response.data.status}.`,
      )

      setContent('')
      setPlacementDriveId('')
    } catch (err) {
      console.error(
        'Experience submission failed:',
        err.response?.data || err.message,
      )

      const detail = err.response?.data?.detail

      setError(
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((item) => item.msg).join(', ')
            : 'Could not submit your experience. Please try again.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-700">
            Community contributions
          </p>

          <h1 className="text-3xl font-bold text-slate-900">
            Share Your Experience
          </h1>

          <p className="mt-3 leading-7 text-slate-600">
            Help REVA students understand placement experiences, interview
            rounds, and preparation strategies through first-hand knowledge.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"
        >
          {error && (
            <div
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              role="status"
              className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800"
            >
              {success}
            </div>
          )}

          <div>
            <label
              htmlFor="placementDrive"
              className="mb-2 block text-sm font-semibold text-slate-800"
            >
              Placement drive
            </label>

            <select
              id="placementDrive"
              value={placementDriveId}
              onChange={(event) => setPlacementDriveId(event.target.value)}
              disabled={loadingDrives || submitting}
              required
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-800 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
            >
              <option value="">
                {loadingDrives
                  ? 'Loading placement drives...'
                  : drives.length
                    ? 'Select a placement drive'
                    : 'No placement drives available'}
              </option>

              {drives.map((item) => {
                const drive = item.placement_drive
                const company = item.company

                if (!drive?.id) return null

                return (
                  <option key={drive.id} value={drive.id}>
                    {company?.name || 'Company'} —{' '}
                    {drive.title || `Drive #${drive.id}`} (
                    {drive.academic_year || 'Year not specified'})
                  </option>
                )
              })}
            </select>

            {!loadingDrives && drives.length === 0 && !error && (
              <p className="mt-2 text-sm text-slate-500">
                No placement drives were found. Please try again later.
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="experienceType"
              className="mb-2 block text-sm font-semibold text-slate-800"
            >
              Experience type
            </label>

            <select
              id="experienceType"
              value={experienceType}
              onChange={(event) => setExperienceType(event.target.value)}
              disabled={submitting}
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-800 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
            >
              <option value="PLACEMENT_EXPERIENCE">
                Placement experience
              </option>
              <option value="PREPARATION">Preparation strategy</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="content"
              className="mb-2 block text-sm font-semibold text-slate-800"
            >
              Your experience
            </label>

            <textarea
              id="content"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              disabled={submitting}
              required
              minLength={10}
              maxLength={10000}
              rows={8}
              placeholder="Describe the placement process, interview rounds, questions you remember, preparation resources, or lessons you learned. Share only information you are comfortable making available to other students."
              className="w-full resize-y rounded-lg border border-slate-300 px-4 py-3 leading-7 text-slate-800 outline-none placeholder:text-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
            />

            <p className="mt-2 text-right text-xs text-slate-500">
              {content.length}/10000 characters
            </p>
          </div>

          <div className="rounded-lg bg-blue-50 p-4 text-sm leading-6 text-blue-900">
            <strong>What happens next?</strong>
            <p className="mt-1">
              Your submission enters pending review. It becomes part of the
              verified placement knowledge base only after the appropriate
              review and verification process.
            </p>
          </div>

          <button
            type="submit"
            disabled={submitting || loadingDrives || drives.length === 0}
            className="w-full rounded-lg bg-blue-700 px-5 py-3 font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
          >
            {submitting ? 'Submitting...' : 'Submit experience'}
          </button>
        </form>
      </div>
    </main>
  )
}
