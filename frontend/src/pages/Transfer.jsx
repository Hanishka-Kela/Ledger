import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAccounts } from '../api/accounts.js'
import { createTransfer } from '../api/transactions.js'
import Alert from '../components/Alert.jsx'
import LoadingState from '../components/LoadingState.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { formatAmount, formatDate } from '../utils/format.js'

export default function Transfer() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ source_account_id: '', destination_account_id: '', amount: '', description: '' })
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    getAccounts().then((items) => {
      setAccounts(items)
      if (items.length) setForm((current) => ({ ...current, source_account_id: current.source_account_id || items[0].account_id }))
    }).catch((err) => setError(err.message)).finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setResult(null)
    const amount = Number(form.amount)
    if (!Number.isInteger(amount) || amount <= 0) {
      setError('Amount must be a positive whole number.')
      return
    }
    setSubmitting(true)
    try {
      const transaction = await createTransfer({ ...form, amount })
      setResult(transaction)
      setForm((current) => ({ ...current, destination_account_id: '', amount: '', description: '' }))
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page narrow-page">
      <PageHeader eyebrow="New transaction" title="Transfer funds" description="Post a transfer from one of your accounts to any valid destination account." />
      <Alert>{error}</Alert>
      {result && <Alert type="success"><strong>Transfer posted.</strong> Transaction <Link to={`/transactions/${result.transaction_id}`}>{result.transaction_id}</Link> was created on {formatDate(result.timestamp)}.</Alert>}
      {loading ? <LoadingState label="Loading accounts…" /> : !accounts.length ? (
        <div className="empty-state"><span>▤</span><h3>An account is required</h3><p>Create a source account before posting a transfer.</p><Link className="button primary" to="/accounts?create=1">Create account</Link></div>
      ) : (
        <section className="panel transaction-form-panel">
          <form onSubmit={handleSubmit} className="form-stack">
            <label>Source account<select required value={form.source_account_id} onChange={(e) => setForm({ ...form, source_account_id: e.target.value })}>{accounts.map((account) => <option value={account.account_id} key={account.account_id}>{account.name} · {account.type}</option>)}</select><small>The account funds are transferred from.</small></label>
            <label>Destination account ID<input required value={form.destination_account_id} onChange={(e) => setForm({ ...form, destination_account_id: e.target.value.trim() })} placeholder="00000000-0000-0000-0000-000000000000" /><small>This may be an account owned by another user.</small></label>
            <div className="field-row">
              <label>Amount<input type="number" inputMode="numeric" min="1" step="1" required value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="0" /></label>
              <label>Description<input required value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="What is this transfer for?" /></label>
            </div>
            <div className="form-actions"><button className="button primary" disabled={submitting}>{submitting ? 'Posting transfer…' : 'Post transfer'}</button></div>
          </form>
        </section>
      )}
      {result && <section className="panel result-panel"><p className="eyebrow">Posted entries</p>{result.entries.map((entry) => <div className="result-entry" key={entry.entry_id}><span className={`entry-type ${entry.type.toLowerCase()}`}>{entry.type}</span><code>{entry.account_id}</code><strong>{formatAmount(entry.amount)}</strong></div>)}</section>}
    </div>
  )
}
