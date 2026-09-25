import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../config'

export default function Checkout() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    customer_name: '', email: '', address: '', city: '', postal_code: ''
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(null)

  const handleChange = e => setFormData({...formData, [e.target.name]: e.target.value})

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await axios.post(`${API_URL}/cart/checkout`, formData)
      setSuccess(res.data)
    } catch (err) {
      console.error(err)
      alert(err.response?.data?.detail || "Checkout failed")
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="max-w-2xl mx-auto mt-20 bg-white p-12 rounded-2xl shadow-xl text-center border-t-8 border-green-500">
        <div className="w-20 h-20 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
        </div>
        <h1 className="text-4xl font-bold mb-4 text-gray-800">Order Confirmed!</h1>
        <p className="text-xl text-gray-600 mb-8">Thank you for shopping with SmartCart.</p>
        <div className="bg-gray-50 p-6 rounded-lg mb-8 text-left">
          <p className="text-gray-500 mb-2">Order Reference: <span className="font-bold text-gray-800">#ORD-{success.id.toString().padStart(6, '0')}</span></p>
          <p className="text-gray-500">Final Total: <span className="font-bold text-indigo-600">£{success.total.toFixed(2)}</span></p>
        </div>
        <button onClick={() => navigate('/')} className="bg-indigo-600 text-white px-8 py-3 rounded-full font-bold hover:bg-indigo-700">Back to Home</button>
      </div>
    )
  }

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-lg border">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
            <input required type="text" name="customer_name" value={formData.customer_name} onChange={handleChange} className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
            <input required type="email" name="email" value={formData.email} onChange={handleChange} className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Shipping Address</label>
            <input required type="text" name="address" value={formData.address} onChange={handleChange} className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
          </div>
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-2">City</label>
              <input required type="text" name="city" value={formData.city} onChange={handleChange} className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-semibold text-gray-700 mb-2">Postal Code</label>
              <input required type="text" name="postal_code" value={formData.postal_code} onChange={handleChange} className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
            </div>
          </div>
        </div>
        
        <div className="mt-10 pt-6 border-t">
          <p className="text-sm text-gray-500 mb-4">* This is a prototype. No real payment will be processed.</p>
          <button 
            type="submit" 
            disabled={loading}
            className={`w-full py-4 rounded-xl font-bold text-lg text-white shadow-lg ${loading ? 'bg-gray-400' : 'bg-indigo-600 hover:bg-indigo-700'}`}
          >
            {loading ? 'Processing...' : 'Place Simulated Order'}
          </button>
        </div>
      </form>
    </div>
  )
}
