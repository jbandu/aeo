import networkx as nx
import json
import sqlite3
from typing import Dict, List, Any, Tuple
import anthropic
import os

class KnowledgeGraphService:
    """Service for managing product knowledge graph using NetworkX."""

    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def build_graph_from_db(self, conn: sqlite3.Connection):
        """Build the in-memory graph from database."""
        self.graph.clear()

        # Add product nodes
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.sku, p.raw_title, p.category, p.brand, p.price,
                   e.enriched_title, e.semantic_tags
            FROM products p
            LEFT JOIN enriched_products e ON p.id = e.product_id
        """)

        for row in cursor.fetchall():
            self.graph.add_node(
                row['id'],
                node_type='product',
                sku=row['sku'],
                title=row['enriched_title'] or row['raw_title'],
                category=row['category'],
                brand=row['brand'],
                price=row['price'],
                semantic_tags=json.loads(row['semantic_tags']) if row['semantic_tags'] else []
            )

        # Add category nodes
        cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL")
        for row in cursor.fetchall():
            category = row['category']
            if category:
                self.graph.add_node(
                    f"category_{category}",
                    node_type='category',
                    name=category
                )

        # Add brand nodes
        cursor.execute("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL")
        for row in cursor.fetchall():
            brand = row['brand']
            if brand:
                self.graph.add_node(
                    f"brand_{brand}",
                    node_type='brand',
                    name=brand
                )

        # Add product relationships
        cursor.execute("""
            SELECT source_product_id, target_product_id, relationship_type,
                   similarity_score, reasoning
            FROM product_relationships
        """)

        for row in cursor.fetchall():
            self.graph.add_edge(
                row['source_product_id'],
                row['target_product_id'],
                relationship_type=row['relationship_type'],
                similarity_score=row['similarity_score'],
                reasoning=row['reasoning']
            )

        # Add BELONGS_TO edges (Product → Category)
        cursor.execute("SELECT id, category FROM products WHERE category IS NOT NULL")
        for row in cursor.fetchall():
            if row['category']:
                self.graph.add_edge(
                    row['id'],
                    f"category_{row['category']}",
                    relationship_type='BELONGS_TO'
                )

        # Add MADE_BY edges (Product → Brand)
        cursor.execute("SELECT id, brand FROM products WHERE brand IS NOT NULL")
        for row in cursor.fetchall():
            if row['brand']:
                self.graph.add_edge(
                    row['id'],
                    f"brand_{row['brand']}",
                    relationship_type='MADE_BY'
                )

        return self.graph

    async def analyze_product_relationships(
        self,
        product_id: int,
        conn: sqlite3.Connection
    ) -> List[Dict[str, Any]]:
        """
        Use Claude to analyze product relationships with other products in the catalog.

        Returns list of relationships with structure:
        {
            "target_product_id": int,
            "relationship_type": "SIMILAR_TO" | "COMPLEMENTS" | "ALTERNATIVE_TO",
            "similarity_score": float,
            "reasoning": str
        }
        """
        if not self.client:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        cursor = conn.cursor()

        # Get source product
        cursor.execute("""
            SELECT p.*, e.enriched_title, e.long_description, e.semantic_tags, e.key_attributes
            FROM products p
            LEFT JOIN enriched_products e ON p.id = e.product_id
            WHERE p.id = ?
        """, (product_id,))

        source_row = cursor.fetchone()
        if not source_row:
            raise ValueError(f"Product {product_id} not found")

        source_product = {
            'id': source_row['id'],
            'sku': source_row['sku'],
            'title': source_row['enriched_title'] or source_row['raw_title'],
            'description': source_row['long_description'] or source_row['raw_description'],
            'category': source_row['category'],
            'brand': source_row['brand'],
            'price': source_row['price'],
            'semantic_tags': json.loads(source_row['semantic_tags']) if source_row['semantic_tags'] else [],
            'attributes': json.loads(source_row['key_attributes']) if source_row['key_attributes'] else []
        }

        # Get all other products
        cursor.execute("""
            SELECT p.id, p.sku, p.raw_title, p.category, p.brand, p.price,
                   e.enriched_title, e.long_description, e.semantic_tags
            FROM products p
            LEFT JOIN enriched_products e ON p.id = e.product_id
            WHERE p.id != ?
            ORDER BY p.id
            LIMIT 20
        """, (product_id,))

        other_products = []
        for row in cursor.fetchall():
            other_products.append({
                'id': row['id'],
                'sku': row['sku'],
                'title': row['enriched_title'] or row['raw_title'],
                'description': row['long_description'],
                'category': row['category'],
                'brand': row['brand'],
                'price': row['price'],
                'semantic_tags': json.loads(row['semantic_tags']) if row['semantic_tags'] else []
            })

        # Build prompt for Claude
        prompt = self._build_relationship_analysis_prompt(source_product, other_products)

        # Call Claude API
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text
            relationships = json.loads(response_text)

            # Store relationships in database
            for rel in relationships:
                self._store_relationship(
                    conn,
                    source_product['id'],
                    rel['target_product_id'],
                    rel['relationship_type'],
                    rel.get('similarity_score', 0.5),
                    rel.get('reasoning', '')
                )

            conn.commit()

            # Rebuild graph to include new relationships
            self.build_graph_from_db(conn)

            return relationships

        except Exception as e:
            conn.rollback()
            raise Exception(f"Relationship analysis failed: {str(e)}")

    def _build_relationship_analysis_prompt(
        self,
        source_product: Dict[str, Any],
        other_products: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for Claude to analyze product relationships."""

        prompt = f"""You are an expert in e-commerce product categorization and relationship analysis. Analyze the following source product and identify relationships with other products in the catalog.

SOURCE PRODUCT:
ID: {source_product['id']}
SKU: {source_product['sku']}
Title: {source_product['title']}
Description: {source_product['description'] or 'N/A'}
Category: {source_product['category']}
Brand: {source_product['brand']}
Price: ${source_product['price']}
Tags: {', '.join(source_product['semantic_tags'])}

OTHER PRODUCTS IN CATALOG:
"""

        for prod in other_products:
            prompt += f"""
- ID {prod['id']}: {prod['title']} | Category: {prod['category']} | Brand: {prod['brand']} | Price: ${prod['price']}
"""

        prompt += """

Analyze the source product and identify up to 5 meaningful relationships with other products. For each relationship, specify:

1. **SIMILAR_TO**: Products that are functionally similar or serve the same purpose (e.g., two different wireless earbuds)
2. **COMPLEMENTS**: Products that work well together or complement each other (e.g., phone and phone case)
3. **ALTERNATIVE_TO**: Products that are alternatives at different price points or from different brands

Return ONLY a valid JSON array with this structure (no markdown formatting, no code blocks):

[
  {
    "target_product_id": 2,
    "relationship_type": "SIMILAR_TO",
    "similarity_score": 0.85,
    "reasoning": "Both are wireless earbuds with noise cancellation features"
  },
  {
    "target_product_id": 5,
    "relationship_type": "COMPLEMENTS",
    "similarity_score": 0.70,
    "reasoning": "Phone case complements the smartphone"
  }
]

Rules:
- Only include relationships with similarity_score >= 0.5
- Maximum 5 relationships
- similarity_score should be between 0.0 and 1.0
- Provide clear reasoning for each relationship
- If no strong relationships exist, return an empty array []

Respond ONLY with the JSON array:"""

        return prompt

    def _store_relationship(
        self,
        conn: sqlite3.Connection,
        source_id: int,
        target_id: int,
        rel_type: str,
        score: float,
        reasoning: str
    ):
        """Store a relationship in the database."""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO product_relationships
            (source_product_id, target_product_id, relationship_type, similarity_score, reasoning)
            VALUES (?, ?, ?, ?, ?)
        """, (source_id, target_id, rel_type, score, reasoning))

    def get_product_relationships(
        self,
        product_id: int,
        conn: sqlite3.Connection
    ) -> List[Dict[str, Any]]:
        """Get all relationships for a product."""
        cursor = conn.cursor()

        # Get outgoing relationships
        cursor.execute("""
            SELECT
                pr.target_product_id,
                pr.relationship_type,
                pr.similarity_score,
                pr.reasoning,
                p.sku,
                p.raw_title,
                e.enriched_title,
                p.category,
                p.brand,
                p.price
            FROM product_relationships pr
            JOIN products p ON pr.target_product_id = p.id
            LEFT JOIN enriched_products e ON p.id = e.product_id
            WHERE pr.source_product_id = ?
        """, (product_id,))

        relationships = []
        for row in cursor.fetchall():
            relationships.append({
                'product_id': row['target_product_id'],
                'sku': row['sku'],
                'title': row['enriched_title'] or row['raw_title'],
                'category': row['category'],
                'brand': row['brand'],
                'price': row['price'],
                'relationship_type': row['relationship_type'],
                'similarity_score': row['similarity_score'],
                'reasoning': row['reasoning']
            })

        return relationships

    def get_recommendations(
        self,
        product_id: int,
        conn: sqlite3.Connection,
        limit: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get product recommendations based on graph relationships.

        Returns recommendations grouped by relationship type.
        """
        relationships = self.get_product_relationships(product_id, conn)

        recommendations = {
            'similar': [],
            'complements': [],
            'alternatives': []
        }

        for rel in relationships:
            if rel['relationship_type'] == 'SIMILAR_TO':
                recommendations['similar'].append(rel)
            elif rel['relationship_type'] == 'COMPLEMENTS':
                recommendations['complements'].append(rel)
            elif rel['relationship_type'] == 'ALTERNATIVE_TO':
                recommendations['alternatives'].append(rel)

        # Sort by similarity score and limit
        for key in recommendations:
            recommendations[key] = sorted(
                recommendations[key],
                key=lambda x: x['similarity_score'],
                reverse=True
            )[:limit]

        return recommendations

    def get_graph_visualization_data(
        self,
        product_id: int = None,
        conn: sqlite3.Connection = None
    ) -> Dict[str, Any]:
        """
        Get graph data in format suitable for visualization.

        Returns:
        {
            "nodes": [{"id": str, "label": str, "type": str, ...}],
            "links": [{"source": str, "target": str, "type": str, ...}]
        }
        """
        if conn:
            self.build_graph_from_db(conn)

        # If product_id specified, get subgraph centered on that product
        if product_id:
            # Get nodes within 2 hops of the product
            try:
                ego_graph = nx.ego_graph(self.graph.to_undirected(), product_id, radius=2)
                graph_to_visualize = ego_graph
            except nx.NetworkXError:
                graph_to_visualize = self.graph
        else:
            graph_to_visualize = self.graph

        # Build nodes array
        nodes = []
        for node_id, node_data in graph_to_visualize.nodes(data=True):
            node_type = node_data.get('node_type', 'unknown')

            if node_type == 'product':
                label = node_data.get('title', f"Product {node_id}")
                group = node_data.get('category', 'Unknown')
            elif node_type == 'category':
                label = node_data.get('name', str(node_id))
                group = 'Category'
            elif node_type == 'brand':
                label = node_data.get('name', str(node_id))
                group = 'Brand'
            else:
                label = str(node_id)
                group = 'Unknown'

            nodes.append({
                'id': str(node_id),
                'label': label,
                'type': node_type,
                'group': group,
                'data': node_data
            })

        # Build links array
        links = []
        for source, target, edge_data in graph_to_visualize.edges(data=True):
            links.append({
                'source': str(source),
                'target': str(target),
                'type': edge_data.get('relationship_type', 'UNKNOWN'),
                'score': edge_data.get('similarity_score', 0),
                'reasoning': edge_data.get('reasoning', '')
            })

        return {
            'nodes': nodes,
            'links': links
        }

    async def batch_analyze_all_products(
        self,
        conn: sqlite3.Connection,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Analyze relationships for all products in the catalog.

        Args:
            conn: Database connection
            progress_callback: Optional callback function for progress updates

        Returns summary statistics
        """
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM products")
        product_ids = [row['id'] for row in cursor.fetchall()]

        total = len(product_ids)
        processed = 0
        relationships_created = 0

        for product_id in product_ids:
            try:
                relationships = await self.analyze_product_relationships(product_id, conn)
                relationships_created += len(relationships)
                processed += 1

                if progress_callback:
                    progress_callback({
                        'product_id': product_id,
                        'processed': processed,
                        'total': total,
                        'relationships_found': len(relationships)
                    })

            except Exception as e:
                print(f"Error analyzing product {product_id}: {e}")
                processed += 1

        return {
            'total_products': total,
            'processed': processed,
            'total_relationships': relationships_created
        }
