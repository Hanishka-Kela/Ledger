import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getAccountBalance, getAccounts, getAccountTransactions } from '../api/accounts.js'
import Alert from '../components/Alert.jsx'
import LoadingState from '../components/LoadingState.jsx'
import PageHeader from '../components/PageHeader.jsx'
import TransactionCard from '../components/TransactionCard.jsx'
import { formatAmount } from '../utils/format.js'

export default function AccountDetail() {
  const { accountId } = useParams()
  const [account, setAccount] = useState(null)
  const [balance, setBalance] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([getAccounts(), getAccountBalance(accountId), getAccountTransactions(accountId)])
      .then(([accounts, balanceData, transactionData]) => {
        if (!active) return
        const selected = accounts.find((item) => item.account_id === accountId)
        if (!selected) throw new Error('Account was not found in your ledger.')
        setAccount(selected)
        setBalance(balanceData.balance)
        setTransactions(transactionData)
      }).catch((err) => active && setError(err.message)).finally(() => active && setLoading(false))
    return () => { active = false }
  }, [accountId])

  const sortedTransactions = useMemo(() => [...transactions].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)), [transactions])

  if (loading) return <div className="page"><LoadingState label="Loading account…" /></div>
  if (error || !account) return <div className="page"><Link className="back-link" to="/accounts">← Back to accounts</Link><Alert>{error || 'Account not found.'}</Alert></div>

  return (
    <div className="page">
      <Link className="back-link" to="/accounts">← Back to accounts</Link>
      <PageHeader eyebrow={account.type} title={account.name} description="Account details and transaction history." />
      <section className="account-summary panel">
        <div><p>Current balance</p><strong>{formatAmount(balance)}</strong></div>
        <div><p>Account type</p><span className="type-pill">{account.type}</span></div>
        <div className="id-block"><p>Account ID</p><code>{account.account_id}</code></div>
      </section>
      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">Activity</p><h2>Transaction history</h2></div><span className="count-badge">{transactions.length}</span></div>
        {sortedTransactions.length ? <div className="transaction-list">{sortedTransactions.map((transaction) => <TransactionCard key={transaction.transaction_id} transaction={transaction} accountId={accountId} />)}</div> : <div className="empty-state compact"><span>↔</span><h3>No transactions</h3><p>Transactions involving this account will appear here.</p></div>}
      </section>
    </div>
  )
}
