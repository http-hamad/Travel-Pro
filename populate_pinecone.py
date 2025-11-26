"""Script to populate Pinecone with sample travel preference data"""
import config
from openai import OpenAI
from pinecone import Pinecone
from typing import List, Dict, Any
import time


class PineconeDataIngestion:
    """Handles ingestion of travel preference data into Pinecone"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self._ensure_index_exists()
        try:
            self.index = self.pc.Index(config.PINECONE_INDEX_NAME)
            print(f"Connected to Pinecone index: {config.PINECONE_INDEX_NAME}")
        except Exception as e:
            print(f"Error connecting to Pinecone: {e}")
            raise
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist, or recreate if dimensions don't match"""
        try:
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if config.PINECONE_INDEX_NAME in existing_indexes:
                # Check if dimensions match
                try:
                    index_info = self.pc.describe_index(config.PINECONE_INDEX_NAME)
                    if hasattr(index_info, 'dimension') and index_info.dimension != config.PINECONE_DIMENSIONS:
                        print(f"Index exists but has wrong dimensions ({index_info.dimension} vs {config.PINECONE_DIMENSIONS})")
                        print(f"Deleting and recreating index '{config.PINECONE_INDEX_NAME}'...")
                        self.pc.delete_index(config.PINECONE_INDEX_NAME)
                        # Wait for deletion
                        time.sleep(2)
                    else:
                        print(f"Index '{config.PINECONE_INDEX_NAME}' already exists with correct dimensions")
                        return
                except:
                    pass
            
            if config.PINECONE_INDEX_NAME not in existing_indexes:
                print(f"Index '{config.PINECONE_INDEX_NAME}' does not exist. Creating it...")
            
            self.pc.create_index(
                name=config.PINECONE_INDEX_NAME,
                dimension=config.PINECONE_DIMENSIONS,
                metric=config.PINECONE_METRIC,
                spec={
                    "serverless": {
                        "cloud": "aws",
                        "region": "us-east-1"
                    }
                }
            )
            print(f"✓ Created index '{config.PINECONE_INDEX_NAME}' with dimension {config.PINECONE_DIMENSIONS}")
            # Wait a bit for index to be ready
            print("Waiting for index to be ready...")
            time.sleep(5)
        except Exception as e:
            print(f"Error checking/creating index: {e}")
            print("Note: You may need to create the index manually in Pinecone console")
            raise
    
    def get_sample_preferences(self) -> List[Dict[str, Any]]:
        """Get sample travel preference data"""
        return [
            {
                "id": "pref_001",
                "text": "I want a luxury beach vacation in the Caribbean with fine dining and spa services",
                "preferences": ["luxury", "beach", "spa", "fine dining", "relaxation"],
                "travel_style": "luxury",
                "destination_type": "beach",
                "activities": ["spa", "fine dining", "water sports"]
            },
            {
                "id": "pref_002",
                "text": "Budget-friendly city trip to explore museums, art galleries, and local street food",
                "preferences": ["budget", "museums", "art", "street food", "culture"],
                "travel_style": "budget",
                "destination_type": "city",
                "activities": ["museums", "art galleries", "street food", "walking tours"]
            },
            {
                "id": "pref_003",
                "text": "Adventure trip with hiking, mountain climbing, and outdoor activities",
                "preferences": ["adventure", "hiking", "mountains", "outdoor", "active"],
                "travel_style": "adventure",
                "destination_type": "mountain",
                "activities": ["hiking", "climbing", "camping", "nature"]
            },
            {
                "id": "pref_004",
                "text": "Romantic getaway with wine tasting, sunset views, and intimate restaurants",
                "preferences": ["romantic", "wine", "sunset", "intimate dining", "couples"],
                "travel_style": "luxury",
                "destination_type": "romantic",
                "activities": ["wine tasting", "sunset viewing", "fine dining", "couples activities"]
            },
            {
                "id": "pref_005",
                "text": "Family-friendly vacation with theme parks, kid activities, and comfortable hotels",
                "preferences": ["family", "theme parks", "kids", "comfortable", "entertainment"],
                "travel_style": "moderate",
                "destination_type": "family",
                "activities": ["theme parks", "family activities", "kid-friendly attractions"]
            },
            {
                "id": "pref_006",
                "text": "Business trip with convenient location, good WiFi, and meeting facilities",
                "preferences": ["business", "convenient", "WiFi", "meetings", "efficient"],
                "travel_style": "moderate",
                "destination_type": "business",
                "activities": ["business meetings", "networking", "work"]
            },
            {
                "id": "pref_007",
                "text": "Cultural immersion trip to experience local traditions, festivals, and authentic cuisine",
                "preferences": ["culture", "traditions", "festivals", "local food", "authentic"],
                "travel_style": "moderate",
                "destination_type": "cultural",
                "activities": ["cultural sites", "festivals", "local experiences", "cooking classes"]
            },
            {
                "id": "pref_008",
                "text": "Solo backpacking trip with hostels, budget food, and meeting other travelers",
                "preferences": ["solo", "backpacking", "hostels", "budget", "social"],
                "travel_style": "budget",
                "destination_type": "backpacking",
                "activities": ["hostels", "budget travel", "meeting travelers", "exploration"]
            },
            {
                "id": "pref_009",
                "text": "Luxury safari experience with wildlife viewing, luxury lodges, and guided tours",
                "preferences": ["luxury", "safari", "wildlife", "nature", "guided tours"],
                "travel_style": "luxury",
                "destination_type": "safari",
                "activities": ["wildlife viewing", "safari", "nature photography", "luxury lodges"]
            },
            {
                "id": "pref_010",
                "text": "Relaxing spa retreat with yoga, meditation, healthy food, and wellness activities",
                "preferences": ["relaxation", "spa", "yoga", "meditation", "wellness", "healthy"],
                "travel_style": "moderate",
                "destination_type": "wellness",
                "activities": ["spa", "yoga", "meditation", "wellness", "healthy dining"]
            },
            {
                "id": "pref_011",
                "text": "Foodie tour focusing on Michelin-starred restaurants, local markets, and cooking classes",
                "preferences": ["food", "fine dining", "Michelin", "markets", "cooking"],
                "travel_style": "luxury",
                "destination_type": "culinary",
                "activities": ["fine dining", "food markets", "cooking classes", "food tours"]
            },
            {
                "id": "pref_012",
                "text": "Weekend city break with shopping, nightlife, trendy restaurants, and modern hotels",
                "preferences": ["shopping", "nightlife", "trendy", "modern", "urban"],
                "travel_style": "moderate",
                "destination_type": "city",
                "activities": ["shopping", "nightlife", "trendy restaurants", "urban exploration"]
            }
        ]
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = []
        
        # Process in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=config.EMBEDDING_MODEL,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                print(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                time.sleep(0.1)  # Small delay to avoid rate limits
            except Exception as e:
                print(f"Error generating embeddings for batch: {e}")
                raise
        
        return embeddings
    
    def upsert_to_pinecone(self, preferences: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Upsert preferences with embeddings to Pinecone"""
        print(f"Upserting {len(preferences)} records to Pinecone...")
        
        vectors_to_upsert = []
        for pref, embedding in zip(preferences, embeddings):
            vector_data = {
                "id": pref["id"],
                "values": embedding,
                "metadata": {
                    "text": pref["text"],
                    "preferences": pref["preferences"],
                    "travel_style": pref["travel_style"],
                    "destination_type": pref["destination_type"],
                    "activities": pref["activities"]
                }
            }
            vectors_to_upsert.append(vector_data)
        
        # Upsert in batches (Pinecone recommends batches of 100)
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
            except Exception as e:
                print(f"Error upserting batch: {e}")
                raise
        
        print(f"Successfully upserted {len(vectors_to_upsert)} records to Pinecone!")
    
    def verify_ingestion(self, sample_text: str = "luxury beach vacation"):
        """Verify that data was ingested correctly by querying"""
        print(f"\nVerifying ingestion with sample query: '{sample_text}'...")
        
        try:
            # Generate embedding for sample text
            response = self.client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=sample_text
            )
            query_embedding = response.data[0].embedding
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True
            )
            
            if results.matches:
                print(f"✓ Found {len(results.matches)} similar preferences:")
                for i, match in enumerate(results.matches, 1):
                    print(f"\n  {i}. ID: {match.id}")
                    print(f"     Score: {match.score:.4f}")
                    print(f"     Text: {match.metadata.get('text', 'N/A')}")
                    print(f"     Preferences: {match.metadata.get('preferences', [])}")
                return True
            else:
                print("✗ No matches found")
                return False
        except Exception as e:
            print(f"✗ Error verifying ingestion: {e}")
            return False
    
    def populate(self):
        """Main method to populate Pinecone with sample data"""
        print("=" * 60)
        print("Pinecone Data Ingestion")
        print("=" * 60)
        print()
        
        # Get sample preferences
        preferences = self.get_sample_preferences()
        print(f"Prepared {len(preferences)} sample travel preferences")
        print()
        
        # Generate embeddings
        texts = [pref["text"] for pref in preferences]
        embeddings = self.generate_embeddings(texts)
        print()
        
        # Upsert to Pinecone
        self.upsert_to_pinecone(preferences, embeddings)
        print()
        
        # Verify ingestion
        success = self.verify_ingestion()
        print()
        
        if success:
            print("=" * 60)
            print("✓ Data ingestion completed successfully!")
            print("=" * 60)
        else:
            print("=" * 60)
            print("⚠ Data ingestion completed but verification failed")
            print("=" * 60)


def main():
    """Main function to run data ingestion"""
    try:
        ingestion = PineconeDataIngestion()
        ingestion.populate()
    except Exception as e:
        print(f"Error during data ingestion: {e}")
        print("\nNote: Make sure your Pinecone index exists and is accessible.")


if __name__ == "__main__":
    main()

