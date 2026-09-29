import type { LeaveBalance } from "../types"
import { LEAVE_TYPE_LABELS } from "../types"

export default function LeaveBalanceCard({ balance }: { balance: LeaveBalance }) {
  const isUnlimited = balance.available === null
  const pct =
    !isUnlimited && balance.entitlement
      ? Math.max(0, Math.min(100, (balance.available! / balance.entitlement) * 100))
      : 100

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
          {LEAVE_TYPE_LABELS[balance.leave_type]}
        </span>
        <span className="text-xs font-medium text-slate-400">{balance.leave_type}</span>
      </div>

      {isUnlimited ? (
        <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">As required, subject to approval</p>
      ) : (
        <>
          <div className="mt-3 flex items-baseline gap-1">
            <span className="text-2xl font-semibold text-slate-900 dark:text-slate-100">{balance.available}</span>
            <span className="text-sm text-slate-400">/ {balance.entitlement} days available</span>
          </div>
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div className="h-full rounded-full bg-indigo-500" style={{ width: `${pct}%` }} />
          </div>
          <div className="mt-2 flex justify-between text-xs text-slate-400">
            <span>Used: {balance.used}</span>
            {balance.pending > 0 && <span>Pending: {balance.pending}</span>}
          </div>
        </>
      )}
    </div>
  )
}
