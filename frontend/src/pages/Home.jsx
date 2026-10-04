import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../config'

export default function Home() {
  const [products, setProducts] = useState([])

  useEffect(() => {
    // Increase limit to list maximum products on home page
    axios.get(`${API_URL}/products?limit=40`)
      .then(res => setProducts(res.data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div className="bg-gray-100 min-h-screen pb-10">
      {/* Hero Banner - Amazon style gradient */}
      <div className="bg-gradient-to-b from-blue-400 to-gray-100 h-64 w-full relative mb-12">
        <div className="absolute bottom-0 w-full px-4 transform translate-y-1/2">
          <div className="bg-white p-4 max-w-7xl mx-auto text-center text-sm shadow-sm">
             You are on SmartCart.com. You can also shop on SmartCart UK for millions of products with fast local delivery.
          </div>
        </div>
      </div>

      <div className="max-w-screen-2xl mx-auto px-4 mt-8">
        <h2 className="text-2xl font-bold mb-4 ml-2">Discover products related to your data</h2>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map(p => (
            <div key={p.id} className="bg-white p-4 flex flex-col items-center justify-between z-10 hover:shadow-lg transition-shadow border border-gray-200 cursor-pointer h-full">
              <h3 className="font-bold text-lg mb-2 self-start line-clamp-1">{p.name}</h3>
              <div className="w-full h-48 flex items-center justify-center my-4 overflow-hidden relative">
                 <Link to={`/products/${p.id}`} className="w-full h-full flex items-center justify-center">
                   <img src={p.image_url} alt={p.name} className="w-full h-full object-contain hover:scale-105 transition-transform duration-300" />
                 </Link>
              </div>
              <div className="self-start w-full">
                 <div className="text-yellow-500 text-sm mb-1">★★★★☆ <span className="text-blue-600 hover:underline cursor-pointer">{Math.floor(Math.random() * 500) + 10}</span></div>
                 <div className="text-xl">
                   <span className="text-sm align-top">£</span>
                   <span className="text-2xl font-semibold">{Math.floor(p.price)}</span>
                   <span className="text-sm align-top">{(p.price % 1).toFixed(2).substring(1)}</span>
                 </div>
                 <Link to={`/products/${p.id}`} className="text-sm text-blue-600 hover:underline hover:text-orange-600 mt-2 block">
                   See more
                 </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
