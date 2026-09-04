import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import Alert from '../components/Alert.jsx'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/dashboard" replace />

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(form)
      navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-aside">
        <div className="auth-brand"><span className="brand-mark">L</span><span>Ledger</span></div>
        <div className="auth-message">
          <p className="eyebrow light">Double-entry accounting</p>
          <h1>Clarity for every transaction.</h1>
          <p>A focused workspace for managing accounts, transfers, and journal entries.</p>
        </div>
        <p className="auth-footnote">Simple. Reliable. Balanced.</p>
      </div>
      <main className="auth-main">
        <div className="auth-card">
          <p className="eyebrow">Welcome back</p>
          <h2>Sign in to Ledger</h2>
          <p className="muted">Enter your credentials to continue.</p>
          {location.state?.message && <Alert type="success">{location.state.message}</Alert>}
          <Alert>{error}</Alert>
          <form onSubmit={handleSubmit} className="form-stack">
            <label>Email<input type="email" autoComplete="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" /></label>
            <label>Password<input type="password" autoComplete="current-password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Enter your password" /></label>
            <button className="button primary full" disabled={submitting}>{submitting ? 'Signing in…' : 'Sign in'}</button>
          </form>
          <p className="auth-switch">New to Ledger? <Link to="/signup">Create an account</Link></p>
        </div>
      </main>
    </div>
  )
}
