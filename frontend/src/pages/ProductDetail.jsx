import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../config'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [added, setAdded] = useState(false)

  useEffect(() => {
    // Fetch product details
    axios.get(`${API_URL}/products/${id}`)
      .then(res => {
        setProduct(res.data)
        setAdded(false)
      })
      .catch(err => console.error(err))

    // Fetch recommendations based on Apriori
    axios.get(`${API_URL}/recommendations/${id}`)
      .then(res => setRecommendations(res.data))
      .catch(err => console.error(err))
  }, [id])

  const addToCart = async (productId) => {
    try {
      await axios.post(`${API_URL}/cart/add`, { product_id: productId, quantity: 1 })
      setAdded(true)
      setTimeout(() => setAdded(false), 3000)
    } catch (err) {
      console.error(err)
    }
  }

  if (!product) return <div className="text-center py-20 text-xl text-gray-500">Loading...</div>

  return (
    <div className="max-w-5xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden flex flex-col md:flex-row mb-12">
        <div className="md:w-1/2 h-96 relative">
          <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
        </div>
        <div className="md:w-1/2 p-8 flex flex-col justify-center">
          <p className="text-sm text-gray-400 mb-2">Stock Code: {product.stock_code}</p>
          <h1 className="text-3xl font-bold mb-4">{product.name}</h1>
          <p className="text-gray-600 mb-6">{product.description}</p>
          <div className="text-4xl font-extrabold text-indigo-600 mb-8">£{product.price.toFixed(2)}</div>
          <button 
            onClick={() => addToCart(product.id)}
            className={`w-full py-4 rounded-xl font-bold text-lg transition-colors ${added ? 'bg-green-500 text-white' : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg'}`}
          >
            {added ? 'Added to Cart ✓' : 'Add to Cart'}
          </button>
        </div>
      </div>

      {recommendations.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-6">Frequently Bought Together</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="bg-white border rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex gap-4">
                  <img src={rec.product.image} alt={rec.product.name} className="w-24 h-24 object-cover rounded-lg" />
                  <div>
                    <h3 className="font-semibold text-gray-800 line-clamp-2" title={rec.product.name}>{rec.product.name}</h3>
                    <p className="text-indigo-600 font-bold mb-2">£{rec.product.price.toFixed(2)}</p>
                    <button 
                      onClick={() => addToCart(rec.product.id)}
                      className="bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm font-semibold py-1 px-3 rounded-lg"
                    >
                      Add to Bundle
                    </button>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-xs text-gray-500 font-medium mb-1">Apriori Recommendation Metrics:</p>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-blue-50 text-blue-700 p-1 rounded text-center">
                      <span className="block font-bold">{(rec.confidence * 100).toFixed(0)}%</span> Confidence
                    </div>
                    <div className="bg-purple-50 text-purple-700 p-1 rounded text-center">
                      <span className="block font-bold">{rec.lift}x</span> Lift
                    </div>
                    <div className="bg-green-50 text-green-700 p-1 rounded text-center">
                      <span className="block font-bold">{(rec.support * 100).toFixed(1)}%</span> Support
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
