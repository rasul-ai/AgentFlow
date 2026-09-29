import type { LeaveRequestOut } from "../types"
import AgentTraceTimeline from "./AgentTraceTimeline"
import StatusBadge from "./StatusBadge"

export default function RequestResultPanel({ request }: { request: LeaveRequestOut }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Agent pipeline result</h3>
        <StatusBadge status={request.status} />
      </div>

      <AgentTraceTimeline steps={request.agent_trace} />

      <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-700 dark:bg-slate-800/60 dark:text-slate-300">
        {request.eligibility_reasons[0]}
      </div>

      {request.policy_citations.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {request.policy_citations.map((c) => (
            <span
              key={c}
              className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 dark:bg-indigo-400/10 dark:text-indigo-300"
            >
              {c}
            </span>
          ))}
        </div>
      )}

      {request.needs_senior_approval && (
        <div className="mt-3 rounded-lg bg-amber-50 p-3 text-xs font-medium text-amber-800 dark:bg-amber-400/10 dark:text-amber-400">
          This request needs additional approval from senior management, beyond the line manager.
        </div>
      )}

      {request.filled_application_text && (
        <div className="mt-4">
          <p className="mb-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
            Application sent to {request.status === "pending_manager" ? "manager" : "HR"}
          </p>
          <pre className="whitespace-pre-wrap rounded-lg border border-slate-200 bg-white p-3 font-sans text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
            {request.filled_application_text}
          </pre>
        </div>
      )}
    </div>
  )
}
