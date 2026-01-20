# Deployment Guide

This guide provides detailed instructions for deploying the AI Diary application to Google Cloud Platform.

## Prerequisites

Before you begin, ensure you have:

1. **Google Cloud Platform Account**
   - A GCP project with billing enabled
   - Owner or Editor role on the project

2. **Local Tools Installed**
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - [Terraform](https://www.terraform.io/downloads) (v1.0+)
   - [Docker](https://docs.docker.com/get-docker/)
   - Git

3. **API Keys and Credentials**
   - OpenAI API key
   - Firebase project set up

## Initial GCP Setup

### 1. Create GCP Project

```bash
# Set your project ID
export PROJECT_ID="ai-diary-$(date +%s)"

# Create the project
gcloud projects create $PROJECT_ID --name="AI Diary"

# Set as default project
gcloud config set project $PROJECT_ID

# Enable billing (must be done via console)
echo "Enable billing for project $PROJECT_ID at:"
echo "https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
```

### 2. Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### 3. Create Service Accounts

```bash
# Service account for Cloud Run backend
gcloud iam service-accounts create ai-diary-backend-sa \
  --display-name="AI Diary Backend Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Service account for GitHub Actions
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account"

# Grant permissions for deployment
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Download key for GitHub Actions
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com
```

### 4. Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Add Firebase to your existing GCP project
3. Enable Authentication:
   - Go to Authentication > Sign-in method
   - Enable "Email/Password"
4. Create Firestore Database:
   - Go to Firestore Database
   - Create database in production mode
   - Choose location (e.g., us-central)
5. Set up Firestore Security Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Diaries collection
    match /diaries/{diaryId} {
      // Allow read/write only if user is authenticated and owns the document
      allow read, write: if request.auth != null 
                         && request.auth.uid == resource.data.userId;
      // Allow create only if user is authenticated and sets correct userId
      allow create: if request.auth != null 
                    && request.auth.uid == request.resource.data.userId;
    }
  }
}
```

6. Download service account key:
   - Go to Project Settings > Service Accounts
   - Generate new private key
   - Save as `service-account.json`

## Terraform Deployment

### 1. Prepare Terraform Backend

```bash
# Create GCS bucket for Terraform state
gsutil mb gs://$PROJECT_ID-terraform-state

# Enable versioning
gsutil versioning set on gs://$PROJECT_ID-terraform-state
```

### 2. Configure Terraform Variables

```bash
cd terraform

# Copy example tfvars
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

Example `terraform.tfvars`:
```hcl
project_id         = "ai-diary-123456"
region             = "us-central1"
firestore_location = "us-central"
openai_api_key     = "sk-..."
firebase_api_key   = "AIza..."
```

### 3. Initialize and Apply Terraform

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply configuration
terraform apply

# Save outputs
terraform output -json > ../terraform-outputs.json
```

## Build and Deploy Application

### 1. Build Docker Images

```bash
# Authenticate with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build backend image
cd ../backend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest

# Build frontend image
cd ../frontend
docker build \
  --build-arg VITE_API_URL=$(terraform output -raw backend_url) \
  --build-arg VITE_FIREBASE_API_KEY=$FIREBASE_API_KEY \
  --build-arg VITE_FIREBASE_AUTH_DOMAIN=$PROJECT_ID.firebaseapp.com \
  --build-arg VITE_FIREBASE_PROJECT_ID=$PROJECT_ID \
  -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest
```

### 2. Deploy to Cloud Run

The services should be automatically deployed via Terraform, but you can manually update them:

```bash
# Deploy Weaviate
gcloud run deploy ai-diary-weaviate \
  --image=semitechnologies/weaviate:1.23.0 \
  --platform=managed \
  --region=us-central1 \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=5

# Get Weaviate URL
WEAVIATE_URL=$(gcloud run services describe ai-diary-weaviate \
  --region=us-central1 \
  --format='value(status.url)')

# Deploy backend
gcloud run deploy ai-diary-backend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=$OPENAI_API_KEY,FIREBASE_PROJECT_ID=$PROJECT_ID,WEAVIATE_URL=$WEAVIATE_URL" \
  --service-account=ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

# Get backend URL
BACKEND_URL=$(gcloud run services describe ai-diary-backend \
  --region=us-central1 \
  --format='value(status.url)')

# Deploy frontend
gcloud run deploy ai-diary-frontend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe ai-diary-frontend \
  --region=us-central1 \
  --format='value(status.url)')

echo "Deployment complete!"
echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"
```

## GitHub Actions CI/CD Setup

### 1. Configure GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:

- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Contents of `github-actions-key.json`
- `OPENAI_API_KEY`: Your OpenAI API key
- `VITE_API_URL`: Backend Cloud Run URL
- `VITE_FIREBASE_API_KEY`: Firebase API key
- `VITE_FIREBASE_AUTH_DOMAIN`: `your-project-id.firebaseapp.com`
- `VITE_FIREBASE_PROJECT_ID`: Firebase project ID

### 2. Enable GitHub Actions

The workflows are already configured in `.github/workflows/`. Simply push to the main branch to trigger deployment:

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

## Post-Deployment Configuration

### 1. Configure Custom Domain (Optional)

```bash
# Map custom domain to frontend
gcloud run domain-mappings create \
  --service=ai-diary-frontend \
  --domain=yourdomain.com \
  --region=us-central1

# Follow the instructions to configure DNS
```

### 2. Set Up Monitoring

```bash
# Enable Cloud Logging
gcloud services enable logging.googleapis.com

# View logs
gcloud run logs read ai-diary-backend --limit=50
gcloud run logs read ai-diary-frontend --limit=50

# Set up alerts (via console)
echo "Configure alerts at: https://console.cloud.google.com/monitoring/alerting"
```

### 3. Configure Firestore Indexes

Create indexes for better query performance:

```bash
# Create composite index for diaries
gcloud firestore indexes composite create \
  --collection-group=diaries \
  --field-config=field-path=userId,order=ascending \
  --field-config=field-path=createdAt,order=descending
```

## Monitoring and Maintenance

### View Logs

```bash
# Backend logs
gcloud run logs read ai-diary-backend --limit=100

# Frontend logs
gcloud run logs read ai-diary-frontend --limit=100

# Weaviate logs
gcloud run logs read ai-diary-weaviate --limit=100
```

### Check Service Status

```bash
# List all services
gcloud run services list

# Describe specific service
gcloud run services describe ai-diary-backend --region=us-central1
```

### Update Services

```bash
# Build and push new image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:v2 ./backend
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:v2

# Update Cloud Run service
gcloud run services update ai-diary-backend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:v2 \
  --region=us-central1
```

### Cost Management

```bash
# View current costs
gcloud billing accounts list
gcloud billing projects describe $PROJECT_ID

# Set budget alerts via console
echo "Set up budgets at: https://console.cloud.google.com/billing/budgets"
```

## Rollback

If you need to rollback to a previous version:

```bash
# List revisions
gcloud run revisions list --service=ai-diary-backend --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic ai-diary-backend \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1
```

## Cleanup

To delete all resources:

```bash
# Using Terraform
cd terraform
terraform destroy

# Or manually delete services
gcloud run services delete ai-diary-backend --region=us-central1 --quiet
gcloud run services delete ai-diary-frontend --region=us-central1 --quiet
gcloud run services delete ai-diary-weaviate --region=us-central1 --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete ai-diary-images --location=us-central1 --quiet

# Delete service accounts
gcloud iam service-accounts delete ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com --quiet
gcloud iam service-accounts delete github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com --quiet
```

## Troubleshooting

### Service Won't Start

1. Check logs: `gcloud run logs read SERVICE_NAME`
2. Verify environment variables are set correctly
3. Ensure service account has proper permissions
4. Check that all dependent services are running

### Authentication Issues

1. Verify Firebase configuration is correct
2. Check service account key is valid
3. Ensure Firestore security rules are properly configured
4. Verify JWT tokens are being sent correctly

### Database Connection Issues

1. Check Firestore is enabled and accessible
2. Verify service account has `datastore.user` role
3. Check network connectivity between services

### High Costs

1. Set min-instances to 0 for development
2. Enable request-based autoscaling
3. Set appropriate memory/CPU limits
4. Use Cloud Logging filters to reduce log volume

## Support

For issues specific to GCP deployment, consult:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform GCP Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCP Support](https://cloud.google.com/support)

