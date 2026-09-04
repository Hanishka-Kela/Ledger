import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signup } from '../api/auth.js'
import Alert from '../components/Alert.jsx'

export default function Signup() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', confirm_password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match.')
      return
    }
    setSubmitting(true)
    try {
      await signup(form)
      navigate('/login', { replace: true, state: { message: 'Account created successfully. Sign in to continue.' } })
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
        <div className="auth-message"><p className="eyebrow light">Get started</p><h1>Your books, clearly organized.</h1><p>Create an account and start building a reliable financial record.</p></div>
        <p className="auth-footnote">Simple. Reliable. Balanced.</p>
      </div>
      <main className="auth-main">
        <div className="auth-card">
          <p className="eyebrow">Create account</p>
          <h2>Start using Ledger</h2>
          <p className="muted">Set up your credentials below.</p>
          <Alert>{error}</Alert>
          <form onSubmit={handleSubmit} className="form-stack">
            <label>Email<input type="email" autoComplete="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" /></label>
            <label>Password<input type="password" autoComplete="new-password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Create a password" /></label>
            <label>Confirm password<input type="password" autoComplete="new-password" required value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} placeholder="Repeat your password" /></label>
            <button className="button primary full" disabled={submitting}>{submitting ? 'Creating account…' : 'Create account'}</button>
          </form>
          <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
        </div>
      </main>
    </div>
  )
}
