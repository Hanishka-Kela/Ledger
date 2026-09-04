import { Link } from 'react-router-dom'
import { formatAmount, formatDate } from '../utils/format.js'

export default function TransactionCard({ transaction, accountId }) {
  const relevantEntries = transaction.entries.filter((entry) => entry.account_id === accountId)
  return (
    <Link className="transaction-card" to={`/transactions/${transaction.transaction_id}`}>
      <div className="transaction-main"><span className="transaction-icon">↔</span><div><h3>{transaction.description || 'Untitled transaction'}</h3><p>{formatDate(transaction.timestamp)}</p><code>{transaction.transaction_id}</code></div></div>
      <div className="entry-summary">
        {relevantEntries.map((entry) => <div key={entry.entry_id}><span className={`entry-type ${entry.type.toLowerCase()}`}>{entry.type}</span><strong>{formatAmount(entry.amount)}</strong></div>)}
      </div>
      <span className="chevron">›</span>
    </Link>
  )
}
