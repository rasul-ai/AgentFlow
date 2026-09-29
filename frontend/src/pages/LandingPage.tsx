import { Link } from "react-router-dom"

const STATS = [
  { label: "Engineers & designers", value: "120+" },
  { label: "Products shipped", value: "80+" },
  { label: "Years building", value: "8" },
  { label: "Team retention", value: "96%" },
]

const VALUES = [
  {
    title: "Craft",
    body: "We hold our engineering and design work to a standard our clients notice — and our team is proud of.",
  },
  {
    title: "Trust",
    body: "Clear policies, honest communication, and systems (like this one) that do what they say they'll do.",
  },
  {
    title: "Balance",
    body: "Sustainable pace beats heroics. Leave isn't a favor we grant — it's how people do their best work.",
  },
]

const ASSISTANT_FEATURES = [
  "Ask about your leave balance or any policy clause, in plain language",
  "Get holiday-aware suggestions for bridging long weekends",
  "Have your application drafted and routed to your manager automatically",
]

const LEADERSHIP = [
  { name: "Imtiaz Farhan Bin Habib", title: "Director, Business Development" },
  { name: "Farhana Khan", title: "HR Manager" },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <header className="border-b border-slate-200 dark:border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
              19
            </div>
            <span className="text-lg font-semibold text-slate-900 dark:text-slate-100">Code 19</span>
          </div>
          <nav className="hidden items-center gap-8 text-sm font-medium text-slate-600 dark:text-slate-300 md:flex">
            <a href="#about" className="hover:text-slate-900 dark:hover:text-white">
              About
            </a>
            <a href="#assistant" className="hover:text-slate-900 dark:hover:text-white">
              HR Assistant
            </a>
            <a href="#leadership" className="hover:text-slate-900 dark:hover:text-white">
              Leadership
            </a>
            <a href="#contact" className="hover:text-slate-900 dark:hover:text-white">
              Contact
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <Link
              to="/login/hr"
              className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
            >
              HR Login
            </Link>
            <Link
              to="/login/employee"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500"
            >
              Employee Login
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
          <div>
            <span className="inline-block rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 dark:bg-indigo-400/10 dark:text-indigo-300">
              Product engineering, since 2018
            </span>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-slate-900 dark:text-slate-100 sm:text-5xl">
              Software craftsmanship,
              <br />a human-first culture.
            </h1>
            <p className="mt-5 max-w-lg text-base text-slate-600 dark:text-slate-400">
              Code 19 builds and ships digital products for clients across fintech, logistics and healthcare — and
              runs on a leave policy that respects people enough to make it effortless to use.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login/employee"
                className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500"
              >
                Employee Portal
              </Link>
              <Link
                to="/login/hr"
                className="rounded-lg border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-900"
              >
                HR / Manager Portal
              </Link>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
              <div className="mb-3 flex items-center gap-2 border-b border-slate-100 pb-3 dark:border-slate-800">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
                  19
                </div>
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">HR Assistant</span>
              </div>
              <div className="space-y-2">
                <div className="max-w-[80%] rounded-2xl rounded-bl-sm bg-slate-100 px-3 py-2 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                  You have 8 Earned Leave days left. Aug 15 falls on a Saturday this year, so it won't extend your
                  weekend — want me to suggest another stretch?
                </div>
                <div className="ml-auto max-w-[80%] rounded-2xl rounded-br-sm bg-indigo-600 px-3 py-2 text-xs text-white">
                  Yes, book 2 days around Victory Day
                </div>
                <div className="max-w-[80%] rounded-2xl rounded-bl-sm bg-slate-100 px-3 py-2 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                  Dec 16 is a Wednesday — take Dec 14–15 off for a 5-day break. Shall I submit it?
                </div>
              </div>
            </div>
          </div>
        </div>

        <dl className="mt-20 grid grid-cols-2 gap-6 border-y border-slate-200 py-10 dark:border-slate-800 sm:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.label} className="text-center">
              <dt className="text-3xl font-semibold text-slate-900 dark:text-slate-100">{s.value}</dt>
              <dd className="mt-1 text-sm text-slate-500 dark:text-slate-400">{s.label}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="about" className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">What we stand for</h2>
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-3">
          {VALUES.map((v) => (
            <div
              key={v.title}
              className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
            >
              <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">{v.title}</h3>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{v.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="assistant" className="bg-slate-50 py-16 dark:bg-slate-900/40">
        <div className="mx-auto max-w-6xl px-6">
          <div className="grid grid-cols-1 items-center gap-10 lg:grid-cols-2">
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Meet your HR Assistant</h2>
              <p className="mt-3 text-sm text-slate-600 dark:text-slate-400">
                Every employee gets a RAG-grounded assistant that actually knows the Code 19 Leave Policy — not a
                generic chatbot guessing at rules.
              </p>
              <ul className="mt-6 space-y-3">
                {ASSISTANT_FEATURES.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                    <svg viewBox="0 0 20 20" fill="currentColor" className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600">
                      <path
                        fillRule="evenodd"
                        d="M16.7 5.3a1 1 0 010 1.4l-7.5 7.5a1 1 0 01-1.4 0l-3.5-3.5a1 1 0 111.4-1.4l2.8 2.8 6.8-6.8a1 1 0 011.4 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                to="/login/employee"
                className="mt-8 inline-block rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500"
              >
                Try it as an employee
              </Link>
            </div>
            <div className="flex h-64 items-center justify-center rounded-2xl border border-dashed border-slate-300 text-sm text-slate-400 dark:border-slate-700">
              Available as a floating assistant on every page of the Employee Portal
            </div>
          </div>
        </div>
      </section>

      <section id="leadership" className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Leadership</h2>
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
          {LEADERSHIP.map((p) => (
            <div
              key={p.name}
              className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white dark:bg-slate-100 dark:text-slate-900">
                {p.name
                  .split(" ")
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join("")}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{p.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{p.title}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer id="contact" className="border-t border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900/40">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div>
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-xs font-bold text-white">
                  19
                </div>
                <span className="font-semibold text-slate-900 dark:text-slate-100">Code 19</span>
              </div>
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                Level 7, Gulshan Avenue, Dhaka 1212, Bangladesh
              </p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Contact</p>
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">hello@code19.com</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">+880 1700-000000</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Portals</p>
              <div className="mt-3 flex flex-col gap-2 text-sm">
                <Link to="/login/employee" className="text-slate-500 hover:text-indigo-600 dark:text-slate-400">
                  Employee Login
                </Link>
                <Link to="/login/hr" className="text-slate-500 hover:text-indigo-600 dark:text-slate-400">
                  HR / Manager Login
                </Link>
              </div>
            </div>
          </div>
          <p className="mt-10 text-xs text-slate-400">© {new Date().getFullYear()} Code 19. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
