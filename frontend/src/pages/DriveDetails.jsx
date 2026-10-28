
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'

function DriveDetails() {
  const { driveId } = useParams()

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    const fetchIntelligence = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await api.get(
          `/placement-drives/${driveId}/intelligence`
        )

        if (!cancelled) {
          setData(response.data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              'Unable to load placement intelligence.'
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchIntelligence()

    return () => {
      cancelled = true
    }
  }, [driveId])

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-12">
        <div className="mx-auto max-w-6xl">
          <p className="text-gray-600">
            Loading placement information...
          </p>
        </div>
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-12">
        <div className="mx-auto max-w-6xl">
          <p className="text-red-600">
            {error || 'Placement information is unavailable.'}
          </p>
        </div>
      </main>
    )
  }

  const company = data.company || {}
  const drive = data.placement_drive || {}
  const eligibility = data.eligibility
  const selectionRounds = data.selection_rounds || []
  const experiences = data.verified_experiences || []
  const claims = data.verified_claims || []

  const isDemo =
    company.name?.toLowerCase() === 'test company' ||
    drive.title?.toLowerCase().includes('test')

  const testExperiences = experiences.filter((experience) =>
    /fictional test content|created to test|sample placement experience/i.test(
      experience.content || ''
    )
  )

  const approvedExperiences = experiences.filter(
    (experience) => !testExperiences.includes(experience)
  )

  // Remove only exact duplicate claim text. Keep distinct claims separate.
  const uniqueClaims = [
    ...new Map(
      claims.map((claim) => [
        (claim.claim_text || '').trim().toLowerCase(),
        claim,
      ])
    ).values(),
  ]

  return (
    <main className="min-h-screen bg-gray-50">
      <section className="mx-auto max-w-6xl px-6 py-12">
        {/* Demo warning */}
        {isDemo && (
          <div
            role="alert"
            className="mb-6 rounded-lg border border-amber-300 bg-amber-50 p-4 text-amber-900"
          >
            <p className="font-semibold">
              DEMO DATA — NOT REAL PLACEMENT RECORDS
            </p>
            <p className="mt-1 text-sm leading-6">
              This company and placement drive are used for application
              testing. The information below must not be interpreted as
              an actual recruitment process or verified real-world outcome.
            </p>
          </div>
        )}

        {/* Company and drive */}
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-blue-700">
            {company.industry || 'Industry not specified'}
          </p>

          <h1 className="mt-2 text-3xl font-bold text-gray-900">
            {company.name || 'Company'}
          </h1>

          <p className="mt-2 text-gray-600">
            {drive.title || 'Placement Drive'}
          </p>

          <p className="mt-4 text-sm text-gray-500">
            Academic Year: {drive.academic_year || 'Not specified'}
          </p>

          {company.description && (
            <p className="mt-4 leading-7 text-gray-600">
              {company.description}
            </p>
          )}
        </section>

        {/* Eligibility */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900">
            Eligibility
          </h2>

          {eligibility ? (
            <div className="mt-3 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-gray-500">Minimum CGPA</p>
                  <p className="mt-1 font-semibold text-gray-900">
                    {eligibility.minimum_cgpa ?? 'Not specified'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-500">
                    Eligible Branches
                  </p>
                  <p className="mt-1 font-semibold text-gray-900">
                    {eligibility.eligible_branches || 'Not specified'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-500">Graduation Year</p>
                  <p className="mt-1 font-semibold text-gray-900">
                    {eligibility.graduation_year ?? 'Not specified'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-500">Backlogs Allowed</p>
                  <p className="mt-1 font-semibold text-gray-900">
                    {eligibility.backlog_allowed == null
                      ? 'Not specified'
                      : eligibility.backlog_allowed
                        ? 'Yes'
                        : 'No'}
                  </p>
                </div>
              </div>

              {eligibility.other_criteria && (
                <div className="mt-5 border-t border-gray-100 pt-4">
                  <p className="text-sm text-gray-500">
                    Other criteria
                  </p>
                  <p className="mt-1 leading-6 text-gray-700">
                    {eligibility.other_criteria}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="mt-3 text-gray-600">
              Eligibility information is not available.
            </p>
          )}
        </section>

        {/* Selection rounds */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900">
            Selection Process
          </h2>

          <div className="mt-3 space-y-3">
            {selectionRounds.length > 0 ? (
              selectionRounds.map((round) => (
                <article
                  key={round.id}
                  className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                >
                  <p className="text-sm font-medium text-blue-700">
                    Round {round.round_number}
                  </p>

                  <h3 className="mt-1 font-semibold text-gray-900">
                    {round.round_type}
                  </h3>

                  {round.description && (
                    <p className="mt-2 leading-6 text-gray-600">
                      {round.description}
                    </p>
                  )}
                </article>
              ))
            ) : (
              <p className="text-gray-600">
                Selection round information is not available.
              </p>
            )}
          </div>
        </section>

        {/* Approved experiences */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900">
            Approved Student Experiences
          </h2>

          {isDemo && (
            <p className="mt-2 text-sm text-amber-800">
              These records belong to a test drive, not confirmed real-world
              placement experiences.
            </p>
          )}

          <div className="mt-3 space-y-4">
            {approvedExperiences.length > 0 ? (
              approvedExperiences.map((experience) => (
                <article
                  key={experience.id}
                  className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                >
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-700">
                      {experience.contributor_type}
                    </span>

                    <span className="text-sm text-gray-500">
                      {experience.experience_type}
                    </span>
                  </div>

                  <p className="mt-4 whitespace-pre-line leading-7 text-gray-700">
                    {experience.content}
                  </p>
                </article>
              ))
            ) : (
              <p className="rounded-lg border border-gray-200 bg-white p-5 text-gray-600">
                No non-test experiences are available.
              </p>
            )}
          </div>
        </section>

        {/* Fictional test experiences */}
        {testExperiences.length > 0 && (
          <section className="mt-8">
            <h2 className="text-xl font-semibold text-gray-900">
              Test Experiences
            </h2>

            <p className="mt-2 text-sm text-amber-800">
              Fictional records shown for development and testing only.
            </p>

            <div className="mt-3 space-y-4">
              {testExperiences.map((experience) => (
                <article
                  key={experience.id}
                  className="rounded-xl border border-amber-200 bg-amber-50 p-5"
                >
                  <p className="text-xs font-bold tracking-wide text-amber-900">
                    FICTIONAL TEST DATA
                  </p>

                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-gray-700">
                      {experience.contributor_type}
                    </span>

                    <span className="text-sm text-gray-600">
                      {experience.experience_type}
                    </span>
                  </div>

                  <p className="mt-3 whitespace-pre-line leading-7 text-gray-700">
                    {experience.content}
                  </p>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* Verified insights */}
        <section className="mt-8 pb-12">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Verified Insights
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Individual claims with their supporting evidence.
              </p>
            </div>

            <span className="w-fit rounded-full bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
              {uniqueClaims.length}{' '}
              {uniqueClaims.length === 1 ? 'insight' : 'insights'}
            </span>
          </div>

          {isDemo && (
            <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm leading-6 text-amber-800">
              These insights come from test records and are not confirmed
              real-world placement findings.
            </p>
          )}

          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            {uniqueClaims.length > 0 ? (
              uniqueClaims.map((claim, index) => (
                <article
                  key={claim.id}
                  className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:border-blue-200 hover:shadow-md"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                      {claim.claim_type || 'Verified claim'}
                    </span>

                    <span className="text-xs text-gray-400">
                      Insight {index + 1}
                    </span>
                  </div>

                  <h3 className="mt-4 font-semibold leading-6 text-gray-900">
                    {claim.claim_text}
                  </h3>

                  {claim.evidence_text && (
                    <div className="mt-4 flex-1 rounded-lg bg-gray-50 p-3">
                      <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Supporting evidence
                      </p>

                      <blockquote className="mt-2 border-l-2 border-blue-300 pl-3 text-sm leading-6 text-gray-600">
                        “{claim.evidence_text}”
                      </blockquote>
                    </div>
                  )}
                </article>
              ))
            ) : (
              <p className="text-gray-600">
                No verified insights are available yet.
              </p>
            )}
          </div>
        </section>
      </section>
    </main>
  )
}

export default DriveDetails

