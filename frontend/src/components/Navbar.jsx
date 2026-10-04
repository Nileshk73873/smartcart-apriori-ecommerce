import React, { useRef, useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShoppingCart, Search, Menu, MapPin, LogOut, Package, ChevronDown } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import api from '../api'

export default function Navbar() {
  const navigate = useNavigate()
  const { user, logout, cartCount } = useAuth()
  const [accountOpen, setAccountOpen] = useState(false)
  const dropdownRef = useRef(null)
  const [relatedProducts, setRelatedProducts] = useState([])

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setAccountOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  useEffect(() => {
    const fetchRelated = async () => {
      try {
        const res = await api.get('/recommendations/related_products')
        setRelatedProducts(res.data)
      } catch (err) {
        console.error("Error fetching related products for dropdown", err)
      }
    }
    fetchRelated()
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    const q = e.target.search.value
    if (q) navigate(`/products?q=${encodeURIComponent(q)}`)
  }

  const handleLogout = () => {
    logout()
    setAccountOpen(false)
    navigate('/')
  }

  return (
    <header className="bg-[#131921]">
      <div className="text-white flex items-center justify-between px-4 py-2">
        {/* Left: Logo & Deliver To */}
        <div className="flex items-center space-x-2 sm:space-x-4">
          <Link to="/" className="flex flex-col justify-center border border-transparent hover:border-white p-1 rounded flex-shrink-0">
            <span className="text-xl md:text-2xl font-bold tracking-tight">SmartCart<span className="text-[#f90]">.co.uk</span></span>
          </Link>

          <div className="hidden sm:flex items-center border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0">
            <MapPin className="w-5 h-5 text-gray-300 mt-2" />
            <div className="flex flex-col ml-1">
              <span className="text-xs text-gray-300 leading-3">Deliver to</span>
              <span className="text-sm font-bold leading-4">United Kingdom</span>
            </div>
          </div>
        </div>

        {/* Middle: Search (Desktop) */}
        <form onSubmit={handleSearch} className="flex-1 hidden md:flex mx-4">
          <select
            className="bg-gray-100 border-r border-gray-300 text-gray-700 text-sm px-2 rounded-l-md focus:outline-none max-w-[150px] truncate"
            onChange={(e) => {
              if (e.target.value !== 'all') {
                navigate(`/products/${e.target.value}`)
                e.target.value = 'all'
              }
            }}
          >
            <option value="all">All (Related Items)</option>
            {relatedProducts.map(p => (
              <option key={p.id} value={p.id} className="truncate">
                {p.name}
              </option>
            ))}
          </select>
          <input
            type="text"
            name="search"
            placeholder="Search Amazon-style..."
            className="flex-1 px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#f90] min-w-0"
          />
          <button type="submit" className="bg-[#febd69] hover:bg-[#f3a847] px-4 py-2 rounded-r-md flex items-center justify-center">
            <Search className="text-gray-900 w-5 h-5" />
          </button>
        </form>

        {/* Right: Account & Cart */}
        <div className="flex items-center space-x-2 md:space-x-4 relative" ref={dropdownRef}>
          {/* Mobile Login */}
          <div className="md:hidden flex items-center">
            {user ? (
              <button onClick={() => setAccountOpen(!accountOpen)} className="flex items-center text-sm font-bold">
                {user.username.substring(0, 8)} <ChevronDown className="w-4 h-4 ml-1 mt-1" />
              </button>
            ) : (
              <Link to="/login" className="flex items-center text-sm">Sign in</Link>
            )}
          </div>

          {/* Desktop Account Dropdown Button */}
          <button
            onClick={() => setAccountOpen(!accountOpen)}
            className="hidden md:flex flex-col border border-transparent hover:border-white p-1 rounded cursor-pointer text-left"
          >
            <span className="text-xs text-gray-300 leading-3">
              {user ? `Hello, ${user.username}` : 'Hello, sign in'}
            </span>
            <span className="text-sm font-bold leading-4 flex items-center gap-0.5">
              Account &amp; Lists <ChevronDown className="w-3 h-3 mt-0.5" />
            </span>
          </button>

          {/* Universal Dropdown Menu */}
          {accountOpen && (
            <div className="absolute right-0 top-12 md:top-full mt-1 w-56 bg-white rounded-lg shadow-xl border border-gray-200 z-50 py-2 text-gray-800">
              {user ? (
                <>
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-semibold text-gray-900">{user.username}</p>
                    {user.email && <p className="text-xs text-gray-500 truncate">{user.email}</p>}
                  </div>
                  <Link
                    to="/orders"
                    onClick={() => setAccountOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 text-sm"
                  >
                    <Package className="w-4 h-4 text-gray-500" />
                    Your Orders
                  </Link>
                  <hr className="my-1 border-gray-100" />
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-4 py-2.5 hover:bg-red-50 text-sm text-red-600 w-full text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign out
                  </button>
                </>
              ) : (
                <>
                  <div className="px-4 py-3 text-center border-b border-gray-100">
                    <Link
                      to="/login"
                      onClick={() => setAccountOpen(false)}
                      className="block w-full py-1.5 bg-[#FFD814] hover:bg-[#F7CA00] border border-[#FCD200] rounded-full text-sm font-medium shadow-sm"
                    >
                      Sign in
                    </Link>
                    <p className="text-xs text-gray-600 mt-2">
                      New customer?{' '}
                      <Link
                        to="/signup"
                        onClick={() => setAccountOpen(false)}
                        className="text-[#0066c0] hover:underline"
                      >
                        Start here
                      </Link>
                    </p>
                  </div>
                  <Link
                    to="/orders"
                    onClick={() => setAccountOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 text-sm"
                  >
                    <Package className="w-4 h-4 text-gray-500" />
                    Your Orders
                  </Link>
                </>
              )}
            </div>
          )}

          {/* Returns & Orders (Desktop) */}
          <Link
            to="/orders"
            className="hidden lg:flex flex-col border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0"
          >
            <span className="text-xs text-gray-300 leading-3">Returns</span>
            <span className="text-sm font-bold leading-4">&amp; Orders</span>
          </Link>

          {/* Cart */}
          <Link to="/cart" className="flex items-center border border-transparent hover:border-white p-2 rounded relative flex-shrink-0 text-white">
            <ShoppingCart className="w-7 h-7 sm:w-8 sm:h-8" />
            <span className="absolute top-1 left-5 sm:left-6 text-[#f90] font-bold text-xs sm:text-sm bg-[#131921] px-1 rounded-full min-w-[1.2rem] text-center">
              {cartCount}
            </span>
            <span className="hidden sm:inline font-bold mt-3 ml-1">Cart</span>
          </Link>
        </div>
      </div>

      {/* Search Bar (Mobile Only) */}
      <div className="md:hidden px-4 pb-3 w-full">
        <form onSubmit={handleSearch} className="flex w-full">
          <select
            className="bg-gray-100 border-r border-gray-300 text-gray-700 text-sm px-2 rounded-l-md focus:outline-none max-w-[80px] truncate"
            onChange={(e) => {
              if (e.target.value !== 'all') {
                navigate(`/products/${e.target.value}`)
                e.target.value = 'all'
              }
            }}
          >
            <option value="all">All</option>
            {relatedProducts.map(p => (
              <option key={p.id} value={p.id} className="truncate">
                {p.name}
              </option>
            ))}
          </select>
          <input
            type="text"
            name="search"
            placeholder="Search products..."
            className="flex-1 px-3 py-2 text-black text-sm focus:outline-none focus:ring-2 focus:ring-[#f90] min-w-0"
          />
          <button type="submit" className="bg-[#febd69] hover:bg-[#f3a847] px-3 py-2 rounded-r-md flex items-center justify-center">
            <Search className="text-gray-900 w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Subnav */}
      <div className="bg-[#232f3e] text-white text-sm flex items-center px-4 py-1 space-x-4 overflow-x-auto whitespace-nowrap hide-scrollbar">
        <Link to="/products" className="flex items-center space-x-1 border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0">
          <Menu className="w-5 h-5" />
          <span className="font-bold">All</span>
        </Link>
        <Link to="/products?q=deals" className="border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0">Today's Deals</Link>
        <Link to="/orders" className="border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0">Customer Service</Link>
        <Link to="/products?q=home" className="border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0">Registry</Link>
        <Link to="/products?q=gift" className="border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0">Gift Cards</Link>
        <Link to="/products" className="border border-transparent hover:border-white p-1 rounded cursor-pointer flex-shrink-0">Sell</Link>
        {user && (
          <>
            <Link to="/orders" className="border border-transparent hover:border-white p-1 rounded cursor-pointer font-medium text-[#f90] flex-shrink-0">
              My Orders
            </Link>
            {user.is_admin && (
              <Link to="/admin" className="border border-transparent hover:border-white p-1 rounded cursor-pointer font-bold text-red-400 flex-shrink-0">
                Admin Panel
              </Link>
            )}
          </>
        )}
      </div>
    </header>
  )
}
