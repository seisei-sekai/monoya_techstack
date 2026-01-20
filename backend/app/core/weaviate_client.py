import weaviate
from app.core.config import settings

_client = None

def get_weaviate_client():
    """Get or create Weaviate client instance"""
    global _client
    if _client is None:
        _client = weaviate.Client(
            url=settings.weaviate_url,
        )
        
        # Create schema if it doesn't exist
        _initialize_schema(_client)
    
    return _client

def _initialize_schema(client: weaviate.Client):
    """Initialize Weaviate schema for diary entries"""
    schema = {
        "classes": [
            {
                "class": "DiaryEntry",
                "description": "A diary entry with its content",
                "properties": [
                    {
                        "name": "diaryId",
                        "dataType": ["string"],
                        "description": "The diary entry ID from Firestore"
                    },
                    {
                        "name": "userId",
                        "dataType": ["string"],
                        "description": "The user ID who owns this diary"
                    },
                    {
                        "name": "title",
                        "dataType": ["string"],
                        "description": "The title of the diary entry"
                    },
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "The content of the diary entry"
                    },
                    {
                        "name": "createdAt",
                        "dataType": ["string"],
                        "description": "Timestamp when entry was created"
                    }
                ]
            }
        ]
    }
    
    # Check if class already exists
    try:
        existing_schema = client.schema.get()
        class_names = [c["class"] for c in existing_schema.get("classes", [])]
        
        if "DiaryEntry" not in class_names:
            client.schema.create(schema)
    except Exception as e:
        print(f"Schema initialization error: {e}")

