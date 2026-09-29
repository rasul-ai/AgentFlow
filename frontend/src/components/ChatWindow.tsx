import { useEffect, useRef, useState } from "react"
import { getChatMessages, resetChatDraft, sendChatMessage } from "../api/client"
import type { ChatMessage } from "../types"
import RequestResultPanel from "./RequestResultPanel"

const STARTER_PROMPTS = [
  "How many casual leave days do I have left?",
  "Suggest a good long weekend using my Earned Leave",
  "I want to apply for 2 days of sick leave",
  "What's the notice period for Earned Leave?",
]

interface Props {
  employeeId: number
  token: string
  onRequestSubmitted: () => void
  onClose?: () => void
}

export default function ChatWindow({ employeeId, token, onRequestSubmitted, onClose }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setLoadingHistory(true)
    getChatMessages(token, employeeId)
      .then(setMessages)
      .finally(() => setLoadingHistory(false))
  }, [employeeId, token])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, sending])

  async function send(content: string) {
    const text = content.trim()
    if (!text || sending) return
    setInput("")
    setMessages((prev) => [...prev, { role: "user", content: text, created_at: new Date().toISOString() }])
    setSending(true)
    try {
      const res = await sendChatMessage(token, employeeId, text)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.reply,
          created_at: new Date().toISOString(),
          submitted_request: res.submitted_request,
        },
      ])
      if (res.submitted_request) onRequestSubmitted()
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong reaching the HR assistant. Please try again.",
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setSending(false)
    }
  }

  async function handleStartOver() {
    await resetChatDraft(token, employeeId)
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: "No problem — I've cleared the current draft. What would you like to do?",
        created_at: new Date().toISOString(),
      },
    ])
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  return (
    <div className="flex h-[32rem] flex-col rounded-xl border border-slate-200 bg-white shadow-xl dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
            19
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">HR Assistant</p>
            <p className="text-xs text-slate-400">Ask, get suggestions, or apply</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleStartOver}
            className="rounded-lg px-2.5 py-1 text-xs font-medium text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            Start over
          </button>
          {onClose && (
            <button
              onClick={onClose}
              aria-label="Close chat"
              className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
            >
              <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
                <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
              </svg>
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
        {loadingHistory && <p className="text-center text-sm text-slate-400">Loading conversation…</p>}

        {!loadingHistory && messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <p className="text-sm text-slate-400">Try asking:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {STARTER_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p)}
                  className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 transition hover:border-indigo-400 hover:text-indigo-600 dark:border-slate-700 dark:text-slate-300"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] ${m.role === "user" ? "" : "flex gap-2"}`}>
              {m.role === "assistant" && (
                <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
                  19
                </div>
              )}
              <div>
                <div
                  className={`whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${
                    m.role === "user"
                      ? "rounded-br-sm bg-indigo-600 text-white"
                      : "rounded-bl-sm bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200"
                  }`}
                >
                  {m.content}
                </div>
                {m.submitted_request && (
                  <div className="mt-2 w-[26rem] max-w-full">
                    <RequestResultPanel request={m.submitted_request} />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex justify-start gap-2">
            <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
              19
            </div>
            <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-slate-100 px-4 py-3 dark:bg-slate-800">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex items-end gap-2 border-t border-slate-200 p-3 dark:border-slate-800">
        <textarea
          className="max-h-24 flex-1 resize-none rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          rows={1}
          placeholder="Message the HR assistant…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          onClick={() => send(input)}
          disabled={sending || !input.trim()}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Send
        </button>
      </div>
    </div>
  )
}
