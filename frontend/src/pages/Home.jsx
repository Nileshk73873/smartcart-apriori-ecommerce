import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../config'

export default function Home() {
  const [products, setProducts] = useState([])

  useEffect(() => {
    axios.get(`${API_URL}/products?limit=8`)
      .then(res => setProducts(res.data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div>
      <section className="bg-indigo-600 text-white rounded-2xl p-12 text-center mb-12 shadow-lg">
        <h1 className="text-5xl font-extrabold mb-4">Shop Smarter with SmartCart</h1>
        <p className="text-xl mb-8">Discover products frequently bought together and save with our smart bundles.</p>
        <Link to="/products" className="bg-white text-indigo-600 px-8 py-3 rounded-full font-bold text-lg hover:bg-gray-100 transition-colors">
          Start Shopping
        </Link>
      </section>

      <section>
        <h2 className="text-3xl font-bold mb-6">Featured Products</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          {products.map(p => (
            <Link to={`/products/${p.id}`} key={p.id} className="bg-white rounded-xl shadow hover:shadow-xl transition-shadow overflow-hidden group">
              <div className="h-48 overflow-hidden relative">
                <img src={p.image_url} alt={p.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-lg line-clamp-2 mb-2" title={p.name}>{p.name}</h3>
                <p className="text-indigo-600 font-bold text-xl">£{p.price.toFixed(2)}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
