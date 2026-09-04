import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '◫' },
  { to: '/accounts', label: 'Accounts', icon: '▤' },
  { to: '/transfer', label: 'Transfer', icon: '⇄' },
  { to: '/journal', label: 'Journal', icon: '≡' },
]

export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/dashboard" className="brand" aria-label="Ledger dashboard">
          <span className="brand-mark">L</span>
          <span>Ledger</span>
        </NavLink>
        <nav className="nav-list" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
              <span className="nav-icon" aria-hidden="true">{item.icon}</span>{item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-chip">
            <span className="avatar">{user?.email?.[0]?.toUpperCase()}</span>
            <span className="truncate">{user?.email}</span>
          </div>
          <button className="nav-item logout-button" onClick={handleLogout}><span className="nav-icon">↪</span>Logout</button>
        </div>
      </aside>
      <main className="main-content"><Outlet /></main>
    </div>
  )
}
