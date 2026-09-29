import type { RequestStatus } from "../types"

const STYLES: Record<RequestStatus, string> = {
  pending_manager: "bg-amber-100 text-amber-800 dark:bg-amber-400/10 dark:text-amber-400",
  approved: "bg-emerald-100 text-emerald-800 dark:bg-emerald-400/10 dark:text-emerald-400",
  rejected_by_agent: "bg-rose-100 text-rose-800 dark:bg-rose-400/10 dark:text-rose-400",
  rejected_by_manager: "bg-rose-100 text-rose-800 dark:bg-rose-400/10 dark:text-rose-400",
}

const LABELS: Record<RequestStatus, string> = {
  pending_manager: "Pending Manager",
  approved: "Approved",
  rejected_by_agent: "Rejected by Agent",
  rejected_by_manager: "Rejected by Manager",
}

export default function StatusBadge({ status }: { status: RequestStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${STYLES[status]}`}>
      {LABELS[status]}
    </span>
  )
}
