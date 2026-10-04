import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import ProductList from './pages/ProductList'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Checkout from './pages/Checkout'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Orders from './pages/Orders'
import AdminLayout from './pages/Admin'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/products" element={<ProductList />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/admin/*" element={<AdminLayout />} />
            </Routes>
          </main>

          <footer className="bg-[#131921] text-white text-center py-6 mt-auto">
            <div className="mb-1 text-lg font-bold">
              SmartCart<span className="text-[#f90]">.co.uk</span>
            </div>
            <p className="text-gray-400 text-sm">&copy; 2026 SmartCart AI. Prototype Application.</p>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
