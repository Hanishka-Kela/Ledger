import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { createAccount, getAccountBalance, getAccounts } from '../api/accounts.js'
import AccountCard from '../components/AccountCard.jsx'
import Alert from '../components/Alert.jsx'
import LoadingState from '../components/LoadingState.jsx'
import PageHeader from '../components/PageHeader.jsx'

const accountTypes = ['ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE']

export default function Accounts() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [accounts, setAccounts] = useState([])
  const [balances, setBalances] = useState({})
  const [balanceErrors, setBalanceErrors] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showForm, setShowForm] = useState(searchParams.get('create') === '1')
  const [form, setForm] = useState({ name: '', account_type: 'ASSET' })
  const [submitting, setSubmitting] = useState(false)

  const loadAccounts = useCallback(async () => {
    setError('')
    try {
      const items = await getAccounts()
      setAccounts(items)
      const results = await Promise.allSettled(items.map((item) => getAccountBalance(item.account_id)))
      const values = {}
      const errors = {}
      results.forEach((result, index) => {
        const id = items[index].account_id
        if (result.status === 'fulfilled') values[id] = result.value.balance
        else errors[id] = true
      })
      setBalances(values)
      setBalanceErrors(errors)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadAccounts() }, [loadAccounts])

  const closeForm = () => {
    setShowForm(false)
    searchParams.delete('create')
    setSearchParams(searchParams, { replace: true })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setSuccess('')
    try {
      await createAccount({ name: form.name.trim(), account_type: form.account_type })
      setForm({ name: '', account_type: 'ASSET' })
      setSuccess('Account created successfully.')
      closeForm()
      await loadAccounts()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <PageHeader eyebrow="Manage" title="Accounts" description="Create and review the accounts in your ledger." actions={<button className="button primary" onClick={() => setShowForm(true)}>＋ Create account</button>} />
      <Alert>{error}</Alert><Alert type="success">{success}</Alert>
      {showForm && (
        <section className="panel form-panel">
          <div className="panel-header"><div><h2>New account</h2><p>Add an account to your ledger.</p></div><button className="icon-button" aria-label="Close form" onClick={closeForm}>×</button></div>
          <form onSubmit={handleSubmit} className="inline-form">
            <label>Account name<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Operating Cash" /></label>
            <label>Account type<select value={form.account_type} onChange={(e) => setForm({ ...form, account_type: e.target.value })}>{accountTypes.map((type) => <option key={type}>{type}</option>)}</select></label>
            <button className="button primary" disabled={submitting}>{submitting ? 'Creating…' : 'Create account'}</button>
          </form>
        </section>
      )}
      {loading ? <LoadingState label="Loading accounts…" /> : accounts.length ? <div className="account-grid">{accounts.map((account) => <AccountCard key={account.account_id} account={account} balance={balances[account.account_id]} balanceError={balanceErrors[account.account_id]} />)}</div> : <div className="empty-state"><span>▤</span><h3>No accounts yet</h3><p>Create an account to get started.</p></div>}
    </div>
  )
}
