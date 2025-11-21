import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadProducts = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${API_BASE_URL}/api/products/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getProducts = async () => {
  const response = await api.get('/api/products');
  return response.data;
};

export const getProduct = async (productId) => {
  const response = await api.get(`/api/products/${productId}`);
  return response.data;
};

export const enrichProduct = async (productId) => {
  const response = await api.post(`/api/products/${productId}/enrich`);
  return response.data;
};

export const getScoreBreakdown = async (productId) => {
  const response = await api.get(`/api/products/${productId}/score`);
  return response.data;
};

// Knowledge Graph API calls
export const analyzeProductRelationships = async (productId) => {
  const response = await api.post(`/api/products/${productId}/analyze-relationships`);
  return response.data;
};

export const getProductRelationships = async (productId) => {
  const response = await api.get(`/api/products/${productId}/relationships`);
  return response.data;
};

export const getProductRecommendations = async (productId) => {
  const response = await api.get(`/api/products/${productId}/recommendations`);
  return response.data;
};

export const getProductGraph = async (productId) => {
  const response = await api.get(`/api/products/${productId}/graph`);
  return response.data;
};

export const getFullKnowledgeGraph = async () => {
  const response = await api.get('/api/knowledge-graph');
  return response.data;
};

export const batchAnalyzeRelationships = async () => {
  const response = await api.post('/api/products/batch-analyze');
  return response.data;
};

export default api;
