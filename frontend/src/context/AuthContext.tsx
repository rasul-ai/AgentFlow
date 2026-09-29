import { createContext, useContext, useEffect, useState } from "react"
import type { ReactNode } from "react"
import { employeeLogin, employeeMe, hrLogin, hrMe } from "../api/client"
import type { Employee, HRUser } from "../types"

const EMP_KEY = "code19_employee_token"
const HR_KEY = "code19_hr_token"

interface AuthContextValue {
  employee: Employee | null
  employeeToken: string | null
  loginEmployee: (username: string, password: string) => Promise<void>
  logoutEmployee: () => void

  hrUser: HRUser | null
  hrToken: string | null
  loginHR: (username: string, password: string) => Promise<void>
  logoutHR: () => void

  loading: boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [employee, setEmployee] = useState<Employee | null>(null)
  const [employeeToken, setEmployeeToken] = useState<string | null>(null)
  const [hrUser, setHrUser] = useState<HRUser | null>(null)
  const [hrToken, setHrToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function restore() {
      const storedEmpToken = localStorage.getItem(EMP_KEY)
      if (storedEmpToken) {
        try {
          const res = await employeeMe(storedEmpToken)
          setEmployee(res.employee)
          setEmployeeToken(res.token)
          localStorage.setItem(EMP_KEY, res.token)
        } catch {
          localStorage.removeItem(EMP_KEY)
        }
      }

      const storedHrToken = localStorage.getItem(HR_KEY)
      if (storedHrToken) {
        try {
          const res = await hrMe(storedHrToken)
          setHrUser(res.hr_user)
          setHrToken(res.token)
          localStorage.setItem(HR_KEY, res.token)
        } catch {
          localStorage.removeItem(HR_KEY)
        }
      }
      setLoading(false)
    }
    restore()
  }, [])

  async function loginEmployee(username: string, password: string) {
    const res = await employeeLogin(username, password)
    setEmployee(res.employee)
    setEmployeeToken(res.token)
    localStorage.setItem(EMP_KEY, res.token)
  }

  function logoutEmployee() {
    setEmployee(null)
    setEmployeeToken(null)
    localStorage.removeItem(EMP_KEY)
  }

  async function loginHR(username: string, password: string) {
    const res = await hrLogin(username, password)
    setHrUser(res.hr_user)
    setHrToken(res.token)
    localStorage.setItem(HR_KEY, res.token)
  }

  function logoutHR() {
    setHrUser(null)
    setHrToken(null)
    localStorage.removeItem(HR_KEY)
  }

  return (
    <AuthContext.Provider
      value={{
        employee,
        employeeToken,
        loginEmployee,
        logoutEmployee,
        hrUser,
        hrToken,
        loginHR,
        logoutHR,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
