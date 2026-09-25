import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShoppingCart, Search, Package } from 'lucide-react'

export default function Navbar() {
  const navigate = useNavigate()
  
  const handleSearch = (e) => {
    e.preventDefault()
    const q = e.target.search.value
    if (q) {
      navigate(`/products?q=${q}`)
    }
  }

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2 text-2xl font-bold text-indigo-600">
            <Package className="w-8 h-8" />
            <span>SmartCart</span>
          </Link>
          
          <form onSubmit={handleSearch} className="flex-1 max-w-lg mx-8 hidden md:block">
            <div className="relative">
              <input 
                type="text" 
                name="search"
                placeholder="Search products..." 
                className="w-full pl-10 pr-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <Search className="absolute left-3 top-2.5 text-gray-400 w-5 h-5" />
            </div>
          </form>

          <div className="flex items-center space-x-6">
            <Link to="/products" className="text-gray-600 hover:text-indigo-600 font-medium">
              Shop
            </Link>
            <Link to="/cart" className="text-gray-600 hover:text-indigo-600 flex items-center relative">
              <ShoppingCart className="w-6 h-6" />
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
