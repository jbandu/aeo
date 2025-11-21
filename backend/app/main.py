from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import csv
import io
import json
import sqlite3
from datetime import datetime

from database import init_database, get_db
from models import (
    Product, ProductCreate, EnrichedProduct, ProductWithEnrichment,
    UploadResponse, EnrichmentResponse, AEOScoreBreakdown
)
from services.enrichment import EnrichmentService, calculate_aeo_score

# Initialize FastAPI app
app = FastAPI(
    title="AEO Platform API",
    description="Answer Engine Optimization Platform for Product Content Enrichment",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()

@app.get("/")
async def root():
    return {
        "message": "AEO Platform API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/products/upload",
            "products": "/api/products",
            "enrich": "/api/products/{product_id}/enrich",
            "product_detail": "/api/products/{product_id}"
        }
    }

@app.post("/api/products/upload", response_model=UploadResponse)
async def upload_products(
    file: UploadFile = File(...),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Upload products via CSV file.

    Expected CSV columns: sku, title, description, category, brand, price, attributes
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV file
        contents = await file.read()
        csv_file = io.StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(csv_file)

        products_created = 0
        product_ids = []

        cursor = conn.cursor()

        for row in reader:
            # Parse attributes JSON if present
            attributes = None
            if 'attributes' in row and row['attributes']:
                try:
                    attributes = json.loads(row['attributes'])
                except json.JSONDecodeError:
                    attributes = {"raw": row['attributes']}

            # Insert product
            cursor.execute("""
                INSERT INTO products (sku, raw_title, raw_description, category, brand, price, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('sku', ''),
                row.get('title', ''),
                row.get('description', ''),
                row.get('category', ''),
                row.get('brand', ''),
                float(row.get('price', 0)) if row.get('price') else None,
                json.dumps(attributes) if attributes else None
            ))

            product_ids.append(cursor.lastrowid)
            products_created += 1

        conn.commit()

        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {products_created} products",
            products_created=products_created,
            product_ids=product_ids
        )

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.get("/api/products", response_model=List[ProductWithEnrichment])
async def get_products(conn: sqlite3.Connection = Depends(get_db)):
    """Get all products with their enrichment data."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.*,
            e.id as enrich_id,
            e.enriched_title,
            e.long_description,
            e.key_attributes,
            e.faqs,
            e.semantic_tags,
            e.use_cases,
            e.aeo_score,
            e.created_at as enrich_created_at
        FROM products p
        LEFT JOIN enriched_products e ON p.id = e.product_id
        ORDER BY p.created_at DESC
    """)

    rows = cursor.fetchall()
    products = []

    for row in rows:
        product = Product(
            id=row['id'],
            sku=row['sku'],
            raw_title=row['raw_title'],
            raw_description=row['raw_description'],
            category=row['category'],
            brand=row['brand'],
            price=row['price'],
            attributes=json.loads(row['attributes']) if row['attributes'] else None,
            created_at=row['created_at']
        )

        enrichment = None
        if row['enrich_id']:
            enrichment = EnrichedProduct(
                id=row['enrich_id'],
                product_id=row['id'],
                enriched_title=row['enriched_title'],
                long_description=row['long_description'],
                key_attributes=json.loads(row['key_attributes']) if row['key_attributes'] else None,
                faqs=json.loads(row['faqs']) if row['faqs'] else None,
                semantic_tags=json.loads(row['semantic_tags']) if row['semantic_tags'] else None,
                use_cases=json.loads(row['use_cases']) if row['use_cases'] else None,
                aeo_score=row['aeo_score'],
                created_at=row['enrich_created_at']
            )

        products.append(ProductWithEnrichment(product=product, enrichment=enrichment))

    return products

@app.get("/api/products/{product_id}", response_model=ProductWithEnrichment)
async def get_product(product_id: int, conn: sqlite3.Connection = Depends(get_db)):
    """Get a specific product with enrichment data."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.*,
            e.id as enrich_id,
            e.enriched_title,
            e.long_description,
            e.key_attributes,
            e.faqs,
            e.semantic_tags,
            e.use_cases,
            e.aeo_score,
            e.created_at as enrich_created_at
        FROM products p
        LEFT JOIN enriched_products e ON p.id = e.product_id
        WHERE p.id = ?
    """, (product_id,))

    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    product = Product(
        id=row['id'],
        sku=row['sku'],
        raw_title=row['raw_title'],
        raw_description=row['raw_description'],
        category=row['category'],
        brand=row['brand'],
        price=row['price'],
        attributes=json.loads(row['attributes']) if row['attributes'] else None,
        created_at=row['created_at']
    )

    enrichment = None
    if row['enrich_id']:
        enrichment = EnrichedProduct(
            id=row['enrich_id'],
            product_id=row['id'],
            enriched_title=row['enriched_title'],
            long_description=row['long_description'],
            key_attributes=json.loads(row['key_attributes']) if row['key_attributes'] else None,
            faqs=json.loads(row['faqs']) if row['faqs'] else None,
            semantic_tags=json.loads(row['semantic_tags']) if row['semantic_tags'] else None,
            use_cases=json.loads(row['use_cases']) if row['use_cases'] else None,
            aeo_score=row['aeo_score'],
            created_at=row['enrich_created_at']
        )

    return ProductWithEnrichment(product=product, enrichment=enrichment)

@app.post("/api/products/{product_id}/enrich", response_model=EnrichmentResponse)
async def enrich_product(product_id: int, conn: sqlite3.Connection = Depends(get_db)):
    """Enrich a product using Claude API."""
    cursor = conn.cursor()

    # Get product data
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    # Prepare product data
    product_data = {
        'id': row['id'],
        'sku': row['sku'],
        'raw_title': row['raw_title'],
        'raw_description': row['raw_description'],
        'category': row['category'],
        'brand': row['brand'],
        'price': row['price'],
        'attributes': json.loads(row['attributes']) if row['attributes'] else None
    }

    try:
        # Initialize enrichment service
        enrichment_service = EnrichmentService()

        # Enrich product
        enriched_data = enrichment_service.enrich_product(product_data)

        # Calculate AEO score
        aeo_score, score_breakdown = calculate_aeo_score(enriched_data, product_data)

        # Check if enrichment already exists
        cursor.execute("SELECT id FROM enriched_products WHERE product_id = ?", (product_id,))
        existing = cursor.fetchone()

        if existing:
            # Update existing enrichment
            cursor.execute("""
                UPDATE enriched_products
                SET enriched_title = ?,
                    long_description = ?,
                    key_attributes = ?,
                    faqs = ?,
                    semantic_tags = ?,
                    use_cases = ?,
                    aeo_score = ?,
                    created_at = CURRENT_TIMESTAMP
                WHERE product_id = ?
            """, (
                enriched_data['enriched_title'],
                enriched_data['long_description'],
                json.dumps(enriched_data['key_attributes']),
                json.dumps(enriched_data['faqs']),
                json.dumps(enriched_data['semantic_tags']),
                json.dumps(enriched_data['use_cases']),
                aeo_score,
                product_id
            ))
            enrichment_id = existing['id']
        else:
            # Insert new enrichment
            cursor.execute("""
                INSERT INTO enriched_products
                (product_id, enriched_title, long_description, key_attributes, faqs, semantic_tags, use_cases, aeo_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                enriched_data['enriched_title'],
                enriched_data['long_description'],
                json.dumps(enriched_data['key_attributes']),
                json.dumps(enriched_data['faqs']),
                json.dumps(enriched_data['semantic_tags']),
                json.dumps(enriched_data['use_cases']),
                aeo_score
            ))
            enrichment_id = cursor.lastrowid

        # Log enrichment
        cursor.execute("""
            INSERT INTO enrichment_logs (product_id, enrichment_type, prompt_used, tokens_used)
            VALUES (?, ?, ?, ?)
        """, (
            product_id,
            'full_enrichment',
            enriched_data.get('prompt_used', ''),
            enriched_data.get('tokens_used', 0)
        ))

        conn.commit()

        return EnrichmentResponse(
            success=True,
            message="Product enriched successfully",
            product_id=product_id,
            enrichment_id=enrichment_id,
            aeo_score=aeo_score
        )

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")

@app.get("/api/products/{product_id}/score", response_model=AEOScoreBreakdown)
async def get_score_breakdown(product_id: int, conn: sqlite3.Connection = Depends(get_db)):
    """Get detailed AEO score breakdown for a product."""
    cursor = conn.cursor()

    # Get product and enrichment data
    cursor.execute("""
        SELECT p.*, e.*
        FROM products p
        LEFT JOIN enriched_products e ON p.id = e.product_id
        WHERE p.id = ?
    """, (product_id,))

    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    if not row['enriched_title']:
        raise HTTPException(status_code=404, detail="Product has not been enriched yet")

    # Prepare data for scoring
    product_data = {
        'raw_title': row['raw_title'],
        'brand': row['brand'],
        'category': row['category']
    }

    enriched_data = {
        'enriched_title': row['enriched_title'],
        'long_description': row['long_description'],
        'key_attributes': json.loads(row['key_attributes']) if row['key_attributes'] else [],
        'faqs': json.loads(row['faqs']) if row['faqs'] else [],
        'semantic_tags': json.loads(row['semantic_tags']) if row['semantic_tags'] else [],
        'use_cases': json.loads(row['use_cases']) if row['use_cases'] else []
    }

    total_score, breakdown = calculate_aeo_score(enriched_data, product_data)

    return AEOScoreBreakdown(
        total_score=total_score,
        title_optimization=breakdown['title_optimization'],
        attribute_completeness=breakdown['attribute_completeness'],
        semantic_richness=breakdown['semantic_richness'],
        structured_data=breakdown['structured_data'],
        consistency=breakdown['consistency'],
        details=breakdown['details']
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
