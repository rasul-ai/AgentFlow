export default function AgentTraceTimeline({ steps }: { steps: string[] }) {
  return (
    <ol className="space-y-3">
      {steps.map((step, i) => {
        const [label, ...rest] = step.split(":")
        const detail = rest.join(":").trim()
        return (
          <li key={i} className="flex gap-3">
            <div className="flex flex-col items-center">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-500 text-xs font-semibold text-white">
                {i + 1}
              </span>
              {i < steps.length - 1 && <span className="mt-1 w-px flex-1 bg-slate-200 dark:bg-slate-700" />}
            </div>
            <div className="pb-3">
              <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{label}</p>
              {detail && <p className="text-sm text-slate-500 dark:text-slate-400">{detail}</p>}
            </div>
          </li>
        )
      })}
    </ol>
  )
}
