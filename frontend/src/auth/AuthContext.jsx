import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import * as authApi from '../api/auth.js'
import { clearToken, getStoredToken, storeToken } from '../api/client.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getStoredToken()))

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
    setLoading(false)
  }, [])

  useEffect(() => {
    const handleUnauthorized = () => logout()
    window.addEventListener('ledger:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('ledger:unauthorized', handleUnauthorized)
  }, [logout])

  useEffect(() => {
    if (!getStoredToken()) return
    authApi.getMe()
      .then(setUser)
      .catch(() => logout())
      .finally(() => setLoading(false))
  }, [logout])

  const login = async (credentials) => {
    const result = await authApi.login(credentials)
    storeToken(result.access_token)
    try {
      const profile = await authApi.getMe()
      setUser(profile)
      return profile
    } catch (error) {
      logout()
      throw error
    }
  }

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
