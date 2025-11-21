import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

function GraphVisualization({ graphData, onNodeClick, height = 600 }) {
  const fgRef = useRef();
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());

  useEffect(() => {
    // Auto-fit graph on load
    if (fgRef.current && graphData.nodes.length > 0) {
      fgRef.current.zoomToFit(400);
    }
  }, [graphData]);

  const handleNodeClick = (node) => {
    if (onNodeClick) {
      // Extract product ID from node
      const productId = typeof node.id === 'string' && node.id.startsWith('category_')
        ? null
        : parseInt(node.id);

      if (productId) {
        onNodeClick(productId);
      }
    }
  };

  const handleNodeHover = (node) => {
    const nodes = new Set();
    const links = new Set();

    if (node) {
      nodes.add(node);

      // Highlight connected nodes and links
      graphData.links.forEach(link => {
        if (link.source.id === node.id || link.source === node.id) {
          links.add(link);
          nodes.add(typeof link.target === 'object' ? link.target :
            graphData.nodes.find(n => n.id === link.target));
        }
        if (link.target.id === node.id || link.target === node.id) {
          links.add(link);
          nodes.add(typeof link.source === 'object' ? link.source :
            graphData.nodes.find(n => n.id === link.source));
        }
      });
    }

    setHighlightNodes(nodes);
    setHighlightLinks(links);
  };

  const getNodeColor = (node) => {
    if (highlightNodes.size > 0 && !highlightNodes.has(node)) {
      return 'rgba(200, 200, 200, 0.3)';
    }

    switch (node.type) {
      case 'product':
        return getGroupColor(node.group);
      case 'category':
        return '#8B5CF6'; // Purple
      case 'brand':
        return '#F59E0B'; // Amber
      default:
        return '#6B7280'; // Gray
    }
  };

  const getGroupColor = (group) => {
    // Hash the group name to get a consistent color
    let hash = 0;
    for (let i = 0; i < group.length; i++) {
      hash = group.charCodeAt(i) + ((hash << 5) - hash);
    }

    const colors = [
      '#3B82F6', // Blue
      '#10B981', // Green
      '#EF4444', // Red
      '#8B5CF6', // Purple
      '#F59E0B', // Amber
      '#EC4899', // Pink
      '#14B8A6', // Teal
    ];

    return colors[Math.abs(hash) % colors.length];
  };

  const getLinkColor = (link) => {
    if (highlightLinks.size > 0 && !highlightLinks.has(link)) {
      return 'rgba(200, 200, 200, 0.1)';
    }

    switch (link.type) {
      case 'SIMILAR_TO':
        return '#3B82F6'; // Blue
      case 'COMPLEMENTS':
        return '#10B981'; // Green
      case 'ALTERNATIVE_TO':
        return '#F59E0B'; // Amber
      case 'BELONGS_TO':
        return 'rgba(139, 92, 246, 0.3)'; // Purple (faded)
      case 'MADE_BY':
        return 'rgba(245, 158, 11, 0.3)'; // Amber (faded)
      default:
        return 'rgba(107, 114, 128, 0.3)'; // Gray
    }
  };

  const getLinkWidth = (link) => {
    if (link.type === 'BELONGS_TO' || link.type === 'MADE_BY') {
      return 1;
    }
    return link.score ? 1 + link.score * 3 : 2;
  };

  const getNodeSize = (node) => {
    switch (node.type) {
      case 'product':
        return 5;
      case 'category':
        return 8;
      case 'brand':
        return 7;
      default:
        return 4;
    }
  };

  const paintNode = (node, ctx, globalScale) => {
    const label = node.label;
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;

    // Draw node
    const size = getNodeSize(node);
    ctx.fillStyle = getNodeColor(node);
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI, false);
    ctx.fill();

    // Draw label
    if (globalScale > 1.5 || highlightNodes.has(node)) {
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#1F2937';
      ctx.fillText(label, node.x, node.y + size + fontSize);
    }
  };

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
        <p className="text-gray-500">No graph data available</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg bg-white overflow-hidden">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel="label"
        nodeColor={getNodeColor}
        nodeCanvasObject={paintNode}
        nodeCanvasObjectMode={() => 'replace'}
        linkColor={getLinkColor}
        linkWidth={getLinkWidth}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.15}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        width={window.innerWidth * 0.85}
        height={height}
        cooldownTicks={100}
        onEngineStop={() => fgRef.current?.zoomToFit(400)}
      />

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg text-sm">
        <h4 className="font-semibold mb-2">Legend</h4>

        <div className="space-y-1 mb-3">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span>Product Nodes</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
            <span>Category</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-amber-500 mr-2"></div>
            <span>Brand</span>
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center">
            <div className="w-8 h-0.5 bg-blue-500 mr-2"></div>
            <span>Similar To</span>
          </div>
          <div className="flex items-center">
            <div className="w-8 h-0.5 bg-green-500 mr-2"></div>
            <span>Complements</span>
          </div>
          <div className="flex items-center">
            <div className="w-8 h-0.5 bg-amber-500 mr-2"></div>
            <span>Alternative To</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GraphVisualization;
