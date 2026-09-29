export type Gender = "male" | "female"

export type LeaveType = "CL" | "SL" | "EL" | "PL" | "ML" | "LWP"

export type RequestStatus =
  | "pending_manager"
  | "approved"
  | "rejected_by_agent"
  | "rejected_by_manager"

export const LEAVE_TYPE_LABELS: Record<LeaveType, string> = {
  CL: "Casual Leave",
  SL: "Sick Leave",
  EL: "Earned Leave",
  PL: "Paternal Leave",
  ML: "Maternity Leave",
  LWP: "Leave Without Pay",
}

export interface Employee {
  id: number
  name: string
  email: string
  username: string
  title: string
  gender: Gender
  date_of_joining: string
  is_confirmed: boolean
  manager_name: string
  manager_email: string
}

export interface HRUser {
  id: number
  name: string
  email: string
  username: string
  title: string
}

export interface EmployeeTokenResponse {
  token: string
  employee: Employee
}

export interface HRTokenResponse {
  token: string
  hr_user: HRUser
}

export interface LeaveBalance {
  leave_type: LeaveType
  entitlement: number | null
  used: number
  pending: number
  available: number | null
}

export interface LeaveRequestCreate {
  employee_id: number
  leave_type: LeaveType
  start_date: string
  end_date: string
  is_half_day: boolean
  reason: string
  medical_certificate_confirmed: boolean
  child_dob?: string | null
}

export interface LeaveRequestOut {
  id: number
  employee_id: number
  employee_name: string
  leave_type: LeaveType
  start_date: string
  end_date: string
  is_half_day: boolean
  reason: string
  submitted_at: string
  status: RequestStatus
  requested_days: number
  eligible: boolean | null
  agent_trace: string[]
  eligibility_reasons: string[]
  policy_citations: string[]
  needs_senior_approval: boolean
  filled_application_text: string | null
  decision_comment: string | null
  decided_at: string | null
}

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  created_at: string
  submitted_request?: LeaveRequestOut | null
}

export interface ChatSendResponse {
  reply: string
  draft_slots: Record<string, unknown>
  submitted_request?: LeaveRequestOut | null
}
