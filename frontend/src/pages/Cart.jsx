import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../config'
import { useAuth } from '../context/AuthContext'

export default function Cart() {
  const navigate = useNavigate()
  const { fetchCartCount } = useAuth()
  const [cart, setCart] = useState(null)
  const [cartRecs, setCartRecs] = useState([])

  const fetchCart = async () => {
    try {
      const res = await axios.get(`${API_URL}/cart/`)
      setCart(res.data)
      
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
    if (newQuantity < 1) return removeItem(productId)
    try {
      await axios.put(`${API_URL}/cart/update`, { product_id: productId, quantity: newQuantity })
      fetchCart()
      fetchCartCount()
    } catch (err) {
      console.error(err)
    }
  }

  const removeItem = async (productId) => {
    try {
      await axios.delete(`${API_URL}/cart/remove/${productId}`)
      fetchCart()
      fetchCartCount()
    } catch (err) {
      console.error(err)
    }
  }

  const addToCart = async (productId) => {
    try {
      await axios.post(`${API_URL}/cart/add`, { product_id: productId, quantity: 1 })
      fetchCart()
      fetchCartCount()
    } catch (err) {
      console.error(err)
    }
  }

  if (!cart) return <div className="text-center py-20">Loading...</div>

  const totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <div className="bg-gray-100 min-h-screen pb-10 pt-6">
      <div className="max-w-screen-xl mx-auto px-4 flex flex-col lg:flex-row gap-6">
        
        {/* Left Side: Cart Items */}
        <div className="lg:w-3/4 flex flex-col gap-6">
          <div className="bg-white p-6 shadow-sm">
            <h1 className="text-3xl font-normal mb-1">Shopping Cart</h1>
            {cart.items.length > 0 && <div className="text-right text-sm text-gray-500 mb-2">Price</div>}
            <hr className="mb-4" />

            {cart.items.length === 0 ? (
              <div className="py-8">
                <p className="text-xl">Your SmartCart Cart is empty.</p>
                <Link to="/products" className="text-blue-600 hover:underline hover:text-orange-600 mt-2 inline-block">Shop today's deals</Link>
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                {cart.items.map(item => (
                  <div key={item.product.id} className="flex gap-4 border-b pb-4">
                    <div className="w-24 sm:w-40 flex-shrink-0 flex items-start justify-center">
                      <Link to={`/products/${item.product.id}`} className="w-full">
                        <img src={item.product.image_url} alt={item.product.name} className="w-full max-h-[160px] object-contain" />
                      </Link>
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex justify-between">
                        <Link to={`/products/${item.product.id}`} className="text-lg font-medium text-black hover:text-orange-600 line-clamp-2">
                          {item.product.name}
                        </Link>
                        <div className="text-lg font-bold">£{item.product.price.toFixed(2)}</div>
                      </div>
                      <div className="text-sm text-green-700 mt-1">In stock</div>
                      <div className="text-xs text-gray-500 mt-1">Eligible for FREE Delivery</div>
                      <div className="text-xs text-gray-500 mt-1"><strong>Stock Code:</strong> {item.product.stock_code}</div>
                      
                      <div className="flex items-center gap-4 mt-4">
                        <div className="bg-gray-100 border rounded-lg flex items-center shadow-sm">
                          <button onClick={() => updateQuantity(item.product.id, item.quantity - 1)} className="px-3 py-1 hover:bg-gray-200 text-lg rounded-l-lg">-</button>
                          <span className="px-4 bg-white border-x py-1">{item.quantity}</span>
                          <button onClick={() => updateQuantity(item.product.id, item.quantity + 1)} className="px-3 py-1 hover:bg-gray-200 text-lg rounded-r-lg">+</button>
                        </div>
                        <div className="text-gray-300">|</div>
                        <button onClick={() => removeItem(item.product.id)} className="text-blue-600 text-sm hover:underline">Delete</button>
                        <div className="text-gray-300">|</div>
                        <button className="text-blue-600 text-sm hover:underline">Save for later</button>
                      </div>
                    </div>
                  </div>
                ))}
                
                <div className="text-right text-lg font-medium mt-2">
                  Subtotal ({totalItems} items): <span className="font-bold">£{cart.subtotal.toFixed(2)}</span>
                </div>
              </div>
            )}
          </div>

          {/* Cart Recommendations section */}
          {cartRecs.length > 0 && (
            <div className="bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold mb-4">Customers who bought items in your cart also bought</h2>
              <div className="flex gap-4 overflow-x-auto pb-4">
                {cartRecs.map((rec, idx) => (
                  <div key={idx} className="w-48 flex-shrink-0 flex flex-col items-start gap-2 border p-2 hover:shadow-sm">
                    <Link to={`/products/${rec.product.id}`}>
                      <img src={rec.product.image_url} className="w-full h-32 object-contain" alt={rec.product.name} />
                    </Link>
                    <Link to={`/products/${rec.product.id}`} className="text-sm text-blue-600 hover:underline hover:text-orange-600 line-clamp-2">
                      {rec.product.name}
                    </Link>
                    <div className="text-[#B12704] font-bold">£{rec.product.price.toFixed(2)}</div>
                    
                    <button 
                      onClick={() => addToCart(rec.product.id)} 
                      className="mt-auto bg-[#FFD814] hover:bg-[#F7CA00] border-[#FCD200] border rounded-full py-1 px-4 text-xs shadow-sm font-medium w-full"
                    >
                      Add to Cart
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Checkout Box */}
        {cart.items.length > 0 && (
          <div className="lg:w-1/4">
            <div className="bg-white p-4 shadow-sm">
              {cart.discount > 0 && (
                <div className="mb-4 text-sm text-green-700 flex items-start gap-2">
                   <div className="bg-green-100 p-1 rounded-full"><span className="text-xs">✓</span></div>
                   <div>
                      Your order qualifies for a <strong>{cart.applied_bundle_tier} bundle discount!</strong>
                      <br/><span className="text-gray-500 text-xs">{cart.savings_reason}</span>
                   </div>
                </div>
              )}
              
              <div className="text-lg font-medium mb-4">
                Subtotal ({totalItems} items): <span className="font-bold">£{cart.subtotal.toFixed(2)}</span>
                {cart.discount > 0 && (
                  <div className="text-sm text-[#B12704] mt-1">
                    Discount applied: -£{cart.discount.toFixed(2)}
                  </div>
                )}
                {cart.discount > 0 && (
                  <div className="text-lg font-bold mt-1">
                    Total: £{cart.final_total.toFixed(2)}
                  </div>
                )}
              </div>

              <button 
                onClick={() => navigate('/checkout')}
                className="w-full bg-[#FFD814] hover:bg-[#F7CA00] border-[#FCD200] border rounded-full py-2 shadow-sm font-medium mb-4"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
