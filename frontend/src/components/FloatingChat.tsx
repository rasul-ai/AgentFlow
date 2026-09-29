import { useState } from "react"
import ChatWindow from "./ChatWindow"

interface Props {
  employeeId: number
  token: string
  onRequestSubmitted: () => void
}

export default function FloatingChat({ employeeId, token, onRequestSubmitted }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <div
        className={`fixed bottom-24 right-6 z-40 w-[24rem] max-w-[calc(100vw-3rem)] origin-bottom-right transition duration-200 ${
          open ? "scale-100 opacity-100" : "pointer-events-none scale-95 opacity-0"
        }`}
      >
        <ChatWindow
          employeeId={employeeId}
          token={token}
          onRequestSubmitted={onRequestSubmitted}
          onClose={() => setOpen(false)}
        />
      </div>

      <button
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close HR Assistant chat" : "Open HR Assistant chat"}
        className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg transition hover:bg-indigo-500 hover:shadow-xl"
      >
        {open ? (
          <svg viewBox="0 0 20 20" fill="currentColor" className="h-6 w-6">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="currentColor" className="h-7 w-7">
            <path d="M4 4a2 2 0 00-2 2v10a2 2 0 002 2h3v3.5a.75.75 0 001.28.53L12.81 18H20a2 2 0 002-2V6a2 2 0 00-2-2H4z" />
          </svg>
        )}
        {!open && (
          <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-white dark:ring-slate-950" />
        )}
      </button>
    </>
  )
}
