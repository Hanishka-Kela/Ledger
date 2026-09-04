import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext.jsx'
import LoadingState from '../components/LoadingState.jsx'

export default function ProtectedRoute() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <div className="page-center"><LoadingState label="Loading your ledger…" /></div>
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />
  return <Outlet />
}
