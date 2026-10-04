import React, { useState, useEffect } from 'react';
import { Link, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Users, Package, ShoppingCart, LayoutDashboard } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

import AdminProducts from './admin/AdminProducts';
import AdminOrders from './admin/AdminOrders';
import AdminUsers from './admin/AdminUsers';

const AdminLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/');
    }
  }, [user, navigate]);

  if (!user || !user.is_admin) return null;

  const navItems = [

    { name: 'Dashboard', path: '/admin', icon: LayoutDashboard },
    { name: 'Products', path: '/admin/products', icon: Package },
    { name: 'Orders', path: '/admin/orders', icon: ShoppingCart },
    { name: 'Users', path: '/admin/users', icon: Users },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-md">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-800">Admin Panel</h2>
        </div>
        <nav className="mt-4">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center px-6 py-3 text-gray-600 hover:bg-gray-50 hover:text-[#f90] transition-colors ${
                location.pathname === item.path ? 'bg-gray-50 text-[#f90] border-r-4 border-[#f90]' : ''
              }`}
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-8">
          <Routes>
            <Route path="/" element={<AdminDashboard />} />
            <Route path="/products" element={<AdminProducts />} />
            <Route path="/orders" element={<AdminOrders />} />
            <Route path="/users" element={<AdminUsers />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

const AdminDashboard = () => {
  const [stats, setStats] = useState({ users: 0, products: 0, orders: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [usersRes, productsRes, ordersRes] = await Promise.all([
          axios.get('http://127.0.0.1:8000/api/admin/users'),
          axios.get('http://127.0.0.1:8000/api/products/'),
          axios.get('http://127.0.0.1:8000/api/admin/orders')
        ]);
        setStats({
          users: usersRes.data.length,
          products: productsRes.data.length,
          orders: ordersRes.data.length
        });
      } catch (err) {
        console.error('Failed to fetch stats', err);
      }
    };
    fetchStats();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Dashboard Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm uppercase tracking-wide">Total Users</p>
            <h3 className="text-3xl font-bold mt-1 text-gray-800">{stats.users}</h3>
          </div>
          <div className="p-3 bg-blue-100 rounded-full text-blue-600">
            <Users size={24} />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm uppercase tracking-wide">Total Products</p>
            <h3 className="text-3xl font-bold mt-1 text-gray-800">{stats.products}</h3>
          </div>
          <div className="p-3 bg-green-100 rounded-full text-green-600">
            <Package size={24} />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm uppercase tracking-wide">Total Orders</p>
            <h3 className="text-3xl font-bold mt-1 text-gray-800">{stats.orders}</h3>
          </div>
          <div className="p-3 bg-purple-100 rounded-full text-purple-600">
            <ShoppingCart size={24} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;
