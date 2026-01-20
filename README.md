# RAG AI Note System

React | FastAPI | Firebase | Weaviate | OpenAI | Terraform | GCP

A full-stack Retrieval-Augmented Generation note-taking system with semantic search and AI-powered insights.

---

## Disclaimer

This is a toy RAG full-stack project built as a technical demonstration based on Monoya job descriptions for the following roles:
- Full Stack Engineer: https://www.tokyodev.com/companies/monoya/jobs/full-stack-engineer
- AI/Machine Learning Engineer: https://www.tokyodev.com/companies/monoya/jobs/ai-machine-learning-engineer

This project does not reflect any actual product, service, or business operations. It is purely an educational and demonstrative implementation.

---

## Overview

AI Diary is a modern web application that combines personal journaling with artificial intelligence. The system uses Retrieval-Augmented Generation (RAG) technology to provide contextual insights based on your journal history.

### Core Features

- User authentication and secure access control
- Create, read, update, and delete diary entries
- AI-powered personalized insights based on journal history
- Semantic search using vector embeddings
- Modern, responsive user interface
- Cloud-native architecture with horizontal scalability

### Technology Stack

**Frontend**
- React with Vite build system
- Tailwind CSS for styling
- Firebase Authentication SDK
- Zustand for state management
- Axios for HTTP communication

**Backend**
- FastAPI Python framework
- Firebase Admin SDK
- OpenAI API integration
- Weaviate vector database
- Google Firestore for data persistence

**Infrastructure**
- Docker containerization
- Google Cloud Platform deployment
- Terraform infrastructure as code
- GitHub Actions CI/CD pipeline

---

## Getting Started

### Prerequisites

- Node.js 20 or higher
- Python 3.11 or higher
- Docker and Docker Compose
- Google Cloud Platform account
- Firebase project
- OpenAI API key

### Local Development

1. Clone the repository

```bash
git clone <repository-url>
cd JD_Project
```

2. Configure environment variables

```bash
cp env.example .env
```

Edit `.env` with your credentials for:
- Firebase configuration
- OpenAI API key
- Weaviate settings
- Backend API URL

3. Set up Firebase

- Create a project at https://console.firebase.google.com
- Enable Authentication with Email/Password provider
- Enable Firestore Database
- Download service account key as `service-account.json`
- Add Firebase configuration to `.env` file

4. Start the application

```bash
docker-compose up --build
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Weaviate Console: http://localhost:8080

### Manual Setup

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
JD_Project/
├── frontend/                 React application
│   ├── src/
│   │   ├── api/             API client layer
│   │   ├── config/          Configuration files
│   │   ├── pages/           Page components
│   │   └── store/           State management
│   ├── Dockerfile
│   └── package.json
│
├── backend/                  FastAPI application
│   ├── app/
│   │   ├── api/             Route handlers
│   │   ├── core/            Core configuration
│   │   ├── models/          Data models
│   │   └── services/        Business logic
│   ├── Dockerfile
│   └── requirements.txt
│
├── terraform/                Infrastructure as code
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── docs/                     Documentation
└── scripts/                  Deployment scripts
```

---

## API Documentation

### Endpoints

**Diary Management**
- `GET /diaries` - Retrieve all diary entries
- `POST /diaries` - Create new diary entry
- `GET /diaries/{id}` - Retrieve specific diary
- `PUT /diaries/{id}` - Update diary entry
- `DELETE /diaries/{id}` - Delete diary entry

**AI Features**
- `POST /diaries/{id}/ai-insight` - Generate AI insight

Authentication required for all endpoints via Firebase JWT token.

Full API documentation available at `/docs` endpoint when running the backend.

---

## Deployment

### Google Cloud Platform

1. Initialize Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

2. Build and push Docker images

```bash
export PROJECT_ID=your-project-id
gcloud auth configure-docker us-central1-docker.pkg.dev

# Backend
cd backend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest

# Frontend
cd frontend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest
```

3. Configure GitHub Actions

Set the following repository secrets:
- `GCP_PROJECT_ID`
- `GCP_SA_KEY`
- `OPENAI_API_KEY`
- `VITE_API_URL`
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`

Push to `main` branch to trigger automated deployment.

---

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- Architecture overview and system design
- Deployment guides for GCP
- Local development setup
- Weaviate configuration tutorial
- Terraform infrastructure guide
- RAG flow explanation

---

## Testing

**Frontend**

```bash
cd frontend
npm run lint
npm run build
```

**Backend**

```bash
cd backend
pip install pytest pytest-asyncio
pytest
```

---

## Security Considerations

- Firebase Authentication for identity management
- JWT token validation on all API endpoints
- Service accounts with principle of least privilege
- Environment variable management for secrets
- Firestore security rules for data access control

---

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes with clear messages
4. Push to your fork
5. Submit a pull request

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

## Support

For issues and questions, please use the GitHub issue tracker.

---

## References

- React: https://react.dev
- FastAPI: https://fastapi.tiangolo.com
- Firebase: https://firebase.google.com/docs
- OpenAI: https://platform.openai.com/docs
- Weaviate: https://weaviate.io/developers/weaviate
- Terraform: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- Google Cloud Run: https://cloud.google.com/run/docs
# monoya_techstack
