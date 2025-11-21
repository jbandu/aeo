import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getProducts, enrichProduct } from '../services/api';

function ProductListPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await getProducts();
      setProducts(data);
    } catch (err) {
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async (productId) => {
    try {
      setEnriching(productId);
      await enrichProduct(productId);
      await loadProducts(); // Reload to get updated data
    } catch (err) {
      alert('Failed to enrich product: ' + (err.response?.data?.detail || err.message));
    } finally {
      setEnriching(null);
    }
  };

  const getScoreBadgeClass = (score) => {
    if (!score) return 'score-badge bg-gray-100 text-gray-800';
    if (score >= 75) return 'score-badge score-high';
    if (score >= 50) return 'score-badge score-medium';
    return 'score-badge score-low';
  };

  const getScoreLabel = (score) => {
    if (!score) return 'Not Enriched';
    return `Score: ${score}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No products</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by uploading a product CSV file.</p>
        <div className="mt-6">
          <Link to="/upload" className="btn btn-primary">
            Upload Products
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Products</h2>
          <p className="text-gray-600 mt-1">{products.length} total products</p>
        </div>
        <Link to="/upload" className="btn btn-primary">
          Upload More Products
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {products.map((item) => {
          const product = item.product;
          const enrichment = item.enrichment;
          const isEnriched = !!enrichment;
          const aeoScore = enrichment?.aeo_score || 0;

          return (
            <div key={product.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-1">SKU: {product.sku}</p>
                  <h3 className="font-semibold text-lg text-gray-900 line-clamp-2">
                    {product.raw_title}
                  </h3>
                </div>
                <span className={getScoreBadgeClass(aeoScore)}>
                  {getScoreLabel(aeoScore)}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                {product.category && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Category:</span> {product.category}
                  </p>
                )}
                {product.brand && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Brand:</span> {product.brand}
                  </p>
                )}
                {product.price && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Price:</span> ${product.price}
                  </p>
                )}
              </div>

              <p className="text-sm text-gray-600 line-clamp-2 mb-4">
                {product.raw_description || 'No description available'}
              </p>

              <div className="flex space-x-2">
                <Link
                  to={`/products/${product.id}`}
                  className="btn btn-secondary flex-1 text-center"
                >
                  View Details
                </Link>
                <button
                  onClick={() => handleEnrich(product.id)}
                  disabled={enriching === product.id}
                  className="btn btn-success flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {enriching === product.id ? 'Enriching...' : isEnriched ? 'Re-enrich' : 'Enrich'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ProductListPage;
