import { useEffect, useState } from "react"
import { decideRequest, getAllHRRequests, getHRQueue } from "../api/client"
import type { LeaveRequestOut } from "../types"
import { LEAVE_TYPE_LABELS } from "../types"
import StatusBadge from "../components/StatusBadge"
import AgentTraceTimeline from "../components/AgentTraceTimeline"
import PortalNav from "../components/PortalNav"
import { useAuth } from "../context/AuthContext"

export default function HRDashboard() {
  const { hrUser, hrToken, logoutHR } = useAuth()
  const [queue, setQueue] = useState<LeaveRequestOut[]>([])
  const [history, setHistory] = useState<LeaveRequestOut[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [comment, setComment] = useState("")
  const [deciding, setDeciding] = useState(false)

  function refresh() {
    if (!hrToken) return
    getHRQueue(hrToken).then((q) => {
      setQueue(q)
      setSelectedId((prev) => prev ?? q[0]?.id ?? null)
    })
    getAllHRRequests(hrToken).then(setHistory)
  }

  useEffect(refresh, [hrToken])

  const selected = queue.find((r) => r.id === selectedId)

  async function handleDecision(approve: boolean) {
    if (!selected || !hrToken) return
    setDeciding(true)
    try {
      await decideRequest(hrToken, selected.id, approve, comment || undefined)
      setComment("")
      setSelectedId(null)
      refresh()
    } finally {
      setDeciding(false)
    }
  }

  if (!hrUser || !hrToken) return null

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <PortalNav badge="HR" userName={hrUser.name} userSubtitle={hrUser.title} onLogout={logoutHR} />

      <main className="mx-auto max-w-6xl space-y-8 px-6 py-8">
        <div>
          <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">HR Dashboard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Applications that passed the eligibility agent and are awaiting manager decision
          </p>
        </div>

        <section className="grid grid-cols-1 gap-6 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">
              Pending queue ({queue.length})
            </h2>
            <div className="space-y-2">
              {queue.map((r) => (
                <button
                  key={r.id}
                  onClick={() => setSelectedId(r.id)}
                  className={`block w-full rounded-xl border p-3 text-left transition ${
                    selectedId === r.id
                      ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-400/10"
                      : "border-slate-200 bg-white hover:border-slate-300 dark:border-slate-800 dark:bg-slate-900"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                      {r.employee_name}
                    </span>
                    {r.needs_senior_approval && (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-800 dark:bg-amber-400/10 dark:text-amber-400">
                        Senior approval
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {LEAVE_TYPE_LABELS[r.leave_type]} · {r.start_date} → {r.end_date} · {r.requested_days} day(s)
                  </p>
                </button>
              ))}
              {queue.length === 0 && (
                <p className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-400 dark:border-slate-700">
                  Nothing pending right now.
                </p>
              )}
            </div>
          </div>

          <div className="lg:col-span-3">
            {selected ? (
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                      {selected.employee_name} — {LEAVE_TYPE_LABELS[selected.leave_type]}
                    </h3>
                    <p className="text-xs text-slate-400">
                      {selected.start_date} → {selected.end_date} ({selected.requested_days} day(s))
                    </p>
                  </div>
                  <StatusBadge status={selected.status} />
                </div>

                <p className="mb-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-800/60 dark:text-slate-300">
                  <span className="font-medium">Employee's stated reason: </span>
                  {selected.reason}
                </p>

                <AgentTraceTimeline steps={selected.agent_trace} />

                {selected.filled_application_text && (
                  <div className="mt-4">
                    <p className="mb-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
                      Application drafted by the Application Filler agent
                    </p>
                    <pre className="whitespace-pre-wrap rounded-lg border border-slate-200 bg-white p-3 font-sans text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300">
                      {selected.filled_application_text}
                    </pre>
                  </div>
                )}

                <div className="mt-4">
                  <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
                    Decision comment (optional)
                  </label>
                  <textarea
                    className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
                    rows={2}
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                  />
                </div>

                <div className="mt-4 flex gap-3">
                  <button
                    onClick={() => handleDecision(true)}
                    disabled={deciding}
                    className="flex-1 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleDecision(false)}
                    disabled={deciding}
                    className="flex-1 rounded-lg bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-rose-500 disabled:opacity-60"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-400 dark:border-slate-700">
                Select a request from the queue to review it.
              </div>
            )}
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">All requests</h2>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-xs text-slate-400 dark:border-slate-800">
                <tr>
                  <th className="px-4 py-2 font-medium">Employee</th>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Dates</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Decision comment</th>
                </tr>
              </thead>
              <tbody>
                {history.map((r) => (
                  <tr key={r.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800/60">
                    <td className="px-4 py-2.5">{r.employee_name}</td>
                    <td className="px-4 py-2.5">{LEAVE_TYPE_LABELS[r.leave_type]}</td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">
                      {r.start_date} → {r.end_date}
                    </td>
                    <td className="px-4 py-2.5">
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{r.decision_comment ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  )
}
