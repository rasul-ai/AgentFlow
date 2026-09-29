import { Link } from "react-router-dom"
import type { ReactNode } from "react"

interface Props {
  badge?: string
  userName: string
  userSubtitle: string
  onLogout: () => void
  children?: ReactNode
}

export default function PortalNav({ badge, userName, userSubtitle, onLogout, children }: Props) {
  return (
    <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
            19
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              Code 19{badge && <span className="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-400">{badge}</span>}
            </p>
            <p className="text-xs text-slate-400">HR Leave Assistant</p>
          </div>
        </Link>

        <div className="flex items-center gap-4">
          {children}
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{userName}</p>
            <p className="text-xs text-slate-400">{userSubtitle}</p>
          </div>
          <Link
            to="/"
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            ← Home
          </Link>
          <button
            onClick={onLogout}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  )
}
