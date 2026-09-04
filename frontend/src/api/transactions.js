import { apiRequest } from './client.js'

export const createTransfer = (payload) => apiRequest('/transactions', {
  method: 'POST',
  body: JSON.stringify(payload),
})

export const createJournal = (payload) => apiRequest('/transactions/journal', {
  method: 'POST',
  body: JSON.stringify(payload),
})

export const getTransaction = (transactionId) => apiRequest(`/transactions/${transactionId}`)
