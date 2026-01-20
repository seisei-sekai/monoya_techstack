import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from app.core.config import settings
import os

db = None

class MockFirestore:
    """Mock Firestore for development"""
    def __init__(self):
        self._data = {}
    
    def collection(self, name):
        if name not in self._data:
            self._data[name] = MockCollection(name)
        return self._data[name]

class MockCollection:
    def __init__(self, name):
        self.name = name
        self._docs = {}
        self._counter = 0
    
    def document(self, doc_id=None):
        # Auto-generate ID if not provided
        if doc_id is None:
            self._counter += 1
            doc_id = f"mock_doc_{self._counter}"
        
        if doc_id not in self._docs:
            self._docs[doc_id] = MockDocument(doc_id, self)
        return self._docs[doc_id]
    
    def stream(self):
        return list(self._docs.values())
    
    def where(self, field, op, value):
        # Store filter but return all docs for simplicity in dev mode
        query = MockQuery(self, [(field, op, value)])
        return query

class MockQuery:
    def __init__(self, collection, filters=None):
        self.collection = collection
        self.filters = filters or []
        self._order = None
        self._limit_count = None
    
    def order_by(self, *args, **kwargs):
        self._order = (args, kwargs)
        return self
    
    def limit(self, count):
        self._limit_count = count
        return self
    
    def stream(self):
        # Return all documents from the collection
        docs = []
        for doc_id, doc in self.collection._docs.items():
            if doc._data:  # Only return docs with data
                docs.append(MockDocSnapshot(doc_id, doc._data))
        return docs
    
    def get(self):
        return self.stream()

class MockDocument:
    def __init__(self, doc_id, collection):
        self.id = doc_id
        self.collection = collection
        self._data = {}
    
    def get(self):
        return MockDocSnapshot(self.id, self._data)
    
    def set(self, data):
        self._data = data
    
    def update(self, data):
        self._data.update(data)
    
    def delete(self):
        if self.id in self.collection._docs:
            del self.collection._docs[self.id]

class MockDocSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
    
    def exists(self):
        return bool(self._data)
    
    def to_dict(self):
        return self._data

def initialize_firebase():
    """Initialize Firebase Admin SDK or return mock for dev mode"""
    global db
    
    # Development mode - use mock
    if settings.dev_mode:
        print("🔧 Running in DEV MODE - Using mock Firestore")
        db = MockFirestore()
        return db
    
    # Production mode - use real Firebase
    if not firebase_admin._apps:
        # Check if service account file exists and is a file (not directory)
        cred_path = settings.google_application_credentials
        if os.path.isfile(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            # For local development without service account
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred, {
            'projectId': settings.firebase_project_id,
        })
    
    db = firestore.client()
    return db

def get_firestore_db():
    """Get Firestore database instance"""
    global db
    if db is None:
        db = initialize_firebase()
    return db

async def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token and return decoded token"""
    # Development mode - mock authentication
    if settings.dev_mode:
        return {
            "uid": "dev-user-123",
            "email": "dev@example.com",
            "name": "Dev User"
        }
    
    # Production mode - real verification
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid authentication token: {str(e)}")

