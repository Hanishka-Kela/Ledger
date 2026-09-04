import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import { getAccountBalance, getAccounts } from '../api/accounts.js'
import AccountCard from '../components/AccountCard.jsx'
import Alert from '../components/Alert.jsx'
import LoadingState from '../components/LoadingState.jsx'
import PageHeader from '../components/PageHeader.jsx'

export default function Dashboard() {
  const { user } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [balances, setBalances] = useState({})
  const [balanceErrors, setBalanceErrors] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    let loadedAccounts = []
    getAccounts().then((data) => {
      if (!active) return
      loadedAccounts = data
      setAccounts(data)
      return Promise.allSettled(data.map((account) => getAccountBalance(account.account_id)))
    }).then((results) => {
      if (!active || !results) return
      const nextBalances = {}
      const nextErrors = {}
      results.forEach((result, index) => {
        const id = loadedAccounts[index]?.account_id
        if (result.status === 'fulfilled') nextBalances[result.value.account_id] = result.value.balance
        else if (id) nextErrors[id] = true
      })
      setBalances(nextBalances)
      setBalanceErrors(nextErrors)
    }).catch((err) => active && setError(err.message)).finally(() => active && setLoading(false))
    return () => { active = false }
  }, [])

  return (
    <div className="page">
      <PageHeader eyebrow="Overview" title="Dashboard" description={`Welcome back, ${user.email}.`} />
      <Alert>{error}</Alert>
      <section className="summary-grid">
        <div className="stat-card"><span className="stat-icon">▤</span><div><p>Accounts</p><strong>{loading ? '—' : accounts.length}</strong></div></div>
        <div className="quick-actions-card">
          <div><p className="eyebrow">Quick actions</p><h2>What would you like to do?</h2></div>
          <div className="action-row">
            <Link className="button secondary" to="/accounts?create=1">＋ Create account</Link>
            <Link className="button secondary" to="/transfer">⇄ Transfer</Link>
            <Link className="button secondary" to="/journal">≡ Journal entry</Link>
          </div>
        </div>
      </section>
      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">Your ledger</p><h2>Accounts</h2></div><Link to="/accounts" className="text-link">View all →</Link></div>
        {loading ? <LoadingState label="Loading accounts…" /> : accounts.length ? (
          <div className="account-grid">{accounts.map((account) => <AccountCard key={account.account_id} account={account} balance={balances[account.account_id]} balanceError={balanceErrors[account.account_id]} />)}</div>
        ) : <div className="empty-state"><span>▤</span><h3>No accounts yet</h3><p>Create your first account to begin recording transactions.</p><Link className="button primary" to="/accounts?create=1">Create account</Link></div>}
      </section>
    </div>
  )
}
