import { apiRequest } from './client.js'

export const getAccounts = () => apiRequest('/accounts')

export const createAccount = (payload) => apiRequest('/accounts', {
  method: 'POST',
  body: JSON.stringify(payload),
})

export const getAccountBalance = (accountId) => apiRequest(`/accounts/${accountId}/balance`)

export const getAccountTransactions = (accountId) => apiRequest(`/accounts/${accountId}/transactions`)
