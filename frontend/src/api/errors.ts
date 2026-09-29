import axios from "axios"

export function describeLoginError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    if (!err.response) {
      return "Could not reach the server. Check that the backend is running and VITE_API_BASE_URL points to it."
    }
    if (err.response.status === 401) {
      return "Incorrect username or password."
    }
    return `Login failed (${err.response.status}). Please try again.`
  }
  return "Something went wrong. Please try again."
}
