import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getTransaction } from '../api/transactions.js'
import Alert from '../components/Alert.jsx'
import LoadingState from '../components/LoadingState.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { formatAmount, formatDate } from '../utils/format.js'

export default function TransactionDetail() {
  const { transactionId } = useParams()
  const [transaction, setTransaction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getTransaction(transactionId).then((data) => active && setTransaction(data)).catch((err) => active && setError(err.message)).finally(() => active && setLoading(false))
    return () => { active = false }
  }, [transactionId])

  if (loading) return <div className="page"><LoadingState label="Loading transaction…" /></div>

  return (
    <div className="page">
      <Link className="back-link" to="/dashboard">← Back to dashboard</Link>
      <Alert>{error}</Alert>
      {transaction && <>
        <PageHeader eyebrow="Transaction" title={transaction.description || 'Untitled transaction'} description={formatDate(transaction.timestamp)} />
        <section className="panel transaction-meta"><div><p>Transaction ID</p><code>{transaction.transaction_id}</code></div><div><p>Entries</p><strong>{transaction.entries.length}</strong></div></section>
        <section className="section-block">
          <div className="section-heading"><div><p className="eyebrow">Double entry</p><h2>Transaction entries</h2></div></div>
          <div className="entries-table-wrap"><table className="entries-table"><thead><tr><th>Type</th><th>Account ID</th><th>Entry ID</th><th>Amount</th></tr></thead><tbody>{transaction.entries.map((entry) => <tr key={entry.entry_id}><td><span className={`entry-type ${entry.type.toLowerCase()}`}>{entry.type}</span></td><td><Link to={`/accounts/${entry.account_id}`}><code>{entry.account_id}</code></Link></td><td><code>{entry.entry_id}</code></td><td className="amount-cell">{formatAmount(entry.amount)}</td></tr>)}</tbody></table></div>
        </section>
      </>}
    </div>
  )
}
