import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
    </div>
  )
}

export function RequireEmployee({ children }: { children: ReactNode }) {
  const { employee, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!employee) return <Navigate to="/login/employee" replace />
  return <>{children}</>
}

export function RequireHR({ children }: { children: ReactNode }) {
  const { hrUser, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!hrUser) return <Navigate to="/login/hr" replace />
  return <>{children}</>
}
