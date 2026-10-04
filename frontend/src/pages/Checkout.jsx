import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api'
import { useAuth } from '../context/AuthContext'
import { AlertCircle, CheckCircle2 } from 'lucide-react'

export default function Checkout() {
  const navigate = useNavigate()
  const { user, setCartCount } = useAuth()
  const [cart, setCart] = useState(null)
  const [formData, setFormData] = useState({
    customer_name: user?.username || '',
    email: user?.email || '',
    address: '',
    city: '',
    postal_code: ''
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(null)
  const [checkoutError, setCheckoutError] = useState('')

  useEffect(() => {
    api.get('/cart/')
      .then(res => {
        setCart(res.data)
        if (res.data.items.length === 0) navigate('/cart')
      })
      .catch(console.error)
  }, [navigate])

  const handleChange = e => setFormData({...formData, [e.target.name]: e.target.value})

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setCheckoutError('')
    try {
      const payload = { ...formData, user_id: user?.id || null }
      const res = await api.post('/cart/checkout', payload)
      setSuccess(res.data)
      setCartCount(0)
    } catch (err) {
      console.error(err)
      const msg = err.response?.data?.detail || err.message || 'Checkout failed. Please try again.'
      setCheckoutError(msg)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="bg-white min-h-screen py-10 px-4">
        <div className="max-w-2xl mx-auto border p-6 shadow-sm border-t-4 border-t-green-500">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center font-bold text-xl">✓</div>
            <div>
              <h1 className="text-2xl font-bold text-green-700">Order placed, thank you!</h1>
              <p className="text-gray-600">Confirmation will be sent to your email.</p>
            </div>
          </div>
          
          <div className="border-t pt-4 text-sm text-gray-700">
             <p className="mb-2"><strong>Order Number:</strong> #ORD-{success.id.toString().padStart(6, '0')}</p>
             <p className="mb-2"><strong>Total Charged:</strong> £{success.total.toFixed(2)}</p>
             <p className="mt-6 mb-4">We've received your order and will begin processing it right away.</p>
             <Link to="/orders" className="text-blue-600 hover:underline hover:text-orange-600">Review or edit your recent orders</Link>
             <div className="mt-8">
               <Link to="/" className="bg-[#FFD814] hover:bg-[#F7CA00] border-[#FCD200] border rounded-full py-2 px-6 shadow-sm font-medium">
                 Continue shopping
               </Link>
             </div>
          </div>
        </div>
      </div>
    )
  }

  if (!cart) return <div className="text-center py-20">Loading...</div>

  return (
    <div className="bg-white min-h-screen pb-20">
      {/* Checkout header */}
      <header className="border-b bg-gray-50 py-4 px-8 flex justify-center">
        <h1 className="text-2xl font-medium tracking-tight">Checkout</h1>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8 flex flex-col md:flex-row gap-8">
        
        {/* Left: Form */}
        <div className="md:w-2/3">
          {/* Error Banner */}
          {checkoutError && (
            <div className="mb-4 p-4 bg-red-50 border border-red-300 rounded-lg flex items-start gap-3 text-red-700">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Order could not be placed</p>
                <p className="text-sm mt-0.5">{checkoutError}</p>
              </div>
            </div>
          )}
          <form id="checkout-form" onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-orange-600">1</span> Enter a delivery address
              </h2>
              <div className="border rounded-md p-4 ml-6 space-y-4">
                <div>
                  <label className="block text-sm font-bold text-gray-800 mb-1">Full name</label>
                  <input required type="text" name="customer_name" value={formData.customer_name} onChange={handleChange} className="w-full px-3 py-1.5 border border-gray-400 rounded focus:ring-2 focus:ring-orange-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-800 mb-1">Email</label>
                  <input required type="email" name="email" value={formData.email} onChange={handleChange} className="w-full px-3 py-1.5 border border-gray-400 rounded focus:ring-2 focus:ring-orange-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-800 mb-1">Address line 1</label>
                  <input required type="text" name="address" value={formData.address} onChange={handleChange} className="w-full px-3 py-1.5 border border-gray-400 rounded focus:ring-2 focus:ring-orange-500 focus:outline-none" />
                </div>
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-bold text-gray-800 mb-1">Town/City</label>
                    <input required type="text" name="city" value={formData.city} onChange={handleChange} className="w-full px-3 py-1.5 border border-gray-400 rounded focus:ring-2 focus:ring-orange-500 focus:outline-none" />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-bold text-gray-800 mb-1">Postcode</label>
                    <input required type="text" name="postal_code" value={formData.postal_code} onChange={handleChange} className="w-full px-3 py-1.5 border border-gray-400 rounded focus:ring-2 focus:ring-orange-500 focus:outline-none" />
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-orange-600">2</span> Payment method
              </h2>
              <div className="border rounded-md p-4 ml-6 bg-yellow-50">
                <p className="text-sm text-gray-800">This is a prototype. No real payment is required.</p>
              </div>
            </div>
            
            <div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-orange-600">3</span> Review items and delivery
              </h2>
              <div className="border rounded-md p-4 ml-6 space-y-4">
                {cart.items.map(item => (
                   <div key={item.product.id} className="flex gap-4 text-sm border-b pb-4 last:border-b-0 last:pb-0">
                      <img src={item.product.image_url} alt={item.product.name} className="w-16 h-16 object-contain" />
                      <div>
                        <div className="font-bold line-clamp-2">{item.product.name}</div>
                        <div className="text-[#B12704] font-bold mt-1">£{item.product.price.toFixed(2)}</div>
                        <div className="text-gray-600 mt-1">Quantity: {item.quantity}</div>
                        <div className="text-gray-600 mt-1 text-xs">Sold by: SmartCart</div>
                      </div>
                   </div>
                ))}
              </div>
            </div>
          </form>
        </div>

        {/* Right: Summary Box */}
        <div className="md:w-1/3">
          <div className="border rounded p-4 sticky top-6 shadow-sm bg-gray-50">
            <button 
              type="submit" 
              form="checkout-form"
              disabled={loading}
              className={`w-full py-2.5 rounded-lg font-medium shadow-sm mb-4 ${loading ? 'bg-gray-400' : 'bg-[#FFD814] hover:bg-[#F7CA00] border-[#FCD200] border'}`}
            >
              {loading ? 'Processing...' : 'Place your order'}
            </button>
            <div className="text-center text-xs text-gray-500 mb-4 border-b pb-4">
              By placing your order, you agree to SmartCart's privacy notice and conditions of use.
            </div>
            
            <h3 className="font-bold mb-2">Order Summary</h3>
            <div className="text-sm space-y-1 mb-4 border-b pb-4">
              <div className="flex justify-between">
                <span>Items:</span>
                <span>£{cart.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Postage & Packing:</span>
                <span>£0.00</span>
              </div>
              {cart.discount > 0 && (
                <div className="flex justify-between text-[#B12704]">
                  <span>Bundle Promotion:</span>
                  <span>-£{cart.discount.toFixed(2)}</span>
                </div>
              )}
            </div>
            <div className="flex justify-between font-bold text-[#B12704] text-lg">
              <span>Order Total:</span>
              <span>£{cart.final_total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
