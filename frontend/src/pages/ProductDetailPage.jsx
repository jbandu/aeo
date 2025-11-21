import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getProduct, enrichProduct, getScoreBreakdown } from '../services/api';

function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [scoreBreakdown, setScoreBreakdown] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProduct();
  }, [id]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const productData = await getProduct(id);
      setData(productData);

      // Load score breakdown if enriched
      if (productData.enrichment) {
        try {
          const breakdown = await getScoreBreakdown(id);
          setScoreBreakdown(breakdown);
        } catch (err) {
          console.error('Failed to load score breakdown:', err);
        }
      }
    } catch (err) {
      setError('Failed to load product');
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    try {
      setEnriching(true);
      await enrichProduct(id);
      await loadProduct();
    } catch (err) {
      alert('Failed to enrich product: ' + (err.response?.data?.detail || err.message));
    } finally {
      setEnriching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
          {error || 'Product not found'}
        </div>
        <Link to="/" className="btn btn-secondary">
          Back to Products
        </Link>
      </div>
    );
  }

  const { product, enrichment } = data;
  const isEnriched = !!enrichment;

  const getScoreBadgeClass = (score) => {
    if (!score) return 'score-badge bg-gray-100 text-gray-800';
    if (score >= 75) return 'score-badge score-high';
    if (score >= 50) return 'score-badge score-medium';
    return 'score-badge score-low';
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button onClick={() => navigate(-1)} className="text-blue-600 hover:text-blue-800 mb-4 flex items-center">
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>

        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm text-gray-500 mb-1">SKU: {product.sku}</p>
            <h1 className="text-3xl font-bold text-gray-900">{product.raw_title}</h1>
            <div className="flex items-center space-x-4 mt-2">
              {product.category && (
                <span className="text-sm text-gray-600">Category: {product.category}</span>
              )}
              {product.brand && (
                <span className="text-sm text-gray-600">Brand: {product.brand}</span>
              )}
              {product.price && (
                <span className="text-sm font-semibold text-gray-900">Price: ${product.price}</span>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-3">
            {isEnriched && (
              <span className={getScoreBadgeClass(enrichment.aeo_score)}>
                AEO Score: {enrichment.aeo_score}
              </span>
            )}
            <button
              onClick={handleEnrich}
              disabled={enriching}
              className="btn btn-success disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {enriching ? 'Enriching...' : isEnriched ? 'Re-enrich' : 'Enrich Product'}
            </button>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      {scoreBreakdown && (
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4">AEO Score Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <ScoreItem
              label="Title Optimization"
              score={scoreBreakdown.title_optimization}
              max={20}
              detail={scoreBreakdown.details.title}
            />
            <ScoreItem
              label="Attribute Completeness"
              score={scoreBreakdown.attribute_completeness}
              max={20}
              detail={scoreBreakdown.details.attributes}
            />
            <ScoreItem
              label="Semantic Richness"
              score={scoreBreakdown.semantic_richness}
              max={20}
              detail={scoreBreakdown.details.semantic}
            />
            <ScoreItem
              label="Structured Data"
              score={scoreBreakdown.structured_data}
              max={20}
              detail={scoreBreakdown.details.structured}
            />
            <ScoreItem
              label="Consistency"
              score={scoreBreakdown.consistency}
              max={20}
              detail={scoreBreakdown.details.consistency}
            />
          </div>
        </div>
      )}

      {/* Side-by-side comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Original Data */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <span className="w-3 h-3 bg-gray-400 rounded-full mr-2"></span>
            Original Data
          </h2>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-semibold text-gray-700">Title</label>
              <p className="text-gray-900 mt-1">{product.raw_title}</p>
            </div>

            <div>
              <label className="text-sm font-semibold text-gray-700">Description</label>
              <p className="text-gray-900 mt-1">{product.raw_description || 'No description'}</p>
            </div>

            {product.attributes && (
              <div>
                <label className="text-sm font-semibold text-gray-700">Attributes</label>
                <div className="mt-1 bg-gray-50 rounded-lg p-3">
                  {Object.entries(product.attributes).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="font-medium">{key}:</span> {String(value)}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Enriched Data */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
            Enriched Data
          </h2>

          {!isEnriched ? (
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
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              <p className="mt-2 text-sm text-gray-500">This product has not been enriched yet.</p>
              <button onClick={handleEnrich} className="btn btn-success mt-4">
                Enrich Now
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-gray-700">Optimized Title</label>
                <p className="text-gray-900 mt-1 font-medium">{enrichment.enriched_title}</p>
                <p className="text-xs text-gray-500 mt-1">{enrichment.enriched_title.length} characters</p>
              </div>

              <div>
                <label className="text-sm font-semibold text-gray-700">Long Description</label>
                <p className="text-gray-900 mt-1">{enrichment.long_description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {enrichment.long_description.split(' ').length} words
                </p>
              </div>

              {enrichment.key_attributes && enrichment.key_attributes.length > 0 && (
                <div>
                  <label className="text-sm font-semibold text-gray-700">Key Attributes</label>
                  <div className="mt-1 bg-green-50 rounded-lg p-3 space-y-2">
                    {enrichment.key_attributes.map((attr, index) => (
                      <div key={index} className="text-sm">
                        <span className="font-medium">{attr.name}:</span> {attr.value}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {enrichment.semantic_tags && enrichment.semantic_tags.length > 0 && (
                <div>
                  <label className="text-sm font-semibold text-gray-700">Semantic Tags</label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {enrichment.semantic_tags.map((tag, index) => (
                      <span
                        key={index}
                        className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {enrichment.use_cases && enrichment.use_cases.length > 0 && (
                <div>
                  <label className="text-sm font-semibold text-gray-700">Use Cases</label>
                  <ul className="mt-1 list-disc list-inside space-y-1">
                    {enrichment.use_cases.map((useCase, index) => (
                      <li key={index} className="text-sm text-gray-900">
                        {useCase}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {enrichment.faqs && enrichment.faqs.length > 0 && (
                <div>
                  <label className="text-sm font-semibold text-gray-700">FAQs</label>
                  <div className="mt-2 space-y-3">
                    {enrichment.faqs.map((faq, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-3">
                        <p className="text-sm font-medium text-gray-900">{faq.question}</p>
                        <p className="text-sm text-gray-600 mt-1">{faq.answer}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoreItem({ label, score, max, detail }) {
  const percentage = (score / max) * 100;
  const getColor = () => {
    if (percentage >= 75) return 'bg-green-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="text-center">
      <div className="text-2xl font-bold text-gray-900">
        {score}<span className="text-sm text-gray-500">/{max}</span>
      </div>
      <div className="text-xs text-gray-600 font-medium mb-2">{label}</div>
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full ${getColor()}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <div className="text-xs text-gray-500">{detail}</div>
    </div>
  );
}

export default ProductDetailPage;
