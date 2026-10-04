import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2 } from 'lucide-react';

const AdminProducts = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [currentProduct, setCurrentProduct] = useState({
    stock_code: '', name: '', price: 0, description: '', image_url: ''
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/products/?limit=100');
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (currentProduct.id) {
        // Update
        await axios.put(`http://127.0.0.1:8000/api/admin/products/${currentProduct.id}`, currentProduct);
      } else {
        // Create
        await axios.post('http://127.0.0.1:8000/api/admin/products', currentProduct);
      }
      setIsEditing(false);
      setCurrentProduct({ stock_code: '', name: '', price: 0, description: '', image_url: '' });
      fetchProducts();
    } catch (err) {
      console.error('Error saving product', err);
      alert('Failed to save product');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await axios.delete(`http://127.0.0.1:8000/api/admin/products/${id}`);
        fetchProducts();
      } catch (err) {
        console.error('Error deleting product', err);
      }
    }
  };

  const editProduct = (product) => {
    setCurrentProduct(product);
    setIsEditing(true);
  };

  const addNew = () => {
    setCurrentProduct({ stock_code: '', name: '', price: 0, description: '', image_url: '' });
    setIsEditing(true);
  };

  if (loading) return <div className="p-4 text-center">Loading products...</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Manage Products</h2>
        <button 
          onClick={addNew}
          className="flex items-center bg-[#f90] hover:bg-[#e88a00] text-white px-4 py-2 rounded-md font-medium transition-colors"
        >
          <Plus size={18} className="mr-2" /> Add Product
        </button>
      </div>

      {isEditing && (
        <div className="mb-8 bg-gray-50 p-6 rounded-lg border border-gray-200">
          <h3 className="text-xl font-semibold mb-4">{currentProduct.id ? 'Edit Product' : 'New Product'}</h3>
          <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Stock Code</label>
              <input type="text" required value={currentProduct.stock_code} onChange={e => setCurrentProduct({...currentProduct, stock_code: e.target.value})} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-[#f90] focus:border-[#f90]" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input type="text" required value={currentProduct.name} onChange={e => setCurrentProduct({...currentProduct, name: e.target.value})} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-[#f90] focus:border-[#f90]" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Price (£)</label>
              <input type="number" step="0.01" required value={currentProduct.price} onChange={e => setCurrentProduct({...currentProduct, price: parseFloat(e.target.value)})} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-[#f90] focus:border-[#f90]" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Image URL</label>
              <input type="text" value={currentProduct.image_url || ''} onChange={e => setCurrentProduct({...currentProduct, image_url: e.target.value})} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-[#f90] focus:border-[#f90]" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea value={currentProduct.description || ''} onChange={e => setCurrentProduct({...currentProduct, description: e.target.value})} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-[#f90] focus:border-[#f90]"></textarea>
            </div>
            <div className="md:col-span-2 flex justify-end space-x-3 mt-4">
              <button type="button" onClick={() => setIsEditing(false)} className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50">Cancel</button>
              <button type="submit" className="px-4 py-2 border border-transparent rounded-md text-white bg-blue-600 hover:bg-blue-700">Save</button>
            </div>
          </form>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product) => (
              <tr key={product.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  {product.image_url ? (
                    <img src={product.image_url} alt={product.name} className="h-10 w-10 object-cover rounded" />
                  ) : (
                    <div className="h-10 w-10 bg-gray-200 rounded flex items-center justify-center text-gray-500 text-xs">No img</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.stock_code}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 truncate max-w-[200px]">{product.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">£{product.price.toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button onClick={() => editProduct(product)} className="text-blue-600 hover:text-blue-900 mr-4">
                    <Edit2 size={18} />
                  </button>
                  <button onClick={() => handleDelete(product.id)} className="text-red-600 hover:text-red-900">
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">No products found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminProducts;
