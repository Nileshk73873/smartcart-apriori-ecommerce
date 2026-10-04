import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import api from '../api'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react'

export default function SignUp() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const from = location.state?.from || '/'

  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('')
  }

  // Password strength checker
  const getStrength = (pw) => {
    let score = 0
    if (pw.length >= 8) score++
    if (/[A-Z]/.test(pw)) score++
    if (/[0-9]/.test(pw)) score++
    if (/[^A-Za-z0-9]/.test(pw)) score++
    return score
  }

  const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong']
  const strengthColors = ['', 'bg-red-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500']
  const pwStrength = getStrength(form.password)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match')
      return
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    setLoading(true)
    setError('')
    try {
      // Create account
      await api.post('/auth/signup', {
        username: form.username,
        email: form.email || null,
        password: form.password,
      })
      // Auto login
      const loginRes = await api.post('/auth/login', {
        username: form.username,
        password: form.password,
      })
      login(loginRes.data)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || 'Sign up failed. Please try again.')
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
        <h1 className="text-2xl font-semibold mb-5">Create account</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-300 rounded-md text-red-700 text-sm flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="su-username" className="block text-sm font-bold text-gray-800 mb-1">
              Username
            </label>
            <input
              id="su-username"
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              required
              autoFocus
              minLength={3}
              placeholder="At least 3 characters"
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-[#f90] focus:border-[#f90] text-sm"
            />
          </div>

          <div>
            <label htmlFor="su-email" className="block text-sm font-bold text-gray-800 mb-1">
              Email <span className="font-normal text-gray-500">(optional)</span>
            </label>
            <input
              id="su-email"
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-[#f90] focus:border-[#f90] text-sm"
            />
          </div>

          <div>
            <label htmlFor="su-password" className="block text-sm font-bold text-gray-800 mb-1">
              Password
            </label>
            <div className="relative">
              <input
                id="su-password"
                type={showPass ? 'text' : 'password'}
                name="password"
                value={form.password}
                onChange={handleChange}
                required
                minLength={6}
                placeholder="At least 6 characters"
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
            {/* Password strength */}
            {form.password && (
              <div className="mt-2">
                <div className="flex gap-1 mb-1">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                        i <= pwStrength ? strengthColors[pwStrength] : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-gray-500">
                  Password strength: <strong>{strengthLabel[pwStrength]}</strong>
                </span>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="su-confirm" className="block text-sm font-bold text-gray-800 mb-1">
              Re-enter password
            </label>
            <div className="relative">
              <input
                id="su-confirm"
                type={showConfirm ? 'text' : 'password'}
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 text-sm pr-10 ${
                  form.confirmPassword && form.password !== form.confirmPassword
                    ? 'border-red-400 focus:ring-red-400'
                    : form.confirmPassword && form.password === form.confirmPassword
                    ? 'border-green-400 focus:ring-green-400'
                    : 'border-gray-400 focus:ring-[#f90] focus:border-[#f90]'
                }`}
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
              {form.confirmPassword && form.password === form.confirmPassword && (
                <CheckCircle2 className="absolute right-9 top-1/2 -translate-y-1/2 w-4 h-4 text-green-500" />
              )}
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
                Creating account...
              </span>
            ) : 'Create your SmartCart account'}
          </button>
        </form>

        <p className="text-xs text-gray-500 mt-4 leading-relaxed">
          By creating an account, you agree to SmartCart's{' '}
          <span className="text-[#0066c0] cursor-pointer hover:underline">Conditions of Use</span>{' '}
          and{' '}
          <span className="text-[#0066c0] cursor-pointer hover:underline">Privacy Notice</span>.
        </p>
      </div>

      <div className="w-full max-w-sm mt-4 text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link
          to="/login"
          state={{ from }}
          className="text-[#0066c0] hover:text-[#c45500] hover:underline font-medium"
        >
          Sign in
        </Link>
      </div>
    </div>
  )
}
