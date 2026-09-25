import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Trash2 } from 'lucide-react'
import { API_URL } from '../config'

export default function Cart() {
  const navigate = useNavigate()
  const [cart, setCart] = useState(null)
  const [cartRecs, setCartRecs] = useState([])

  const fetchCart = async () => {
    try {
      const res = await axios.get(`${API_URL}/cart/`)
      setCart(res.data)
      
      // Fetch cart based recommendations
      if (res.data.items.length > 0) {
        const itemIds = res.data.items.map(i => i.product.id)
        const recsRes = await axios.post(`${API_URL}/cart/recommendations`, itemIds)
        setCartRecs(recsRes.data)
      } else {
        setCartRecs([])
      }
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchCart()
  }, [])

  const updateQuantity = async (productId, newQuantity) => {
    try {
      await axios.put(`${API_URL}/cart/update`, { product_id: productId, quantity: newQuantity })
      fetchCart()
    } catch (err) {
      console.error(err)
    }
  }

  const removeItem = async (productId) => {
    try {
      await axios.delete(`${API_URL}/cart/remove/${productId}`)
      fetchCart()
    } catch (err) {
      console.error(err)
    }
  }

  const addToCart = async (productId) => {
    try {
      await axios.post(`${API_URL}/cart/add`, { product_id: productId, quantity: 1 })
      fetchCart()
    } catch (err) {
      console.error(err)
    }
  }

  if (!cart) return <div className="text-center py-20">Loading cart...</div>

  return (
    <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-8">
      <div className="lg:w-2/3">
        <h1 className="text-3xl font-bold mb-6">Your Cart</h1>
        {cart.items.length === 0 ? (
          <div className="bg-white rounded-xl shadow p-12 text-center">
            <p className="text-gray-500 mb-6 text-xl">Your cart is empty.</p>
            <Link to="/products" className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700">Continue Shopping</Link>
          </div>
        ) : (
          <div className="space-y-4 mb-8">
            {cart.items.map(item => (
              <div key={item.product.id} className="bg-white p-4 rounded-xl shadow-sm flex items-center justify-between border">
                <div className="flex items-center gap-4">
                  <img src={item.product.image_url} alt={item.product.name} className="w-20 h-20 object-cover rounded" />
                  <div>
                    <h3 className="font-semibold text-lg line-clamp-1 max-w-xs" title={item.product.name}>{item.product.name}</h3>
                    <p className="text-gray-500 font-medium">£{item.product.price.toFixed(2)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="flex items-center bg-gray-100 rounded-lg">
                    <button onClick={() => updateQuantity(item.product.id, item.quantity - 1)} className="px-3 py-1 font-bold text-gray-600 hover:bg-gray-200 rounded-l-lg">-</button>
                    <span className="px-3 font-semibold">{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.product.id, item.quantity + 1)} className="px-3 py-1 font-bold text-gray-600 hover:bg-gray-200 rounded-r-lg">+</button>
                  </div>
                  <div className="font-bold text-lg w-20 text-right">£{item.subtotal.toFixed(2)}</div>
                  <button onClick={() => removeItem(item.product.id)} className="text-red-500 hover:text-red-700 p-2"><Trash2 className="w-5 h-5" /></button>
                </div>
              </div>
            ))}
          </div>
        )}

        {cartRecs.length > 0 && (
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-xl border border-indigo-100 mt-8">
            <h2 className="text-xl font-bold mb-4 text-indigo-900">Complete Your Bundle</h2>
            <p className="text-indigo-700 mb-4">Customers who purchased items in your cart also bought:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {cartRecs.slice(0, 4).map((rec, idx) => (
                <div key={idx} className="bg-white p-3 rounded-lg shadow-sm flex items-center gap-3">
                  <img src={rec.product.image} className="w-16 h-16 object-cover rounded" alt={rec.product.name} />
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold line-clamp-2" title={rec.product.name}>{rec.product.name}</h4>
                    <p className="font-bold text-indigo-600 text-sm mb-1">£{rec.product.price.toFixed(2)}</p>
                    <button onClick={() => addToCart(rec.product.id)} className="text-xs bg-indigo-100 text-indigo-700 hover:bg-indigo-200 px-2 py-1 rounded font-semibold">
                      Add to Bundle
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="lg:w-1/3">
        <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
          <h2 className="text-2xl font-bold mb-6">Order Summary</h2>
          <div className="space-y-3 mb-6 pb-6 border-b border-gray-200 text-lg">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">£{cart.subtotal.toFixed(2)}</span>
            </div>
            
            {cart.discount > 0 && (
              <div className="flex justify-between text-green-600 font-semibold bg-green-50 p-2 rounded -mx-2 px-2">
                <div>
                  <span>Bundle Discount</span>
                  <div className="text-xs font-normal text-green-700">{cart.applied_bundle_tier}</div>
                </div>
                <span>-£{cart.discount.toFixed(2)}</span>
              </div>
            )}
            
            {cart.discount > 0 && cart.savings_reason && (
              <p className="text-sm text-green-600 mt-1 italic">{cart.savings_reason}</p>
            )}
          </div>
          
          <div className="flex justify-between items-center mb-8">
            <span className="text-xl font-bold">Total</span>
            <span className="text-3xl font-extrabold text-indigo-600">£{cart.final_total.toFixed(2)}</span>
          </div>

          <button 
            onClick={() => navigate('/checkout')}
            disabled={cart.items.length === 0}
            className={`w-full py-4 rounded-xl font-bold text-lg text-white shadow-lg transition-colors ${cart.items.length === 0 ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'}`}
          >
            Proceed to Checkout
          </button>
        </div>
      </div>
    </div>
  )
}
