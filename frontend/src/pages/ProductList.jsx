import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../api'

export default function ProductList() {
  const [products, setProducts] = useState([])
  const [filteredProducts, setFilteredProducts] = useState([])
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q')

  // Filter States
  const [priceRange, setPriceRange] = useState({ min: 0, max: Infinity })
  const [minRating, setMinRating] = useState(0)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const endpoint = query ? `/products/search?q=${encodeURIComponent(query)}` : '/products?limit=40'
        const res = await api.get(endpoint)
        // Add a deterministic fake rating to each product so filters have data to work with
        const withRatings = res.data.map(p => ({
          ...p,
          rating: (p.id % 3) + 3, // gives a deterministic rating of 3, 4, or 5
          reviewCount: (p.id * 7) % 500 + 10
        }))
        setProducts(withRatings)
      } catch (err) {
        console.error(err)
      }
    }
    fetchProducts()
  }, [query])

  useEffect(() => {
    // Apply filters
    let result = products
    if (priceRange.min > 0 || priceRange.max < Infinity) {
      result = result.filter(p => p.price >= priceRange.min && p.price <= priceRange.max)
    }
    if (minRating > 0) {
      result = result.filter(p => p.rating >= minRating)
    }
    setFilteredProducts(result)
  }, [products, priceRange, minRating])

  return (
    <div className="bg-white min-h-screen pb-20">
      <div className="border-b shadow-sm">
        <div className="max-w-screen-2xl mx-auto px-4 py-2 text-sm text-gray-700 shadow-sm font-medium">
          {filteredProducts.length} results for "{query || 'all departments'}"
        </div>
      </div>
      
      <div className="max-w-screen-2xl mx-auto px-4 py-4 flex gap-6">
        {/* Amazon style left sidebar mock */}
        <div className="hidden md:block w-64 flex-shrink-0 border-r pr-4">
          <h3 className="font-bold mb-2">Department</h3>
          <ul className="text-sm space-y-1 text-gray-800 mb-6">
            <li className="hover:text-orange-600 cursor-pointer">&lt; Any Department</li>
            <li className="font-bold">Home & Kitchen</li>
          </ul>
          
          <h3 className="font-bold mb-2">Customer Review</h3>
          <ul className="text-sm space-y-1 mb-6">
            {[4, 3, 2, 1].map(stars => (
              <li 
                key={stars}
                onClick={() => setMinRating(stars)}
                className={`flex items-center gap-1 cursor-pointer hover:text-orange-600 ${minRating === stars ? 'font-bold' : ''}`}
              >
                 <span className="text-yellow-500">{'★'.repeat(stars)}{'☆'.repeat(5-stars)}</span> & Up
              </li>
            ))}
            {minRating > 0 && (
              <li onClick={() => setMinRating(0)} className="text-blue-600 hover:underline cursor-pointer mt-1">Clear rating filter</li>
            )}
          </ul>

          <h3 className="font-bold mb-2">Price</h3>
          <ul className="text-sm space-y-1 text-gray-800">
            <li 
              onClick={() => setPriceRange({ min: 0, max: 10 })}
              className={`hover:text-orange-600 cursor-pointer ${priceRange.min === 0 && priceRange.max === 10 ? 'font-bold text-black' : ''}`}
            >Under £10</li>
            <li 
              onClick={() => setPriceRange({ min: 10, max: 20 })}
              className={`hover:text-orange-600 cursor-pointer ${priceRange.min === 10 && priceRange.max === 20 ? 'font-bold text-black' : ''}`}
            >£10 - £20</li>
            <li 
              onClick={() => setPriceRange({ min: 20, max: 50 })}
              className={`hover:text-orange-600 cursor-pointer ${priceRange.min === 20 && priceRange.max === 50 ? 'font-bold text-black' : ''}`}
            >£20 - £50</li>
            <li 
              onClick={() => setPriceRange({ min: 50, max: Infinity })}
              className={`hover:text-orange-600 cursor-pointer ${priceRange.min === 50 && priceRange.max === Infinity ? 'font-bold text-black' : ''}`}
            >Over £50</li>
            {(priceRange.min > 0 || priceRange.max < Infinity) && (
              <li onClick={() => setPriceRange({ min: 0, max: Infinity })} className="text-blue-600 hover:underline cursor-pointer mt-1">Clear price filter</li>
            )}
          </ul>
        </div>

        {/* Results */}
        <div className="flex-1">
          {filteredProducts.length === 0 ? (
            <div className="py-8 text-center">
              <p className="text-gray-500 text-lg">No products found matching these filters.</p>
              <button 
                onClick={() => { setPriceRange({ min: 0, max: Infinity }); setMinRating(0); }}
                className="mt-4 text-blue-600 hover:underline"
              >
                Clear all filters
              </button>
            </div>
          ) : (
            <div className="flex flex-col space-y-4">
              {filteredProducts.map(p => (
                <div key={p.id} className="flex gap-6 border rounded-lg p-4 hover:shadow-sm transition-shadow bg-white items-center">
                  <div className="w-24 h-24 sm:w-32 sm:h-32 md:w-48 md:h-48 flex-shrink-0 flex items-center justify-center bg-gray-50 rounded p-2 overflow-hidden">
                    <Link to={`/products/${p.id}`} className="w-full h-full flex items-center justify-center">
                      <img src={p.image_url} alt={p.name} className="w-full h-full object-contain hover:scale-105 transition-transform" />
                    </Link>
                  </div>
                  
                  <div className="flex flex-col flex-1">
                    <Link to={`/products/${p.id}`}>
                      <h2 className="text-lg font-medium text-black hover:text-orange-600 line-clamp-2">{p.name}</h2>
                    </Link>
                    <div className="text-yellow-500 text-sm mt-1">
                      {'★'.repeat(p.rating)}{'☆'.repeat(5-p.rating)}
                      <span className="text-blue-600 hover:underline cursor-pointer ml-1">{p.reviewCount}</span>
                    </div>
                    
                    <div className="mt-2 text-2xl font-medium">
                      <span className="text-sm align-top">£</span>
                      <span className="">{Math.floor(p.price)}</span>
                      <span className="text-sm align-top">{(p.price % 1).toFixed(2).substring(1)}</span>
                    </div>
                    
                    <div className="text-xs text-gray-500 mt-1">Delivery by SmartCart</div>
                    <div className="text-sm text-gray-500 mt-2"><strong>Code:</strong> {p.stock_code}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
