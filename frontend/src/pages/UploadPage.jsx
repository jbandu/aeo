import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadProducts } from '../services/api';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a valid CSV file');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    setMessage(null);

    try {
      const result = await uploadProducts(file);
      setMessage(`Successfully uploaded ${result.products_created} products`);
      setFile(null);

      // Reset file input
      e.target.reset();

      // Navigate to products list after 2 seconds
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload products');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Upload Product Data</h2>

        <div className="mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">CSV Format Requirements</h3>
            <p className="text-sm text-blue-800 mb-2">
              Your CSV file should include the following columns:
            </p>
            <ul className="text-sm text-blue-800 list-disc list-inside space-y-1">
              <li><strong>sku</strong> - Product SKU (required)</li>
              <li><strong>title</strong> - Product title (required)</li>
              <li><strong>description</strong> - Product description (optional)</li>
              <li><strong>category</strong> - Product category (optional)</li>
              <li><strong>brand</strong> - Brand name (optional)</li>
              <li><strong>price</strong> - Price (optional)</li>
              <li><strong>attributes</strong> - JSON string of attributes (optional)</li>
            </ul>
            <p className="text-sm text-blue-800 mt-3">
              A sample CSV file is available in <code className="bg-blue-100 px-1 rounded">sample_data/sample_products.csv</code>
            </p>
          </div>
        </div>

        <form onSubmit={handleUpload}>
          <div className="mb-6">
            <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">
              Select CSV File
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-blue-400 transition-colors">
              <div className="space-y-1 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                  >
                    <span>Upload a file</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      accept=".csv"
                      className="sr-only"
                      onChange={handleFileChange}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">CSV files only</p>
              </div>
            </div>
            {file && (
              <p className="mt-2 text-sm text-green-600">
                Selected: {file.name}
              </p>
            )}
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {message && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={!file || uploading}
            className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Upload Products'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default UploadPage;
