import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../config'
import { useAuth } from '../context/AuthContext'
import {
  Package, PackageCheck, Truck, RotateCcw, AlertCircle,
  ChevronDown, ChevronUp, ArrowLeft, Clock
} from 'lucide-react'

const STATUS_CONFIG = {
  Processing: {
    icon: <Clock className="w-5 h-5" />,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    badge: 'bg-blue-100 text-blue-700',
    label: 'Processing',
    desc: 'Your order is being prepared.',
  },
  Shipped: {
    icon: <Truck className="w-5 h-5" />,
    color: 'text-orange-600',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    badge: 'bg-orange-100 text-orange-700',
    label: 'Shipped',
    desc: 'Your order is on its way.',
  },
  Delivered: {
    icon: <PackageCheck className="w-5 h-5" />,
    color: 'text-green-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
    badge: 'bg-green-100 text-green-700',
    label: 'Delivered',
    desc: 'Your order has been delivered.',
  },
  'Return Requested': {
    icon: <RotateCcw className="w-5 h-5" />,
    color: 'text-purple-600',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    badge: 'bg-purple-100 text-purple-700',
    label: 'Return Requested',
    desc: 'Your return request is being processed.',
  },
  Returned: {
    icon: <RotateCcw className="w-5 h-5" />,
    color: 'text-gray-600',
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    badge: 'bg-gray-100 text-gray-700',
    label: 'Returned',
    desc: 'Your return has been completed.',
  },
}

function OrderCard({ order, onReturn }) {
  const [expanded, setExpanded] = useState(false)
  const [returning, setReturning] = useState(false)
  const [returnMsg, setReturnMsg] = useState('')

  const status = STATUS_CONFIG[order.status] || STATUS_CONFIG['Processing']
  const canReturn = order.status === 'Delivered'
  const orderId = `#ORD-${order.id.toString().padStart(6, '0')}`

  const handleReturn = async () => {
    if (!window.confirm(`Request a return for order ${orderId}?`)) return
    setReturning(true)
    try {
      const res = await axios.post(`${API_URL}/cart/orders/${order.id}/return`, {
        order_id: order.id,
        reason: 'Customer requested return',
      })
      setReturnMsg(res.data.message)
      onReturn(order.id, 'Return Requested')
    } catch (err) {
      setReturnMsg(err.response?.data?.detail || 'Return request failed')
    } finally {
      setReturning(false)
    }
  }

  const formattedDate = order.created_at
    ? new Date(order.created_at).toLocaleDateString('en-GB', {
        day: 'numeric', month: 'long', year: 'numeric',
      })
    : 'Date unavailable'

  return (
    <div className={`border rounded-lg overflow-hidden ${status.border} shadow-sm`}>
      {/* Order Header */}
      <div className={`${status.bg} px-5 py-3 flex flex-wrap gap-4 items-center justify-between text-sm`}>
        <div className="flex flex-wrap gap-6">
          <div>
            <div className="text-gray-500 text-xs uppercase tracking-wide font-medium">Order Placed</div>
            <div className="font-semibold text-gray-800">{formattedDate}</div>
          </div>
          <div>
            <div className="text-gray-500 text-xs uppercase tracking-wide font-medium">Total</div>
            <div className="font-semibold text-gray-800">£{order.total.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-gray-500 text-xs uppercase tracking-wide font-medium">Ship to</div>
            <div className="font-semibold text-gray-800">{order.customer_name}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-gray-500 text-xs">{orderId}</div>
          <span className={`inline-flex items-center gap-1.5 mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${status.badge}`}>
            <span className={status.color}>{status.icon}</span>
            {status.label}
          </span>
        </div>
      </div>

      {/* Order Body */}
      <div className="bg-white px-5 py-4">
        <div className={`flex items-center gap-2 mb-3 text-sm ${status.color} font-medium`}>
          {status.icon}
          <span>{status.desc}</span>
        </div>

        {/* Items preview */}
        <div className="flex gap-3 flex-wrap mb-3">
          {order.items.slice(0, expanded ? undefined : 3).map((item) => (
            <div key={item.product.id} className="flex items-center gap-3 border rounded-md px-3 py-2 bg-gray-50 min-w-0">
              <img
                src={item.product.image_url || 'https://via.placeholder.com/48'}
                alt={item.product.name}
                className="w-12 h-12 object-contain flex-shrink-0"
              />
              <div className="min-w-0">
                <div className="text-sm font-medium text-gray-800 line-clamp-2 max-w-xs">{item.product.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  Qty: {item.quantity} · £{item.price.toFixed(2)} each
                </div>
              </div>
            </div>
          ))}
        </div>

        {order.items.length > 3 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-[#0066c0] hover:text-[#c45500] hover:underline flex items-center gap-1 mb-3"
          >
            {expanded ? (
              <><ChevronUp className="w-4 h-4" /> Show less</>
            ) : (
              <><ChevronDown className="w-4 h-4" /> Show {order.items.length - 3} more item{order.items.length - 3 > 1 ? 's' : ''}</>
            )}
          </button>
        )}

        {/* Discount info */}
        {order.discount > 0 && (
          <div className="text-xs text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-1.5 mb-3 inline-block">
            🎉 Bundle discount saved you £{order.discount.toFixed(2)}
          </div>
        )}

        {/* Delivery address */}
        <div className="text-xs text-gray-500 border-t pt-3 mt-3">
          <span className="font-semibold text-gray-700">Delivery address: </span>
          {order.address}, {order.city}, {order.postal_code}
        </div>

        {/* Return message */}
        {returnMsg && (
          <div className="mt-3 p-2 bg-purple-50 border border-purple-200 rounded-md text-purple-700 text-sm">
            ✓ {returnMsg}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 mt-4 flex-wrap">
          <Link
            to="/products"
            className="px-4 py-1.5 border border-gray-300 rounded-full text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Buy again
          </Link>
          {canReturn && (
            <button
              onClick={handleReturn}
              disabled={returning}
              className="px-4 py-1.5 border border-orange-400 text-orange-700 rounded-full text-sm font-medium hover:bg-orange-50 transition-colors flex items-center gap-1.5 disabled:opacity-60"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              {returning ? 'Requesting...' : 'Return items'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Orders() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filterStatus, setFilterStatus] = useState('All')

  useEffect(() => {
    if (!user) {
      navigate('/login', {
        state: { from: '/orders', message: 'Please sign in to view your orders.' },
      })
      return
    }
    fetchOrders()
  }, [user, navigate])

  const fetchOrders = async () => {
    setLoading(true)
    setError('')
    try {
      const params = user?.id ? { user_id: user.id } : {}
      const res = await axios.get(`${API_URL}/cart/orders`, { params })
      setOrders(res.data)
    } catch (err) {
      setError('Failed to load orders. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReturn = (orderId, newStatus) => {
    setOrders((prev) =>
      prev.map((o) => (o.id === orderId ? { ...o, status: newStatus } : o))
    )
  }

  const statuses = ['All', 'Processing', 'Shipped', 'Delivered', 'Return Requested', 'Returned']
  const filtered = filterStatus === 'All' ? orders : orders.filter((o) => o.status === filterStatus)

  return (
    <div className="min-h-screen bg-[#f3f3f3]">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => navigate(-1)}
            className="text-[#0066c0] hover:text-[#c45500] hover:underline text-sm flex items-center gap-1"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </button>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Package className="w-6 h-6" />
            Your Orders
          </h1>
          {user && (
            <span className="text-sm text-gray-500">({user.username})</span>
          )}
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 flex-wrap mb-6">
          {statuses.map((s) => (
            <button
              key={s}
              onClick={() => setFilterStatus(s)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                filterStatus === s
                  ? 'bg-[#131921] text-white border-[#131921]'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-gray-500'
              }`}
            >
              {s}
              {s !== 'All' && orders.filter((o) => o.status === s).length > 0 && (
                <span className="ml-1.5 text-xs">
                  ({orders.filter((o) => o.status === s).length})
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <svg className="animate-spin h-8 w-8 text-[#f90]" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            <p className="text-gray-500">Loading your orders...</p>
          </div>
        ) : error ? (
          <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p>{error}</p>
              <button onClick={fetchOrders} className="text-sm underline mt-1">Try again</button>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-lg border border-gray-200">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              {filterStatus === 'All' ? 'No orders yet' : `No ${filterStatus} orders`}
            </h2>
            <p className="text-gray-500 mb-6">
              {filterStatus === 'All'
                ? "You haven't placed any orders yet."
                : `You have no orders with status "${filterStatus}".`}
            </p>
            <Link
              to="/products"
              className="inline-block bg-[#FFD814] hover:bg-[#F7CA00] border border-[#FCD200] rounded-full py-2 px-6 font-medium text-sm shadow-sm"
            >
              Start shopping
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              Showing {filtered.length} order{filtered.length !== 1 ? 's' : ''}
              {filterStatus !== 'All' ? ` · ${filterStatus}` : ''}
            </p>
            {filtered.map((order) => (
              <OrderCard key={order.id} order={order} onReturn={handleReturn} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
