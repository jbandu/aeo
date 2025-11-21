# AEO Platform - Answer Engine Optimization

A comprehensive platform for optimizing product content for answer engines using AI-powered enrichment. Built with FastAPI, React, and Claude API.

## Overview

The AEO Platform helps businesses optimize their product content to be more discoverable and informative for AI-powered search engines and answer engines. It uses Claude AI to enrich product data with semantic content, structured attributes, FAQs, and use cases, then provides an AEO score (0-100) to measure optimization quality.

## Features

- **CSV Product Upload**: Bulk upload products via CSV files
- **AI-Powered Enrichment**: Automatically enhance product data using Claude API
- **AEO Scoring**: 0-100 score based on 5 key metrics:
  - Title optimization (20 points)
  - Attribute completeness (20 points)
  - Semantic richness (20 points)
  - Structured data (20 points)
  - Consistency (20 points)
- **Visual Dashboard**: Color-coded product list with score visualization
- **Side-by-Side Comparison**: View original vs enriched content
- **Detailed Score Breakdown**: Understand exactly how scores are calculated

## Project Structure

```
aeo/
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI application
│   ├── database/
│   │   ├── __init__.py          # Database connection & initialization
│   │   └── schema.sql           # SQLite schema
│   ├── models/
│   │   └── __init__.py          # Pydantic models
│   ├── services/
│   │   └── enrichment.py        # Claude API integration & scoring
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client
│   │   ├── styles/              # CSS & Tailwind
│   │   ├── App.jsx              # Main app component
│   │   └── main.jsx             # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
└── sample_data/
    └── sample_products.csv      # Sample product data
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- Anthropic API key

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aeo
```

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY='your-api-key-here'
export DATABASE_PATH='aeo_platform.db'  # Optional, defaults to aeo_platform.db
```

### 3. Set Up Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file (optional)
echo "VITE_API_URL=http://localhost:8000" > .env
```

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # If not already activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage Guide

### 1. Upload Products

1. Navigate to the "Upload" page
2. Select a CSV file with the following columns:
   - `sku` (required): Product SKU
   - `title` (required): Product title
   - `description` (optional): Product description
   - `category` (optional): Product category
   - `brand` (optional): Brand name
   - `price` (optional): Price
   - `attributes` (optional): JSON string of attributes

3. Click "Upload Products"

**Sample CSV:** See `sample_data/sample_products.csv` for an example.

### 2. View Products

- The main page displays all products
- Products are shown with their current AEO scores:
  - Green (75-100): Excellent optimization
  - Yellow (50-74): Good optimization
  - Red (0-49): Needs improvement
  - Gray: Not yet enriched

### 3. Enrich Products

1. Click the "Enrich" button on any product
2. Wait for Claude API to generate enriched content (15-30 seconds)
3. View the updated AEO score

### 4. View Product Details

1. Click "View Details" on any product
2. See side-by-side comparison of original vs enriched data
3. View detailed score breakdown across 5 categories
4. Re-enrich if needed to regenerate content

## API Documentation

### Endpoints

#### Upload Products
```
POST /api/products/upload
Content-Type: multipart/form-data

Uploads a CSV file containing product data.
```

#### Get All Products
```
GET /api/products

Returns all products with their enrichment data.
```

#### Get Single Product
```
GET /api/products/{product_id}

Returns a specific product with enrichment data.
```

#### Enrich Product
```
POST /api/products/{product_id}/enrich

Enriches a product using Claude API.
Returns: enrichment_id, aeo_score
```

#### Get Score Breakdown
```
GET /api/products/{product_id}/score

Returns detailed AEO score breakdown.
```

### Response Models

**Product:**
```json
{
  "id": 1,
  "sku": "ELEC-001",
  "raw_title": "Wireless Earbuds",
  "raw_description": "Bluetooth earbuds with noise cancellation",
  "category": "Electronics",
  "brand": "TechSound",
  "price": 79.99,
  "attributes": {"color": "black", "battery_life": "24 hours"},
  "created_at": "2024-01-15T10:30:00"
}
```

**Enriched Product:**
```json
{
  "id": 1,
  "product_id": 1,
  "enriched_title": "Premium Wireless Earbuds with Active Noise Cancellation",
  "long_description": "Experience superior audio quality...",
  "key_attributes": [
    {"name": "Battery Life", "value": "24 hours total"},
    {"name": "Connectivity", "value": "Bluetooth 5.0"}
  ],
  "faqs": [
    {
      "question": "Are these earbuds waterproof?",
      "answer": "Yes, they have IPX4 water resistance..."
    }
  ],
  "semantic_tags": ["wireless audio", "noise cancelling", "bluetooth earbuds"],
  "use_cases": ["Commuting", "Working out", "Travel"],
  "aeo_score": 85,
  "created_at": "2024-01-15T10:35:00"
}
```

## AEO Scoring System

The AEO score (0-100) is calculated based on five categories:

### 1. Title Optimization (20 points)
- **20 pts**: 45-60 characters (optimal)
- **15 pts**: 40-45 or 60-70 characters (acceptable)
- **10 pts**: Other lengths (suboptimal)

### 2. Attribute Completeness (20 points)
- **20 pts**: 7+ attributes (excellent)
- **15 pts**: 5-6 attributes (good)
- **10 pts**: 3-4 attributes (acceptable)
- **5 pts**: <3 attributes (poor)

### 3. Semantic Richness (20 points)
- **Description (10 pts)**:
  - 10 pts: 150-200 words (optimal)
  - 7 pts: 120-150 or 200-250 words (acceptable)
  - 5 pts: Other word counts
- **FAQs (10 pts)**:
  - 10 pts: 5+ FAQs
  - 7 pts: 3-4 FAQs
  - 5 pts: 1-2 FAQs

### 4. Structured Data (20 points)
- **Tags (10 pts)**: Up to 10 points based on semantic tag count
- **Use Cases (10 pts)**: Up to 10 points based on use case count

### 5. Consistency (20 points)
- **20 pts**: Perfect alignment between original and enriched content
- **-5 pts**: Brand missing from enriched title
- **-5 pts**: Category not mentioned in description

## Environment Variables

Create a `.env` file in the backend directory:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional
DATABASE_PATH=aeo_platform.db
```

Create a `.env` file in the frontend directory:

```bash
# Optional - defaults to http://localhost:8000
VITE_API_URL=http://localhost:8000
```

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    raw_title TEXT NOT NULL,
    raw_description TEXT,
    category TEXT,
    brand TEXT,
    price REAL,
    attributes TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Enriched Products Table
```sql
CREATE TABLE enriched_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    enriched_title TEXT,
    long_description TEXT,
    key_attributes TEXT, -- JSON
    faqs TEXT, -- JSON
    semantic_tags TEXT, -- JSON
    use_cases TEXT, -- JSON
    aeo_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### Enrichment Logs Table
```sql
CREATE TABLE enrichment_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    enrichment_type TEXT NOT NULL,
    prompt_used TEXT,
    tokens_used INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## Development

### Backend Development

```bash
# Run with auto-reload
cd backend
uvicorn app.main:app --reload

# Run tests (if implemented)
pytest

# Check code quality
flake8 .
black .
```

### Frontend Development

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Backend Issues

**Issue**: `ANTHROPIC_API_KEY not set`
- **Solution**: Export the environment variable: `export ANTHROPIC_API_KEY='your-key'`

**Issue**: Database errors
- **Solution**: Delete `aeo_platform.db` and restart the backend to reinitialize

**Issue**: CORS errors
- **Solution**: Ensure the frontend is running on port 3000 or update CORS settings in `app/main.py`

### Frontend Issues

**Issue**: API connection refused
- **Solution**: Ensure backend is running on port 8000

**Issue**: Build errors
- **Solution**: Delete `node_modules` and run `npm install` again

## Production Deployment

### Backend

1. Set production environment variables
2. Use a production WSGI server (e.g., gunicorn):
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```
3. Use PostgreSQL or MySQL instead of SQLite for better performance
4. Enable proper CORS settings (restrict origins)
5. Add authentication/authorization

### Frontend

1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Serve the `dist` folder using nginx, Apache, or a CDN
3. Update `VITE_API_URL` to point to production backend

## Sample Data

The `sample_data/sample_products.csv` file contains 10 diverse products across three categories:
- Electronics (5 products)
- Fashion (3 products)
- Home & Kitchen (2 products)

Use this to test the platform functionality.

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database
- **Anthropic SDK**: Claude API integration
- **Pydantic**: Data validation and serialization

### Frontend
- **React**: UI library
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Batch enrichment for multiple products
- [ ] Export enriched data to various formats (JSON-LD, XML, etc.)
- [ ] Product comparison tool
- [ ] A/B testing for enriched content
- [ ] Analytics dashboard for enrichment performance
- [ ] Multi-language support
- [ ] Integration with e-commerce platforms
- [ ] Custom enrichment templates