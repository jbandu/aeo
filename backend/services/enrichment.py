import os
import json
import anthropic
from typing import Dict, Any, List

class EnrichmentService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def enrich_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a product using Claude API.

        Returns enriched data including:
        - enriched_title
        - long_description
        - key_attributes
        - faqs
        - semantic_tags
        - use_cases
        """
        prompt = self._build_enrichment_prompt(product)

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens

            # Parse JSON response
            enriched_data = json.loads(response_text)

            return {
                **enriched_data,
                "tokens_used": tokens_used,
                "prompt_used": prompt
            }

        except Exception as e:
            raise Exception(f"Enrichment failed: {str(e)}")

    def _build_enrichment_prompt(self, product: Dict[str, Any]) -> str:
        """Build the enrichment prompt for Claude."""
        attributes_str = json.dumps(product.get('attributes', {}), indent=2) if product.get('attributes') else "None"

        prompt = f"""You are an expert in Answer Engine Optimization (AEO) and product content optimization. Your task is to enrich product data to make it highly discoverable and informative for AI-powered search engines and answer engines.

Given the following product information:

**SKU:** {product.get('sku', 'N/A')}
**Title:** {product.get('raw_title', 'N/A')}
**Description:** {product.get('raw_description', 'N/A')}
**Category:** {product.get('category', 'N/A')}
**Brand:** {product.get('brand', 'N/A')}
**Price:** ${product.get('price', 'N/A')}
**Attributes:** {attributes_str}

Generate enriched product data optimized for Answer Engine Optimization (AEO). Return ONLY a valid JSON object with the following structure (no markdown formatting, no code blocks):

{{
  "enriched_title": "A 45-60 character keyword-rich, benefit-focused title",
  "long_description": "A 150-200 word semantic description that naturally incorporates relevant keywords, benefits, features, and use cases",
  "key_attributes": [
    {{"name": "attribute1", "value": "value1"}},
    {{"name": "attribute2", "value": "value2"}}
  ],
  "faqs": [
    {{"question": "Common question 1?", "answer": "Detailed answer 1"}},
    {{"question": "Common question 2?", "answer": "Detailed answer 2"}}
  ],
  "semantic_tags": ["tag1", "tag2", "tag3"],
  "use_cases": ["use case 1", "use case 2", "use case 3"]
}}

Requirements:
1. enriched_title: 45-60 characters, include primary keywords and key benefit
2. long_description: 150-200 words, natural language, SEO-optimized
3. key_attributes: 5-7 structured attributes with name-value pairs
4. faqs: 3-5 questions with detailed answers (50-100 words each)
5. semantic_tags: 5-8 relevant tags for semantic search
6. use_cases: 3-4 specific usage scenarios

Respond ONLY with the JSON object, no additional text."""

        return prompt

def calculate_aeo_score(enriched_data: Dict[str, Any], product_data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
    """
    Calculate AEO score (0-100) based on enrichment quality.

    Scoring breakdown:
    - Title optimization (20 points)
    - Attribute completeness (20 points)
    - Semantic richness (20 points)
    - Structured data (20 points)
    - Consistency (20 points)
    """
    score_breakdown = {
        "title_optimization": 0,
        "attribute_completeness": 0,
        "semantic_richness": 0,
        "structured_data": 0,
        "consistency": 0,
        "details": {}
    }

    # 1. Title Optimization (20 points)
    title = enriched_data.get("enriched_title", "")
    title_len = len(title)
    if 45 <= title_len <= 60:
        score_breakdown["title_optimization"] = 20
        score_breakdown["details"]["title"] = "Optimal length"
    elif 40 <= title_len < 45 or 60 < title_len <= 70:
        score_breakdown["title_optimization"] = 15
        score_breakdown["details"]["title"] = "Acceptable length"
    elif title_len > 0:
        score_breakdown["title_optimization"] = 10
        score_breakdown["details"]["title"] = "Suboptimal length"

    # 2. Attribute Completeness (20 points)
    attributes = enriched_data.get("key_attributes", [])
    attr_count = len(attributes)
    if attr_count >= 7:
        score_breakdown["attribute_completeness"] = 20
        score_breakdown["details"]["attributes"] = f"{attr_count} attributes (excellent)"
    elif attr_count >= 5:
        score_breakdown["attribute_completeness"] = 15
        score_breakdown["details"]["attributes"] = f"{attr_count} attributes (good)"
    elif attr_count >= 3:
        score_breakdown["attribute_completeness"] = 10
        score_breakdown["details"]["attributes"] = f"{attr_count} attributes (acceptable)"
    else:
        score_breakdown["attribute_completeness"] = 5
        score_breakdown["details"]["attributes"] = f"{attr_count} attributes (poor)"

    # 3. Semantic Richness (20 points)
    description = enriched_data.get("long_description", "")
    word_count = len(description.split())
    faqs = enriched_data.get("faqs", [])
    faq_count = len(faqs)

    desc_score = 0
    if 150 <= word_count <= 200:
        desc_score = 10
    elif 120 <= word_count < 150 or 200 < word_count <= 250:
        desc_score = 7
    elif word_count > 0:
        desc_score = 5

    faq_score = 0
    if faq_count >= 5:
        faq_score = 10
    elif faq_count >= 3:
        faq_score = 7
    elif faq_count > 0:
        faq_score = 5

    score_breakdown["semantic_richness"] = desc_score + faq_score
    score_breakdown["details"]["semantic"] = f"{word_count} words, {faq_count} FAQs"

    # 4. Structured Data (20 points)
    tags = enriched_data.get("semantic_tags", [])
    use_cases = enriched_data.get("use_cases", [])

    tags_score = min(len(tags) * 2, 10)  # Up to 10 points
    use_cases_score = min(len(use_cases) * 3, 10)  # Up to 10 points

    score_breakdown["structured_data"] = tags_score + use_cases_score
    score_breakdown["details"]["structured"] = f"{len(tags)} tags, {len(use_cases)} use cases"

    # 5. Consistency (20 points)
    consistency_score = 20  # Start with full points
    original_title = product_data.get("raw_title", "").lower()
    enriched_title = title.lower()

    # Check brand consistency
    brand = product_data.get("brand", "").lower()
    if brand and brand not in enriched_title and brand in original_title:
        consistency_score -= 5
        score_breakdown["details"]["consistency"] = "Brand missing from enriched title"

    # Check category alignment
    category = product_data.get("category", "").lower()
    if category and category not in description.lower():
        consistency_score -= 5
        if "consistency" in score_breakdown["details"]:
            score_breakdown["details"]["consistency"] += ", category not mentioned"
        else:
            score_breakdown["details"]["consistency"] = "Category not mentioned in description"

    if consistency_score == 20:
        score_breakdown["details"]["consistency"] = "Excellent alignment"

    score_breakdown["consistency"] = max(consistency_score, 0)

    # Calculate total score
    total_score = (
        score_breakdown["title_optimization"] +
        score_breakdown["attribute_completeness"] +
        score_breakdown["semantic_richness"] +
        score_breakdown["structured_data"] +
        score_breakdown["consistency"]
    )

    return total_score, score_breakdown
