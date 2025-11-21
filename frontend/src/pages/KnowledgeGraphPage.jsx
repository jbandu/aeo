import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GraphVisualization from '../components/GraphVisualization';
import { getFullKnowledgeGraph, batchAnalyzeRelationships } from '../services/api';

function KnowledgeGraphPage() {
  const navigate = useNavigate();
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const data = await getFullKnowledgeGraph();
      setGraphData(data.graph);
      setStats(data.stats);
    } catch (err) {
      setError('Failed to load knowledge graph');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchAnalyze = async () => {
    if (!confirm('This will analyze all products and may take several minutes. Continue?')) {
      return;
    }

    try {
      setAnalyzing(true);
      const result = await batchAnalyzeRelationships();
      alert(`Analysis complete! Created ${result.statistics.total_relationships} relationships.`);
      await loadGraph(); // Reload to see new relationships
    } catch (err) {
      alert('Batch analysis failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleNodeClick = (productId) => {
    navigate(`/products/${productId}`);
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

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Knowledge Graph</h2>
            <p className="text-gray-600 mt-1">
              Visual representation of product relationships and catalog structure
            </p>
          </div>
          <button
            onClick={handleBatchAnalyze}
            disabled={analyzing}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analyzing ? 'Analyzing All Products...' : 'Batch Analyze All Products'}
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="card">
            <div className="text-sm text-gray-600">Total Nodes</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_nodes}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600">Total Relationships</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_edges}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600">Graph Density</div>
            <div className="text-2xl font-bold text-gray-900">
              {stats.total_nodes > 0
                ? ((stats.total_edges / (stats.total_nodes * (stats.total_nodes - 1))) * 100).toFixed(2)
                : 0}%
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">How to Use</h3>
        <ul className="text-sm text-blue-800 list-disc list-inside space-y-1">
          <li>Click and drag nodes to reposition them</li>
          <li>Scroll to zoom in/out</li>
          <li>Hover over nodes to highlight connections</li>
          <li>Click on product nodes to view details</li>
          <li>Use "Batch Analyze" to discover relationships between all products</li>
        </ul>
      </div>

      {/* Graph Visualization */}
      <div className="relative">
        {graphData && (
          <GraphVisualization
            graphData={graphData}
            onNodeClick={handleNodeClick}
            height={700}
          />
        )}
      </div>

      {/* Relationship Types Info */}
      <div className="mt-6 card">
        <h3 className="text-lg font-semibold mb-3">Relationship Types</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="flex items-center mb-2">
              <div className="w-8 h-0.5 bg-blue-500 mr-2"></div>
              <span className="font-medium text-blue-900">Similar To</span>
            </div>
            <p className="text-sm text-gray-600">
              Products that are functionally similar or serve the same purpose
            </p>
          </div>
          <div>
            <div className="flex items-center mb-2">
              <div className="w-8 h-0.5 bg-green-500 mr-2"></div>
              <span className="font-medium text-green-900">Complements</span>
            </div>
            <p className="text-sm text-gray-600">
              Products that work well together or complement each other
            </p>
          </div>
          <div>
            <div className="flex items-center mb-2">
              <div className="w-8 h-0.5 bg-amber-500 mr-2"></div>
              <span className="font-medium text-amber-900">Alternative To</span>
            </div>
            <p className="text-sm text-gray-600">
              Products that are alternatives at different price points or brands
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default KnowledgeGraphPage;
