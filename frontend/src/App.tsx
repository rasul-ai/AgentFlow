import { BrowserRouter, Route, Routes } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import { RequireEmployee, RequireHR } from "./components/ProtectedRoute"
import LandingPage from "./pages/LandingPage"
import EmployeeLogin from "./pages/EmployeeLogin"
import HRLogin from "./pages/HRLogin"
import EmployeePortal from "./pages/EmployeePortal"
import HRDashboard from "./pages/HRDashboard"

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login/employee" element={<EmployeeLogin />} />
          <Route path="/login/hr" element={<HRLogin />} />
          <Route
            path="/portal"
            element={
              <RequireEmployee>
                <EmployeePortal />
              </RequireEmployee>
            }
          />
          <Route
            path="/hr"
            element={
              <RequireHR>
                <HRDashboard />
              </RequireHR>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
