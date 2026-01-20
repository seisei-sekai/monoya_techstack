#!/bin/bash

# Deployment script for Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required environment variables are set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ PROJECT_ID environment variable is not set${NC}"
    echo "Usage: PROJECT_ID=your-project-id ./scripts/deploy-gcp.sh"
    exit 1
fi

REGION=${REGION:-us-central1}

echo -e "${GREEN}🚀 Deploying AI Diary to GCP${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}📋 Enabling required APIs...${NC}"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com

# Configure Docker authentication
echo -e "${YELLOW}🔐 Configuring Docker authentication...${NC}"
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build and push backend image
echo -e "${YELLOW}🏗️  Building backend image...${NC}"
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-diary-images/backend:latest ./backend
echo -e "${YELLOW}📤 Pushing backend image...${NC}"
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-diary-images/backend:latest

# Build and push frontend image
echo -e "${YELLOW}🏗️  Building frontend image...${NC}"
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-diary-images/frontend:latest ./frontend
echo -e "${YELLOW}📤 Pushing frontend image...${NC}"
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-diary-images/frontend:latest

# Deploy Weaviate
echo -e "${YELLOW}🚀 Deploying Weaviate...${NC}"
gcloud run deploy ai-diary-weaviate \
  --image=semitechnologies/weaviate:1.23.0 \
  --platform=managed \
  --region=${REGION} \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=5 \
  --no-allow-unauthenticated

# Get Weaviate URL
WEAVIATE_URL=$(gcloud run services describe ai-diary-weaviate --region=${REGION} --format='value(status.url)')
echo "Weaviate URL: $WEAVIATE_URL"

# Deploy backend
echo -e "${YELLOW}🚀 Deploying backend...${NC}"
gcloud run deploy ai-diary-backend \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-diary-images/backend:latest \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --set-env-vars="WEAVIATE_URL=${WEAVIATE_URL},FIREBASE_PROJECT_ID=${PROJECT_ID}" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

# Get backend URL
BACKEND_URL=$(gcloud run services describe ai-diary-backend --region=${REGION} --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"

# Deploy frontend
echo -e "${YELLOW}🚀 Deploying frontend...${NC}"
gcloud run deploy ai-diary-frontend \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-diary-images/frontend:latest \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe ai-diary-frontend --region=${REGION} --format='value(status.url)')

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Frontend: ${FRONTEND_URL}"
echo "Backend: ${BACKEND_URL}"
echo ""
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "1. Set up Firebase Authentication"
echo "2. Configure Firestore database"
echo "3. Update frontend environment variables with backend URL"
echo "4. Add your OpenAI API key to backend environment"

