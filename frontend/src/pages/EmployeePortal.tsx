import { useEffect, useState } from "react"
import { getEmployeeBalances, listLeaveRequests } from "../api/client"
import type { LeaveBalance, LeaveRequestOut } from "../types"
import { LEAVE_TYPE_LABELS } from "../types"
import LeaveBalanceCard from "../components/LeaveBalanceCard"
import StatusBadge from "../components/StatusBadge"
import FloatingChat from "../components/FloatingChat"
import PortalNav from "../components/PortalNav"
import { useAuth } from "../context/AuthContext"

function initials(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()
}

export default function EmployeePortal() {
  const { employee, employeeToken, logoutEmployee } = useAuth()
  const [balances, setBalances] = useState<LeaveBalance[]>([])
  const [history, setHistory] = useState<LeaveRequestOut[]>([])

  function refresh() {
    if (!employee || !employeeToken) return
    getEmployeeBalances(employeeToken, employee.id).then(setBalances)
    listLeaveRequests(employeeToken).then(setHistory)
  }

  useEffect(refresh, [employee, employeeToken])

  if (!employee || !employeeToken) return null

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <PortalNav userName={employee.name} userSubtitle={employee.title} onLogout={logoutEmployee} />

      <main className="mx-auto max-w-6xl space-y-8 px-6 py-8">
        <section className="flex flex-wrap items-center gap-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-600 text-xl font-semibold text-white">
            {initials(employee.name)}
          </div>
          <div className="flex-1">
            <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{employee.name}</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">{employee.title}</p>
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
              <span>Joined {employee.date_of_joining}</span>
              <span>Manager: {employee.manager_name}</span>
              <span>{employee.is_confirmed ? "Confirmed employee" : "On probation"}</span>
              <span>{employee.email}</span>
            </div>
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">Leave balances</h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {balances.map((b) => (
              <LeaveBalanceCard key={b.leave_type} balance={b} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">Your request history</h2>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-xs text-slate-400 dark:border-slate-800">
                <tr>
                  <th className="px-4 py-2 font-medium">Type</th>
                  <th className="px-4 py-2 font-medium">Dates</th>
                  <th className="px-4 py-2 font-medium">Days</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Submitted</th>
                </tr>
              </thead>
              <tbody>
                {history.map((r) => (
                  <tr key={r.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800/60">
                    <td className="px-4 py-2.5">{LEAVE_TYPE_LABELS[r.leave_type]}</td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">
                      {r.start_date} → {r.end_date}
                    </td>
                    <td className="px-4 py-2.5">{r.requested_days}</td>
                    <td className="px-4 py-2.5">
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">
                      {new Date(r.submitted_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
                {history.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-6 text-center text-slate-400">
                      No requests yet — try the HR Assistant chat in the bottom-right corner.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <FloatingChat employeeId={employee.id} token={employeeToken} onRequestSubmitted={refresh} />
    </div>
  )
}
