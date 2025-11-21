from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

# Product Models
class ProductCreate(BaseModel):
    sku: str
    raw_title: str
    raw_description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None

class Product(BaseModel):
    id: int
    sku: str
    raw_title: str
    raw_description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None
    created_at: str

    class Config:
        from_attributes = True

# Enriched Product Models
class EnrichedProductCreate(BaseModel):
    product_id: int
    enriched_title: str
    long_description: str
    key_attributes: List[Dict[str, str]]
    faqs: List[Dict[str, str]]
    semantic_tags: List[str]
    use_cases: List[str]
    aeo_score: int = Field(ge=0, le=100)

class EnrichedProduct(BaseModel):
    id: int
    product_id: int
    enriched_title: Optional[str] = None
    long_description: Optional[str] = None
    key_attributes: Optional[List[Dict[str, str]]] = None
    faqs: Optional[List[Dict[str, str]]] = None
    semantic_tags: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    aeo_score: int = 0
    created_at: str

    class Config:
        from_attributes = True

# Combined Product View
class ProductWithEnrichment(BaseModel):
    product: Product
    enrichment: Optional[EnrichedProduct] = None

# CSV Upload Response
class UploadResponse(BaseModel):
    success: bool
    message: str
    products_created: int
    product_ids: List[int]

# Enrichment Response
class EnrichmentResponse(BaseModel):
    success: bool
    message: str
    product_id: int
    enrichment_id: int
    aeo_score: int

# AEO Score Breakdown
class AEOScoreBreakdown(BaseModel):
    total_score: int
    title_optimization: int
    attribute_completeness: int
    semantic_richness: int
    structured_data: int
    consistency: int
    details: Dict[str, Any]
