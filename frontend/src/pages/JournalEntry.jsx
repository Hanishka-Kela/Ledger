import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAccounts } from '../api/accounts.js'
import { createJournal } from '../api/transactions.js'
import Alert from '../components/Alert.jsx'
import LoadingState from '../components/LoadingState.jsx'
import PageHeader from '../components/PageHeader.jsx'

const blankEntry = (accountId = '', type = 'DEBIT') => ({ account_id: accountId, type, amount: '' })

export default function JournalEntry() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [description, setDescription] = useState('')
  const [entries, setEntries] = useState([blankEntry('', 'DEBIT'), blankEntry('', 'CREDIT')])
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    getAccounts().then((items) => {
      setAccounts(items)
      if (items.length) setEntries([blankEntry(items[0].account_id, 'DEBIT'), blankEntry(items[0].account_id, 'CREDIT')])
    }).catch((err) => setError(err.message)).finally(() => setLoading(false))
  }, [])

  const totals = useMemo(() => entries.reduce((sum, entry) => {
    const amount = Number(entry.amount) || 0
    sum[entry.type] += amount
    return sum
  }, { DEBIT: 0, CREDIT: 0 }), [entries])

  const updateEntry = (index, field, value) => setEntries((current) => current.map((entry, entryIndex) => entryIndex === index ? { ...entry, [field]: value } : entry))
  const addEntry = () => setEntries((current) => [...current, blankEntry(accounts[0]?.account_id)])
  const removeEntry = (index) => {
    if (entries.length <= 2) return
    setEntries((current) => current.filter((_, entryIndex) => entryIndex !== index))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setResult(null)
    if (entries.length < 2) {
      setError('A journal transaction requires at least two entries.')
      return
    }
    const mappedEntries = entries.map((entry) => ({ ...entry, amount: Number(entry.amount) }))
    if (mappedEntries.some((entry) => !Number.isInteger(entry.amount) || entry.amount <= 0)) {
      setError('Each entry amount must be a positive whole number.')
      return
    }
    setSubmitting(true)
    try {
      const transaction = await createJournal({ description, entries: mappedEntries })
      setResult(transaction)
      setDescription('')
      setEntries([blankEntry(accounts[0].account_id, 'DEBIT'), blankEntry(accounts[0].account_id, 'CREDIT')])
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <PageHeader eyebrow="Advanced" title="Journal entry" description="Build a custom double-entry transaction. Accounting validation is performed by the ledger." />
      <Alert>{error}</Alert>
      {result && <Alert type="success">Journal transaction posted successfully. <Link to={`/transactions/${result.transaction_id}`}>View transaction →</Link></Alert>}
      {loading ? <LoadingState label="Loading accounts…" /> : !accounts.length ? (
        <div className="empty-state"><span>▤</span><h3>Accounts are required</h3><p>Create accounts before posting a journal entry.</p><Link className="button primary" to="/accounts?create=1">Create account</Link></div>
      ) : (
        <form onSubmit={handleSubmit}>
          <section className="panel journal-panel">
            <label className="description-field">Description<input required value={description} onChange={(e) => setDescription(e.target.value)} placeholder="e.g. Record owner capital" /></label>
            <div className="journal-table-wrap">
              <table className="journal-table">
                <thead><tr><th>Account</th><th>Entry type</th><th>Amount</th><th><span className="sr-only">Actions</span></th></tr></thead>
                <tbody>{entries.map((entry, index) => (
                  <tr key={index}>
                    <td><select aria-label={`Account for entry ${index + 1}`} required value={entry.account_id} onChange={(e) => updateEntry(index, 'account_id', e.target.value)}>{accounts.map((account) => <option key={account.account_id} value={account.account_id}>{account.name} · {account.type}</option>)}</select></td>
                    <td><select aria-label={`Type for entry ${index + 1}`} value={entry.type} onChange={(e) => updateEntry(index, 'type', e.target.value)}><option>DEBIT</option><option>CREDIT</option></select></td>
                    <td><input aria-label={`Amount for entry ${index + 1}`} type="number" min="1" step="1" required value={entry.amount} onChange={(e) => updateEntry(index, 'amount', e.target.value)} placeholder="0" /></td>
                    <td><button type="button" className="remove-button" onClick={() => removeEntry(index)} disabled={entries.length <= 2} aria-label={`Remove entry ${index + 1}`}>×</button></td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
            <button type="button" className="button ghost" onClick={addEntry}>＋ Add entry</button>
            <div className="journal-footer">
              <div className="totals"><span>Debit total <strong>{totals.DEBIT}</strong></span><span>Credit total <strong>{totals.CREDIT}</strong></span></div>
              <button className="button primary" disabled={submitting}>{submitting ? 'Posting journal…' : 'Post journal entry'}</button>
            </div>
          </section>
        </form>
      )}
    </div>
  )
}
