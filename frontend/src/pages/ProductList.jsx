import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../config'

export default function ProductList() {
  const [products, setProducts] = useState([])
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q')

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const endpoint = query ? `/products/search?q=${query}` : '/products'
        const res = await axios.get(`${API_URL}${endpoint}`)
        setProducts(res.data)
      } catch (err) {
        console.error(err)
      }
    }
    fetchProducts()
  }, [query])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">
        {query ? `Search Results for "${query}"` : 'All Products'}
      </h1>
      
      {products.length === 0 ? (
        <p className="text-gray-500 text-lg">No products found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map(p => (
            <Link to={`/products/${p.id}`} key={p.id} className="bg-white rounded-xl shadow hover:shadow-xl transition-shadow overflow-hidden group">
              <div className="h-56 overflow-hidden relative">
                <img src={p.image_url} alt={p.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-400 mb-1">Code: {p.stock_code}</p>
                <h3 className="font-semibold text-lg line-clamp-2 mb-2" title={p.name}>{p.name}</h3>
                <p className="text-indigo-600 font-bold text-xl">£{p.price.toFixed(2)}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
