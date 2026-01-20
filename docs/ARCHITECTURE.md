# Architecture Documentation

## System Overview

AI Diary is a cloud-native, full-stack web application that provides users with an intelligent journaling experience. The system leverages modern technologies including React, FastAPI, Firebase, OpenAI, and Weaviate to deliver personalized AI insights based on diary history.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│                  (React + TypeScript + Tailwind)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTPS
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Cloud Run - Frontend                       │
│                   (Static Content Serving)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ REST API
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Cloud Run - Backend                        │
│                      (FastAPI)                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  API Layer (FastAPI Routes)                        │    │
│  │  - Authentication Middleware                       │    │
│  │  - Request Validation                              │    │
│  │  - Error Handling                                  │    │
│  └────────────────────┬───────────────────────────────┘    │
│  ┌────────────────────▼───────────────────────────────┐    │
│  │  Service Layer                                      │    │
│  │  - Diary Service (CRUD operations)                 │    │
│  │  - RAG Service (AI insights generation)            │    │
│  └──────┬─────────────────────────────────────┬───────┘    │
└─────────┼─────────────────────────────────────┼────────────┘
          │                                     │
          │                                     │
     ┌────▼────┐                          ┌────▼─────┐
     │Firebase │                          │ Weaviate │
     │ Auth &  │                          │  Vector  │
     │Firestore│                          │    DB    │
     └─────────┘                          └────┬─────┘
                                               │
                                          ┌────▼─────┐
                                          │  OpenAI  │
                                          │   API    │
                                          └──────────┘
```

## Component Details

### 1. Frontend (React + TypeScript)

**Technology Stack:**
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Zustand for state management
- React Router for navigation
- Axios for HTTP requests
- Firebase SDK for authentication

**Key Components:**

```
src/
├── pages/
│   ├── Login.tsx          # Authentication page
│   ├── Dashboard.tsx      # Diary list view
│   └── DiaryEditor.tsx    # Create/edit diary
├── api/
│   ├── client.ts          # Axios instance with auth interceptor
│   └── diaries.ts         # Diary API endpoints
├── store/
│   └── authStore.ts       # Global auth state
├── config/
│   └── firebase.ts        # Firebase initialization
└── types/
    └── diary.ts           # TypeScript interfaces
```

**Authentication Flow:**
1. User enters credentials
2. Firebase Auth validates and returns ID token
3. Token stored in memory and attached to all API requests
4. Backend verifies token on each request

### 2. Backend (FastAPI)

**Technology Stack:**
- FastAPI (Python 3.11)
- Firebase Admin SDK
- OpenAI Python SDK
- Weaviate Python Client
- Pydantic for data validation
- Uvicorn ASGI server

**Architecture Layers:**

```
app/
├── main.py                    # FastAPI application entry
├── api/
│   ├── dependencies.py        # Auth dependency injection
│   └── routes/
│       └── diaries.py         # Diary endpoints
├── services/
│   ├── diary_service.py       # Business logic
│   └── rag_service.py         # RAG implementation
├── models/
│   └── diary.py               # Pydantic models
└── core/
    ├── config.py              # Configuration management
    ├── firebase.py            # Firebase client
    └── weaviate_client.py     # Weaviate client
```

**API Endpoints:**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API info | No |
| GET | `/health` | Health check | No |
| GET | `/diaries` | List user's diaries | Yes |
| POST | `/diaries` | Create diary | Yes |
| GET | `/diaries/{id}` | Get diary | Yes |
| PUT | `/diaries/{id}` | Update diary | Yes |
| DELETE | `/diaries/{id}` | Delete diary | Yes |
| POST | `/diaries/{id}/ai-insight` | Generate AI insight | Yes |

### 3. Authentication & Authorization

**Firebase Authentication:**
- Email/password authentication
- JWT token-based session management
- Secure token refresh mechanism

**Backend Verification:**
```python
# Middleware verifies Firebase ID token
async def get_current_user(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    decoded_token = firebase_auth.verify_id_token(token)
    return decoded_token  # Contains uid, email, etc.
```

**Authorization:**
- User can only access their own diaries
- Firestore security rules enforce access control
- Backend double-checks ownership on all operations

### 4. Data Storage

#### Firestore (Primary Database)

**Schema:**
```javascript
// Collection: diaries
{
  "diaryId": "auto-generated",
  "userId": "firebase-uid",
  "title": "string",
  "content": "string",
  "createdAt": "timestamp",
  "updatedAt": "timestamp",
  "aiInsight": "string | null"
}
```

**Indexes:**
- Composite: (userId, createdAt DESC)
- Single: userId

**Security Rules:**
```javascript
// Users can only read/write their own diaries
match /diaries/{diaryId} {
  allow read, write: if request.auth.uid == resource.data.userId;
}
```

#### Weaviate (Vector Database)

**Purpose:** Semantic search for RAG

**Schema:**
```javascript
{
  "class": "DiaryEntry",
  "properties": [
    {"name": "diaryId", "dataType": ["string"]},
    {"name": "userId", "dataType": ["string"]},
    {"name": "title", "dataType": ["string"]},
    {"name": "content", "dataType": ["text"]},
    {"name": "createdAt", "dataType": ["string"]}
  ]
}
```

**Vector Embeddings:**
- Generated using OpenAI's `text-embedding-ada-002`
- Input: `{title}\n\n{content}`
- Dimensions: 1536

### 5. RAG System (Retrieval-Augmented Generation)

**Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    RAG Pipeline                          │
│                                                          │
│  1. User requests AI insight for diary X               │
│           │                                              │
│           ▼                                              │
│  2. Generate embedding for diary X content             │
│           │ (OpenAI text-embedding-ada-002)             │
│           ▼                                              │
│  3. Search Weaviate for similar past diaries           │
│           │ (Vector similarity search)                  │
│           ▼                                              │
│  4. Retrieve top 3 most similar diaries                │
│           │                                              │
│           ▼                                              │
│  5. Build context with current + past diaries          │
│           │                                              │
│           ▼                                              │
│  6. Generate insight using GPT-3.5                     │
│           │ (OpenAI chat completion)                    │
│           ▼                                              │
│  7. Store insight in Firestore                         │
│           │                                              │
│           ▼                                              │
│  8. Return insight to user                             │
└─────────────────────────────────────────────────────────┘
```

**Implementation Details:**

```python
async def generate_insight(current_diary, user_id):
    # 1. Embed current diary
    embedding = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=f"{current_diary.title}\n\n{current_diary.content}"
    )
    
    # 2. Search similar diaries
    similar = weaviate.query.get("DiaryEntry")
        .with_near_vector({"vector": embedding.data[0].embedding})
        .with_where({"path": ["userId"], "operator": "Equal", "valueString": user_id})
        .with_limit(5)
        .do()
    
    # 3. Build context
    context = build_context(current_diary, similar)
    
    # 4. Generate insight
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a compassionate AI journal companion..."},
            {"role": "user", "content": context}
        ]
    )
    
    return response.choices[0].message.content
```

**Prompt Engineering:**
- System prompt defines AI persona (compassionate companion)
- User prompt includes current entry + past similar entries
- Temperature: 0.7 (balanced creativity/consistency)
- Max tokens: 200 (concise insights)

### 6. Infrastructure (GCP)

**Services Used:**

| Service | Purpose | Configuration |
|---------|---------|---------------|
| Cloud Run | Serverless container hosting | Auto-scaling 0-10 instances |
| Artifact Registry | Docker image storage | Regional repository |
| Firestore | Primary database | Native mode, us-central |
| Firebase Auth | User authentication | Email/password provider |
| Cloud Build | CI/CD pipeline | Automated deployments |
| Cloud Logging | Centralized logging | 30-day retention |

**Network Architecture:**
- All services communicate over HTTPS
- Cloud Run services have internal URLs
- Frontend and backend have public URLs
- Weaviate is internal-only (accessed by backend)

**Security:**
- Service accounts with minimal permissions
- Secrets stored in environment variables
- TLS/SSL for all communications
- CORS configured for frontend domain
- Firestore security rules enforced

### 7. CI/CD Pipeline

**GitHub Actions Workflows:**

```
┌──────────────────────────────────────────────────────┐
│           Push to main branch                        │
└───────────────────┬──────────────────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  Run Tests          │
         │  - Lint frontend    │
         │  - Lint backend     │
         │  - Build checks     │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Build Images       │
         │  - Backend Docker   │
         │  - Frontend Docker  │
         │  - Tag with SHA     │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Push to Registry   │
         │  - Artifact Registry│
         │  - Tag latest       │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Deploy to Cloud Run│
         │  - Update backend   │
         │  - Update frontend  │
         │  - Health checks    │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Notify Success     │
         │  - Get service URLs │
         │  - Update status    │
         └─────────────────────┘
```

## Data Flow

### Creating a Diary Entry

```
1. User writes diary in frontend
2. Frontend POSTs to /diaries with title & content
3. Backend verifies Firebase token
4. Backend saves to Firestore
5. Backend creates embedding and stores in Weaviate
6. Backend returns diary object to frontend
7. Frontend updates UI with new diary
```

### Generating AI Insight

```
1. User clicks "Get AI Insight" button
2. Frontend POSTs to /diaries/{id}/ai-insight
3. Backend retrieves diary from Firestore
4. Backend generates embedding for diary
5. Backend searches Weaviate for similar past diaries
6. Backend builds context with current + past diaries
7. Backend calls OpenAI to generate insight
8. Backend stores insight in Firestore
9. Backend returns insight to frontend
10. Frontend displays insight to user
```

## Performance Considerations

### Caching Strategy
- Frontend: React component memoization
- Backend: Weaviate client connection pooling
- Database: Firestore automatic caching

### Optimization
- Frontend: Code splitting, lazy loading
- Backend: Async/await throughout
- Database: Indexed queries, batch operations
- CDN: Cloud Run automatic edge caching

### Scalability
- Horizontal: Cloud Run auto-scaling
- Vertical: Configurable CPU/memory limits
- Database: Firestore handles millions of operations
- Vector DB: Weaviate scales with data volume

## Monitoring & Observability

### Logging
- Cloud Logging for all services
- Structured JSON logs
- Request/response logging
- Error stack traces

### Metrics
- Cloud Run built-in metrics
- Request count, latency, errors
- Cold start tracking
- Cost monitoring

### Alerting
- Error rate thresholds
- Response time SLAs
- Cost budget alerts
- Quota monitoring

## Security Architecture

### Defense in Depth
1. **Network:** HTTPS only, CORS restrictions
2. **Authentication:** Firebase JWT verification
3. **Authorization:** User-specific data access
4. **Database:** Security rules enforcement
5. **Secrets:** Environment variables, no hardcoding
6. **Infrastructure:** IAM roles, service accounts

### Data Protection
- In-transit: TLS 1.2+
- At-rest: GCP default encryption
- Backups: Firestore automatic
- Audit: Cloud Logging

## Disaster Recovery

### Backup Strategy
- Firestore: Automatic daily backups
- Weaviate: Volume snapshots (if persistent)
- Code: Git version control
- Infrastructure: Terraform state

### Recovery Procedures
1. Service outage: Cloud Run auto-restarts
2. Data corruption: Restore from Firestore backup
3. Complete failure: Terraform redeploy
4. Rollback: Deploy previous container image

## Future Enhancements

### Planned Features
- Mobile app (React Native)
- Advanced analytics dashboard
- Export diaries to PDF
- Voice-to-text diary entry
- Multi-language support
- Sentiment analysis
- Daily reminder notifications

### Scalability Improvements
- Redis caching layer
- GraphQL API
- CDN for static assets
- Multi-region deployment
- Database sharding

### AI Enhancements
- Fine-tuned model on user data
- Mood tracking over time
- Goal setting and tracking
- Writing prompt suggestions
- Theme detection

## Conclusion

This architecture provides a scalable, secure, and maintainable foundation for the AI Diary application. The use of modern cloud-native technologies ensures reliability and performance while the RAG system delivers personalized AI insights that improve over time.

