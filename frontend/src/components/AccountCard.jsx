import { Link } from 'react-router-dom'
import { formatAmount } from '../utils/format.js'

export default function AccountCard({ account, balance, balanceError }) {
  return (
    <Link to={`/accounts/${account.account_id}`} className="account-card">
      <div className="account-card-top">
        <span className={`account-icon type-${account.type.toLowerCase()}`}>{account.name[0]?.toUpperCase()}</span>
        <span className="badge">{account.type}</span>
      </div>
      <h3>{account.name}</h3>
      <p className="muted-label">Current balance</p>
      {balanceError ? <span className="balance-error">Unavailable</span> : balance === undefined ? <span className="skeleton short" /> : <strong className="balance">{formatAmount(balance)}</strong>}
      <span className="card-link">View account <span>→</span></span>
    </Link>
  )
}
