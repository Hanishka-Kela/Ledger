const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')
const TOKEN_KEY = 'ledger_access_token'

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function storeToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export async function apiRequest(path, options = {}) {
  const token = getStoredToken()
  const headers = new Headers(options.headers)

  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  } catch {
    throw new ApiError('Unable to reach the Ledger API. Check that the backend is running.', 0)
  }

  const contentType = response.headers.get('content-type') || ''
  let data = null
  if (response.status !== 204) {
    try {
      data = contentType.includes('application/json') ? await response.json() : await response.text()
    } catch {
      data = null
    }
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearToken()
      window.dispatchEvent(new Event('ledger:unauthorized'))
    }
    const detail = data && typeof data === 'object' ? data.detail : data
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((item) => item?.msg).filter(Boolean).join(' ') || `Request failed with status ${response.status}`
        : `Request failed with status ${response.status}`
    throw new ApiError(message, response.status, data)
  }

  return data
}
