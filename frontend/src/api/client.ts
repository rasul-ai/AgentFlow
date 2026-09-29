import axios from "axios"
import type {
  ChatMessage,
  ChatSendResponse,
  Employee,
  EmployeeTokenResponse,
  HRTokenResponse,
  HRUser,
  LeaveBalance,
  LeaveRequestCreate,
  LeaveRequestOut,
} from "../types"

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export const api = axios.create({ baseURL })

function auth(token: string) {
  return { headers: { Authorization: `Bearer ${token}` } }
}

// --- Auth ---

export async function employeeLogin(username: string, password: string): Promise<EmployeeTokenResponse> {
  const { data } = await api.post<EmployeeTokenResponse>("/auth/employee/login", { username, password })
  return data
}

export async function employeeMe(token: string): Promise<EmployeeTokenResponse> {
  const { data } = await api.get<EmployeeTokenResponse>("/auth/employee/me", auth(token))
  return data
}

export async function hrLogin(username: string, password: string): Promise<HRTokenResponse> {
  const { data } = await api.post<HRTokenResponse>("/auth/hr/login", { username, password })
  return data
}

export async function hrMe(token: string): Promise<HRTokenResponse> {
  const { data } = await api.get<HRTokenResponse>("/auth/hr/me", auth(token))
  return data
}

// --- Employee-scoped ---

export async function getEmployeeBalances(token: string, employeeId: number): Promise<LeaveBalance[]> {
  const { data } = await api.get<LeaveBalance[]>(`/employees/${employeeId}/balances`, auth(token))
  return data
}

export async function listLeaveRequests(token: string): Promise<LeaveRequestOut[]> {
  const { data } = await api.get<LeaveRequestOut[]>("/leave/requests", auth(token))
  return data
}

export async function createLeaveRequest(token: string, payload: LeaveRequestCreate): Promise<LeaveRequestOut> {
  const { data } = await api.post<LeaveRequestOut>("/leave/requests", payload, auth(token))
  return data
}

export async function getChatMessages(token: string, employeeId: number): Promise<ChatMessage[]> {
  const { data } = await api.get<ChatMessage[]>(`/chat/${employeeId}/messages`, auth(token))
  return data
}

export async function sendChatMessage(token: string, employeeId: number, content: string): Promise<ChatSendResponse> {
  const { data } = await api.post<ChatSendResponse>(`/chat/${employeeId}/messages`, { content }, auth(token))
  return data
}

export async function resetChatDraft(token: string, employeeId: number): Promise<void> {
  await api.post(`/chat/${employeeId}/reset`, {}, auth(token))
}

// --- HR-scoped ---

export async function listEmployees(token: string): Promise<Employee[]> {
  const { data } = await api.get<Employee[]>("/employees", auth(token))
  return data
}

export async function getHRQueue(token: string): Promise<LeaveRequestOut[]> {
  const { data } = await api.get<LeaveRequestOut[]>("/hr/queue", auth(token))
  return data
}

export async function getAllHRRequests(token: string): Promise<LeaveRequestOut[]> {
  const { data } = await api.get<LeaveRequestOut[]>("/hr/requests", auth(token))
  return data
}

export async function decideRequest(
  token: string,
  requestId: number,
  approve: boolean,
  comment?: string,
): Promise<LeaveRequestOut> {
  const { data } = await api.post<LeaveRequestOut>(`/hr/requests/${requestId}/decision`, { approve, comment }, auth(token))
  return data
}

export type { HRUser }
