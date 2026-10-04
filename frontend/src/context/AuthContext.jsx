import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { API_URL } from '../config'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('smartcart_user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })
  const [cartCount, setCartCount] = useState(0)

  const fetchCartCount = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/cart/count`)
      setCartCount(res.data.count)
    } catch {
      setCartCount(0)
    }
  }, [])

  useEffect(() => {
    fetchCartCount()
  }, [fetchCartCount])

  const login = (userData) => {
    setUser(userData)
    localStorage.setItem('smartcart_user', JSON.stringify(userData))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('smartcart_user')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, cartCount, setCartCount, fetchCartCount }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
