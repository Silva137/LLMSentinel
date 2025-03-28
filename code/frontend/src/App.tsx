import { AuthProvider } from './Context/AuthContext.tsx';
import {BrowserRouter, Navigate, Route, Routes} from 'react-router-dom'
import PrivateRoute from "./Components/PrivateRoute.tsx";
import Login from "./Pages/Login/Login.tsx"
import Dashboard from "./Pages/Dashboard.tsx";
import Register from "./Pages/Register/Register.tsx";

function App() {

  return (
      <BrowserRouter>
        <AuthProvider>
          <Routes>
              <Route path="/" element={<Navigate to="/login" />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login />} />

              {/* Protected Routes */}
              <Route element={<PrivateRoute />}>
                  <Route path="/dashboard" element={<Dashboard />} />
              </Route>

          </Routes>
        </AuthProvider>
      </BrowserRouter>
  )
}

export default App
