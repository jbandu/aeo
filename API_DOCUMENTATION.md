# AEO Platform API Documentation

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Currently, the API does not require authentication. For production use, implement authentication/authorization.

## Endpoints

### 1. Root Endpoint

Get API information and available endpoints.

**Endpoint**: `GET /`

**Response**:
```json
{
  "message": "AEO Platform API",
  "version": "1.0.0",
  "endpoints": {
    "upload": "/api/products/upload",
    "products": "/api/products",
    "enrich": "/api/products/{product_id}/enrich",
    "product_detail": "/api/products/{product_id}"
  }
}
```

---

### 2. Upload Products

Upload a CSV file containing product data.

**Endpoint**: `POST /api/products/upload`

**Content-Type**: `multipart/form-data`

**Request Body**:
- `file`: CSV file (required)

**CSV Format**:
The CSV file should contain the following columns:

| Column | Required | Type | Description |
|--------|----------|------|-------------|
| sku | Yes | string | Product SKU (unique identifier) |
| title | Yes | string | Product title |
| description | No | string | Product description |
| category | No | string | Product category |
| brand | No | string | Brand name |
| price | No | float | Product price |
| attributes | No | JSON string | Product attributes as JSON |

**Example CSV**:
```csv
sku,title,description,category,brand,price,attributes
ELEC-001,Wireless Earbuds,Bluetooth earbuds with noise cancellation,Electronics,TechSound,79.99,"{""color"": ""black"", ""battery_life"": ""24 hours""}"
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Successfully uploaded 10 products",
  "products_created": 10,
  "product_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "File must be a CSV"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "Error processing CSV: [error details]"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/products/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_products.csv"
```

---

### 3. Get All Products

Retrieve all products with their enrichment data.

**Endpoint**: `GET /api/products`

**Response** (200 OK):
```json
[
  {
    "product": {
      "id": 1,
      "sku": "ELEC-001",
      "raw_title": "Wireless Earbuds",
      "raw_description": "Bluetooth earbuds with noise cancellation",
      "category": "Electronics",
      "brand": "TechSound",
      "price": 79.99,
      "attributes": {
        "color": "black",
        "battery_life": "24 hours",
        "wireless": true
      },
      "created_at": "2024-01-15T10:30:00"
    },
    "enrichment": {
      "id": 1,
      "product_id": 1,
      "enriched_title": "Premium Wireless Earbuds with 24H Battery & Active Noise Cancellation",
      "long_description": "Experience superior audio quality with these advanced wireless earbuds...",
      "key_attributes": [
        {"name": "Battery Life", "value": "24 hours total playtime"},
        {"name": "Connectivity", "value": "Bluetooth 5.0"},
        {"name": "Noise Cancellation", "value": "Active ANC technology"}
      ],
      "faqs": [
        {
          "question": "How long does the battery last?",
          "answer": "The earbuds provide up to 6 hours of continuous playback, with an additional 18 hours from the charging case, totaling 24 hours."
        }
      ],
      "semantic_tags": ["wireless audio", "noise cancelling", "bluetooth earbuds", "portable audio"],
      "use_cases": ["Commuting and travel", "Working out at the gym", "Remote work calls"],
      "aeo_score": 85,
      "created_at": "2024-01-15T10:35:00"
    }
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/products" \
  -H "accept: application/json"
```

---

### 4. Get Single Product

Retrieve a specific product with its enrichment data.

**Endpoint**: `GET /api/products/{product_id}`

**Path Parameters**:
- `product_id` (integer, required): Product ID

**Success Response** (200 OK):
```json
{
  "product": {
    "id": 1,
    "sku": "ELEC-001",
    "raw_title": "Wireless Earbuds",
    "raw_description": "Bluetooth earbuds with noise cancellation",
    "category": "Electronics",
    "brand": "TechSound",
    "price": 79.99,
    "attributes": {
      "color": "black",
      "battery_life": "24 hours",
      "wireless": true
    },
    "created_at": "2024-01-15T10:30:00"
  },
  "enrichment": {
    "id": 1,
    "product_id": 1,
    "enriched_title": "Premium Wireless Earbuds with 24H Battery & Active Noise Cancellation",
    "long_description": "Experience superior audio quality with these advanced wireless earbuds...",
    "key_attributes": [
      {"name": "Battery Life", "value": "24 hours total playtime"}
    ],
    "faqs": [
      {
        "question": "How long does the battery last?",
        "answer": "The earbuds provide up to 6 hours of continuous playback..."
      }
    ],
    "semantic_tags": ["wireless audio", "noise cancelling"],
    "use_cases": ["Commuting and travel", "Working out at the gym"],
    "aeo_score": 85,
    "created_at": "2024-01-15T10:35:00"
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Product not found"
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/products/1" \
  -H "accept: application/json"
```

---

### 5. Enrich Product

Enrich a product using Claude API to generate optimized content.

**Endpoint**: `POST /api/products/{product_id}/enrich`

**Path Parameters**:
- `product_id` (integer, required): Product ID

**Process**:
1. Retrieves product data from database
2. Sends data to Claude API with enrichment prompt
3. Receives enriched content (title, description, attributes, FAQs, tags, use cases)
4. Calculates AEO score (0-100)
5. Stores enriched data and logs the enrichment
6. Returns enrichment result

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Product enriched successfully",
  "product_id": 1,
  "enrichment_id": 1,
  "aeo_score": 85
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Product not found"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "Enrichment failed: [error details]"
}
```

**Note**: This endpoint requires a valid `ANTHROPIC_API_KEY` environment variable. Enrichment typically takes 15-30 seconds.

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/products/1/enrich" \
  -H "accept: application/json"
```

---

### 6. Get Score Breakdown

Get detailed AEO score breakdown for an enriched product.

**Endpoint**: `GET /api/products/{product_id}/score`

**Path Parameters**:
- `product_id` (integer, required): Product ID

**Success Response** (200 OK):
```json
{
  "total_score": 85,
  "title_optimization": 20,
  "attribute_completeness": 15,
  "semantic_richness": 17,
  "structured_data": 18,
  "consistency": 15,
  "details": {
    "title": "Optimal length",
    "attributes": "6 attributes (good)",
    "semantic": "178 words, 4 FAQs",
    "structured": "7 tags, 3 use cases",
    "consistency": "Excellent alignment"
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Product not found"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Product has not been enriched yet"
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/products/1/score" \
  -H "accept: application/json"
```

---

## Data Models

### Product

```typescript
{
  id: number;
  sku: string;
  raw_title: string;
  raw_description: string | null;
  category: string | null;
  brand: string | null;
  price: number | null;
  attributes: object | null;
  created_at: string; // ISO 8601 datetime
}
```

### Enriched Product

```typescript
{
  id: number;
  product_id: number;
  enriched_title: string;
  long_description: string;
  key_attributes: Array<{name: string, value: string}>;
  faqs: Array<{question: string, answer: string}>;
  semantic_tags: string[];
  use_cases: string[];
  aeo_score: number; // 0-100
  created_at: string; // ISO 8601 datetime
}
```

### Product With Enrichment

```typescript
{
  product: Product;
  enrichment: EnrichedProduct | null;
}
```

### Upload Response

```typescript
{
  success: boolean;
  message: string;
  products_created: number;
  product_ids: number[];
}
```

### Enrichment Response

```typescript
{
  success: boolean;
  message: string;
  product_id: number;
  enrichment_id: number;
  aeo_score: number; // 0-100
}
```

### AEO Score Breakdown

```typescript
{
  total_score: number; // 0-100
  title_optimization: number; // 0-20
  attribute_completeness: number; // 0-20
  semantic_richness: number; // 0-20
  structured_data: number; // 0-20
  consistency: number; // 0-20
  details: {
    title: string;
    attributes: string;
    semantic: string;
    structured: string;
    consistency: string;
  };
}
```

---

## Error Handling

All errors follow the FastAPI standard error format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters or body
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error (database, API, etc.)

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting to prevent abuse, especially for the enrichment endpoint which calls the Claude API.

---

## CORS Configuration

The API is configured to accept requests from all origins (`*`). For production:

1. Update `allow_origins` in `backend/app/main.py`
2. Specify exact frontend domain(s)
3. Consider enabling credentials if needed

Example:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Enrichment Details

### Claude API Integration

The enrichment process uses Claude 3.5 Sonnet with the following configuration:

- **Model**: `claude-3-5-sonnet-20241022`
- **Max Tokens**: 2048
- **Response Format**: JSON

### Enrichment Prompt Structure

The prompt includes:
1. Product information (SKU, title, description, category, brand, price, attributes)
2. Instructions for AEO optimization
3. Required JSON structure for response
4. Quality requirements for each field

### Token Usage Tracking

Token usage is logged in the `enrichment_logs` table for monitoring and cost tracking.

---

## Database

The API uses SQLite by default. For production use, consider:

1. PostgreSQL or MySQL for better performance
2. Connection pooling
3. Database backups
4. Index optimization

---

## Performance Considerations

### Enrichment Endpoint

- Takes 15-30 seconds per product
- Makes external API call to Claude
- Consider implementing:
  - Background job processing (Celery, RQ)
  - Rate limiting
  - Caching
  - Batch processing

### Product List Endpoint

- Returns all products (no pagination)
- Consider implementing pagination for large datasets:
  - Query parameters: `?page=1&limit=20`
  - Response metadata: `total_count`, `page`, `pages`

---

## Testing

### Example Test Workflow

1. Upload sample products:
```bash
curl -X POST http://localhost:8000/api/products/upload -F "file=@sample_data/sample_products.csv"
```

2. List all products:
```bash
curl http://localhost:8000/api/products
```

3. Enrich first product:
```bash
curl -X POST http://localhost:8000/api/products/1/enrich
```

4. View enriched product:
```bash
curl http://localhost:8000/api/products/1
```

5. Get score breakdown:
```bash
curl http://localhost:8000/api/products/1/score
```

---

## WebSocket Support

Currently not implemented. Future versions may include WebSocket support for:
- Real-time enrichment progress updates
- Live score calculations
- Batch processing notifications

---

## Versioning

Current version: **1.0.0**

The API does not currently use versioning in the URL structure. For production, consider:
- `/api/v1/products`
- Header-based versioning
- Semantic versioning for breaking changes

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Anthropic API Documentation**: https://docs.anthropic.com/
- **SQLite Documentation**: https://www.sqlite.org/docs.html
