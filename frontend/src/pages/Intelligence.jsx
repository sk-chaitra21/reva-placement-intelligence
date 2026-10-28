
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import Navbar from '../components/Navbar'
import api from '../services/api'

export default function Intelligence() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [isDemoData, setIsDemoData] = useState(false)
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const askQuestion = async (event) => {
    event?.preventDefault()

    if (!question.trim() || loading) return

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])
    setNotice('')
    setIsDemoData(false)

    try {
      const response = await api.post('/intelligence/query', {
        question: question.trim(),
        limit: 3,
      })

      const data = response.data

      setAnswer(data.answer || '')
      setSources(Array.isArray(data.sources) ? data.sources : [])
      setIsDemoData(Boolean(data.is_demo_data))
      setNotice(data.notice || '')
    } catch (err) {
      console.error('Intelligence query failed:', err)

      setError(
        err.response?.data?.detail ||
          'Unable to retrieve placement intelligence right now. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault()
      askQuestion()
    }
  }

  const formatSimilarity = (value) => {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      return null
    }

    return `${(value * 100).toFixed(1)}%`
  }

  const cleanAnswer = isDemoData
    ? answer.replace(/^DEMO DATA ONLY:[^\n]*(?:\n\n)?/, '')
    : answer

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                className="h-6 w-6"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 3v2m0 14v2M3 12h2m14 0h2M5.64 5.64l1.42 1.42m9.88 9.88 1.42 1.42m0-12.72-1.42 1.42m-9.88 9.88-1.42 1.42"
                />
                <circle cx="12" cy="12" r="5" />
              </svg>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">
                REVA Placement Intelligence
              </p>
              <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
                Ask about placements
              </h1>
            </div>
          </div>

          <p className="max-w-3xl leading-7 text-slate-600">
            Explore placement knowledge using available claims and experience
            records. Answers depend on the evidence available.
          </p>
        </header>

        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
          <form onSubmit={askQuestion}>
            <label
              htmlFor="placement-question"
              className="mb-2 block text-sm font-semibold text-slate-800"
            >
              Your question
            </label>

            <textarea
              id="placement-question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Example: What preparation strategies are mentioned in the available placement knowledge?"
              rows={4}
              className="w-full resize-y rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm leading-6 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              disabled={loading}
            />

            <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs text-slate-500">
                Press Ctrl + Enter to ask
              </p>

              <button
                type="submit"
                disabled={!question.trim() || loading}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading && (
                  <svg
                    className="h-4 w-4 animate-spin"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden="true"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                    />
                  </svg>
                )}
                {loading ? 'Finding an answer...' : 'Ask question'}
              </button>
            </div>
          </form>
        </section>

        {error && (
          <div
            role="alert"
            className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-800"
          >
            <p className="font-semibold">Something went wrong</p>
            <p className="mt-1">{error}</p>
          </div>
        )}

        {loading && (
          <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-5">
            <p className="text-sm font-medium text-blue-900">
              Searching available evidence and generating an answer...
            </p>
            <p className="mt-1 text-sm text-blue-700">
              This may take a few moments.
            </p>
          </div>
        )}

        {!loading && answer && (
          <div className="mt-8 space-y-6">
            {isDemoData && (
              <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 sm:p-5">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 text-amber-700">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      className="h-5 w-5"
                      aria-hidden="true"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 9v4m0 4h.01M10.3 3.86 1.82 18.5A2 2 0 003.55 21h16.9a2 2 0 001.73-2.5L13.7 3.86a2 2 0 00-3.4 0z"
                      />
                    </svg>
                  </div>

                  <div>
                    <h2 className="font-bold text-amber-950">
                      Demo data — not real placement records
                    </h2>
                    <p className="mt-1 text-sm leading-6 text-amber-900">
                      {notice ||
                        'This answer uses fictional or test placement records. It does not represent verified real-world REVA placement outcomes.'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-5 py-4 sm:px-7">
                <h2 className="text-lg font-bold text-slate-900">
                  Answer
                </h2>

                <span
                  className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                    isDemoData
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {isDemoData ? 'Demo answer' : 'Evidence-based answer'}
                </span>
              </div>

              <div className="px-5 py-6 sm:px-7">
                <div className="markdown-answer text-sm leading-7 text-slate-700">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => (
                        <h1 className="mb-4 mt-6 text-2xl font-bold text-slate-900 first:mt-0">
                          {children}
                        </h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="mb-3 mt-6 text-xl font-bold text-slate-900 first:mt-0">
                          {children}
                        </h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="mb-2 mt-5 text-base font-bold text-slate-900">
                          {children}
                        </h3>
                      ),
                      p: ({ children }) => (
                        <p className="mb-4 last:mb-0">{children}</p>
                      ),
                      ul: ({ children }) => (
                        <ul className="mb-4 list-disc space-y-2 pl-6">
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="mb-4 list-decimal space-y-2 pl-6">
                          {children}
                        </ol>
                      ),
                      li: ({ children }) => (
                        <li className="pl-1">{children}</li>
                      ),
                      strong: ({ children }) => (
                        <strong className="font-semibold text-slate-900">
                          {children}
                        </strong>
                      ),
                      em: ({ children }) => (
                        <em className="italic">{children}</em>
                      ),
                      blockquote: ({ children }) => (
                        <blockquote className="my-4 border-l-4 border-blue-300 pl-4 text-slate-600">
                          {children}
                        </blockquote>
                      ),
                      code: ({ children }) => (
                        <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-800">
                          {children}
                        </code>
                      ),
                    }}
                  >
                    {cleanAnswer}
                  </ReactMarkdown>
                </div>
              </div>
            </section>

            <section>
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">
                    {isDemoData ? 'Demo sources used' : 'Evidence used'}
                  </h2>
                  <p className="mt-1 text-sm text-slate-600">
                    These records contributed to the generated answer.
                  </p>
                </div>

                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  {sources.length} {sources.length === 1 ? 'source' : 'sources'}
                </span>
              </div>

              {sources.length === 0 ? (
                <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-600">
                  No supporting source records were returned for this answer.
                </div>
              ) : (
                <div className="space-y-4">
                  {sources.map((source, index) => {
                    const metadata = source.source || {}
                    const similarity = formatSimilarity(source.similarity)

                    return (
                      <article
                        key={source.claim_id ?? `${index}-${source.claim_text}`}
                        className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-sm font-bold text-blue-800">
                            {index + 1}
                          </div>

                          <div className="min-w-0 flex-1">
                            <h3 className="break-words font-semibold leading-6 text-slate-900">
                              {source.claim_text || 'Claim text unavailable'}
                            </h3>

                            {source.evidence_text && (
                              <div className="mt-4 rounded-xl bg-slate-50 p-4">
                                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                                  Supporting evidence
                                </p>
                                <p className="whitespace-pre-line break-words text-sm leading-6 text-slate-700">
                                  {source.evidence_text}
                                </p>
                              </div>
                            )}

                            <div className="mt-4 flex flex-wrap items-center gap-2">
                              {source.claim_type && (
                                <span className="inline-flex max-w-full break-words rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-800">
                                  {source.claim_type}
                                </span>
                              )}

                              {metadata.contributor_type && (
                                <span className="inline-flex max-w-full break-words rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                                  {metadata.contributor_type}
                                </span>
                              )}

                              {metadata.company && (
                                <span className="inline-flex max-w-full break-words rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                                  {metadata.company}
                                </span>
                              )}

                              {metadata.academic_year && (
                                <span className="inline-flex max-w-full break-words rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                                  {metadata.academic_year}
                                </span>
                              )}
                            </div>

                            {similarity !== null && (
                              <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                                <span className="font-medium text-slate-600">
                                  Retrieval similarity:
                                </span>
                                <span className="rounded-md bg-slate-100 px-2 py-1 font-semibold tabular-nums text-slate-700">
                                  {similarity}
                                </span>
                              </div>
                            )}

                            {(
                              source.is_demo_data ||
                              metadata.data_label?.startsWith('DEMO DATA')
                            ) && (
                              <div className="mt-4">
                                <span className="inline-flex rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-800">
                                  Demo data — not real placement records
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </article>
                    )
                  })}
                </div>
              )}
            </section>
          </div>
        )}

        {!loading && !answer && !error && (
          <section className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-10 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-700">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                className="h-6 w-6"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M8 10h8M8 14h5m-7 7 3.2-3H18a2 2 0 002-2V5a2 2 0 00-2-2H4a2 2 0 00-2 2v11a2 2 0 002 2h2z"
                />
              </svg>
            </div>
            <h2 className="mt-4 font-semibold text-slate-900">
              Your placement questions start here
            </h2>
            <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-600">
              Ask a question to explore the placement claims and experience
              records currently available in the system. Answers may be limited
              when supporting evidence is unavailable.
            </p>
          </section>
        )}
      </main>
    </div>
  )
}

