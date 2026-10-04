import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../api'
import { useAuth } from '../context/AuthContext'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { fetchCartCount } = useAuth()
  const [product, setProduct] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [added, setAdded] = useState(false)
  
  // For Frequently Bought Together checkboxes
  const [selectedBundle, setSelectedBundle] = useState([])

  useEffect(() => {
    let isMounted = true

    Promise.all([
      api.get(`/products/${id}`),
      api.get(`/recommendations/${id}`)
    ])
      .then(([prodRes, recsRes]) => {
        if (!isMounted) return
        setProduct(prodRes.data)
        setRecommendations(recsRes.data)
        setAdded(false)

        // Only preselect items that belong to a single rule (main item + top rule's consequent)
        if (recsRes.data && recsRes.data.length > 0) {
          setSelectedBundle([prodRes.data.id, recsRes.data[0].product.id])
        } else {
          setSelectedBundle([prodRes.data.id])
        }
      })
      .catch((err) => {
        if (isMounted) console.error(err)
      })

    return () => {
      isMounted = false
    }
  }, [id])

  const addToCart = async (productIds) => {
    try {
      // Add all selected products to cart
      const promises = productIds.map(pid => 
        api.post('/cart/add', { product_id: pid, quantity: 1 })
      )
      await Promise.all(promises)
      setAdded(true)
      fetchCartCount()
      setTimeout(() => setAdded(false), 3000)
    } catch (err) {
      console.error(err)
    }
  }

  const buyNow = async () => {
    try {
      await api.post('/cart/add', { product_id: product.id, quantity: 1 })
      navigate('/checkout')
    } catch (err) {
      console.error(err)
    }
  }

  const toggleBundleItem = (pid) => {
    setSelectedBundle(prev => 
      prev.includes(pid) ? prev.filter(id => id !== pid) : [...prev, pid]
    )
  }

  if (!product) return <div className="text-center py-20 text-xl">Loading...</div>

  // Calculate bundle price
  const bundleItems = [product, ...recommendations.map(r => r.product)]
  const selectedBundleItems = bundleItems.filter(item => selectedBundle.includes(item.id))
  const bundleTotalPrice = selectedBundleItems.reduce((sum, item) => sum + item.price, 0)

  return (
    <div className="bg-white min-h-screen pb-20">
      {/* Category Nav */}
      <div className="bg-white border-b shadow-sm py-2 px-4 text-sm text-gray-600">
        Home & Kitchen &gt; Home Accessories &gt; Decorative Accessories
      </div>

      <div className="max-w-screen-xl mx-auto px-4 py-6 flex flex-col md:flex-row gap-8">
        
        {/* Left: Image */}
        <div className="md:w-5/12 flex justify-center md:sticky md:top-20 h-max mb-6 md:mb-0 w-full">
          <img src={product.image_url} alt={product.name} className="w-full max-h-[300px] md:max-h-[500px] object-contain bg-white" />
        </div>

        {/* Middle: Details */}
        <div className="md:w-5/12">
          <h1 className="text-2xl font-medium leading-tight mb-2">{product.name}</h1>
          <a href="#" className="text-sm text-blue-600 hover:underline hover:text-orange-600">Visit the SmartCart Store</a>
          
          <div className="flex items-center gap-4 mt-2 border-b pb-4">
             <div className="text-yellow-500 text-sm">★★★★☆ <span className="text-blue-600 ml-1">{(Math.random() * 1000).toFixed(0)} ratings</span></div>
          </div>

          <div className="mt-4">
            <div className="flex items-end gap-2">
              <span className="text-3xl font-medium text-[#B12704]">£{product.price.toFixed(2)}</span>
            </div>
            <p className="text-sm text-gray-500 mt-1">Free Returns</p>
            <p className="text-sm mt-2">All prices include VAT.</p>
          </div>

          <div className="mt-6">
            <h3 className="font-bold text-gray-900 mb-2">About this item</h3>
            <ul className="list-disc pl-5 text-sm space-y-2 text-gray-800">
              <li>{product.description}</li>
              <li>Stock Code: {product.stock_code}</li>
              <li>Perfect for your home or as a gift for loved ones.</li>
              <li>High-quality materials sourced responsibly.</li>
            </ul>
          </div>
        </div>

        {/* Right: Buy Box */}
        <div className="md:w-2/12">
          <div className="border rounded p-4 shadow-sm">
            <div className="text-2xl font-medium text-[#B12704] mb-2">£{product.price.toFixed(2)}</div>
            <p className="text-sm text-green-700 font-bold mb-4">In stock.</p>
            
            <div className="flex flex-col gap-2">
              <button 
                onClick={() => addToCart([product.id])}
                className="w-full bg-[#FFD814] hover:bg-[#F7CA00] border-[#FCD200] border rounded-full py-2 text-sm shadow-sm font-medium"
              >
                {added ? 'Added ✓' : 'Add to Cart'}
              </button>
              <button 
                onClick={buyNow}
                className="w-full bg-[#FFA41C] hover:bg-[#FA8900] border-[#FF8F00] border rounded-full py-2 text-sm shadow-sm font-medium"
              >
                Buy Now
              </button>
            </div>
            
            <div className="mt-4 text-xs text-gray-500 flex flex-col gap-1">
              <div className="flex justify-between"><span>Dispatches from</span> <span>SmartCart</span></div>
              <div className="flex justify-between"><span>Sold by</span> <span>SmartCart</span></div>
              <div className="flex justify-between"><span>Returns</span> <span className="text-blue-600">Returnable within 30 days</span></div>
            </div>
          </div>
        </div>
      </div>

      <hr className="my-8" />

      {/* Apriori Recommendations styled as "Frequently Bought Together" */}
      {recommendations.length > 0 && (
        <div className="max-w-screen-xl mx-auto px-4 mt-8">
          <h2 className="text-xl font-bold text-[#c60] mb-4">Frequently bought together</h2>
          
          <div className="flex flex-col md:flex-row gap-8 items-start">
            
            {/* Images Row */}
            <div className="flex items-center gap-4 flex-wrap">
               {/* Main Product */}
               <div className="relative">
                  <img src={product.image_url} alt={product.name} className="w-32 h-32 object-contain" />
               </div>
               
               {/* Recommended Products */}
               {recommendations.slice(0, 2).map((rec, idx) => (
                 <React.Fragment key={idx}>
                   <div className="text-3xl text-gray-400 font-light">+</div>
                   <Link to={`/products/${rec.product.id}`}>
                     <img src={rec.product.image_url} alt={rec.product.name} className="w-32 h-32 object-contain" />
                   </Link>
                 </React.Fragment>
               ))}
            </div>

            {/* Total Price and Buy Bundle */}
            <div className="flex flex-col border p-4 rounded bg-gray-50 flex-1 max-w-sm shadow-sm">
               <div className="text-lg mb-2">
                 Total price: <span className="font-bold text-[#B12704]">£{bundleTotalPrice.toFixed(2)}</span>
               </div>
               <button 
                 onClick={() => addToCart(selectedBundle)}
                 className="bg-[#FFD814] hover:bg-[#F7CA00] border-[#FCD200] border rounded-full py-2 px-4 shadow-sm text-sm font-medium whitespace-nowrap mb-4"
               >
                 Add selected to Cart
               </button>
               
               {/* Confidence metric chip to show Apriori powers it */}
               <div className="text-xs text-gray-500 mb-2 flex items-center">
                 <span className="mr-1">Powered by Apriori </span> 
                 <span className="inline-block bg-blue-100 text-blue-800 text-[10px] px-1.5 py-0.5 rounded">Rules</span>
               </div>
            </div>
          </div>
          
          {/* Checkboxes for bundle selection */}
          <div className="mt-6 flex flex-col gap-2 text-sm">
             <label className="flex items-start gap-2 cursor-pointer">
               <input type="checkbox" checked={selectedBundle.includes(product.id)} onChange={() => toggleBundleItem(product.id)} className="mt-1" />
               <span><strong>This item:</strong> {product.name} - <span className="text-[#B12704]">£{product.price.toFixed(2)}</span></span>
             </label>
             
             {recommendations.slice(0, 2).map((rec, idx) => (
               <label key={idx} className="flex items-start gap-2 cursor-pointer">
                 <input type="checkbox" checked={selectedBundle.includes(rec.product.id)} onChange={() => toggleBundleItem(rec.product.id)} className="mt-1" />
                 <span>
                   <Link to={`/products/${rec.product.id}`} className="text-blue-600 hover:underline">{rec.product.name}</Link> - <span className="text-[#B12704]">£{rec.product.price.toFixed(2)}</span>
                   <span className="ml-2 inline-flex items-center rounded-md bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                     {rec.lift.toFixed(1)}x Lift
                   </span>
                 </span>
               </label>
             ))}
          </div>

        </div>
      )}
    </div>
  )
}
