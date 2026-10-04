import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import api from '../api'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff, ShoppingBag, AlertCircle } from 'lucide-react'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const from = location.state?.from || '/'

  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/auth/login', form)
      login(res.data)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f3f3f3] flex flex-col items-center py-8 px-4">
      {/* Logo */}
      <Link to="/" className="mb-6">
        <span className="text-3xl font-bold text-[#131921]">
          SmartCart<span className="text-[#f90]">.co.uk</span>
        </span>
      </Link>

      <div className="w-full max-w-sm bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h1 className="text-2xl font-semibold mb-5">Sign in</h1>

        {location.state?.message && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-blue-800 text-sm flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{location.state.message}</span>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-300 rounded-md text-red-700 text-sm flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-bold text-gray-800 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              required
              autoFocus
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-[#f90] focus:border-[#f90] text-sm"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-bold text-gray-800 mb-1">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPass ? 'text' : 'password'}
                name="password"
                value={form.password}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-[#f90] focus:border-[#f90] text-sm pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-[#FFD814] hover:bg-[#F7CA00] border border-[#FCD200] rounded-full font-medium text-sm shadow-sm transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Signing in...
              </span>
            ) : 'Sign in'}
          </button>
        </form>

        <p className="text-xs text-gray-500 mt-4 leading-relaxed">
          By continuing, you agree to SmartCart's{' '}
          <span className="text-[#0066c0] cursor-pointer hover:text-[#c45500] hover:underline">Conditions of Use</span>{' '}
          and{' '}
          <span className="text-[#0066c0] cursor-pointer hover:text-[#c45500] hover:underline">Privacy Notice</span>.
        </p>
      </div>

      <div className="w-full max-w-sm mt-4">
        <div className="relative flex items-center">
          <div className="flex-grow border-t border-gray-300" />
          <span className="mx-3 text-xs text-gray-500 whitespace-nowrap">New to SmartCart?</span>
          <div className="flex-grow border-t border-gray-300" />
        </div>
        <Link
          to="/signup"
          state={{ from }}
          className="mt-3 w-full flex items-center justify-center gap-2 py-2 px-4 bg-white hover:bg-gray-50 border border-gray-300 rounded-full font-medium text-sm shadow-sm transition-all duration-150"
        >
          <ShoppingBag className="w-4 h-4" />
          Create your SmartCart account
        </Link>
      </div>
    </div>
  )
}
