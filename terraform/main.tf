terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "ai-diary-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "cloud_run" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build" {
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firestore" {
  service = "firestore.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firebase" {
  service = "firebase.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "ai-diary-images"
  description   = "Docker repository for AI Diary application"
  format        = "DOCKER"
  
  depends_on = [google_project_service.artifact_registry]
}

# Cloud Run service for backend
resource "google_cloud_run_service" "backend" {
  name     = "ai-diary-backend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/ai-diary-images/backend:latest"
        
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }
        
        env {
          name  = "FIREBASE_PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "WEAVIATE_URL"
          value = google_cloud_run_service.weaviate.status[0].url
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
        
        ports {
          container_port = 8000
        }
      }
      
      service_account_name = google_service_account.backend_sa.email
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "autoscaling.knative.dev/minScale" = "0"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.cloud_run]
}

# Cloud Run service for Weaviate
resource "google_cloud_run_service" "weaviate" {
  name     = "ai-diary-weaviate"
  location = var.region

  template {
    spec {
      containers {
        image = "semitechnologies/weaviate:1.23.0"
        
        env {
          name  = "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED"
          value = "true"
        }
        
        env {
          name  = "PERSISTENCE_DATA_PATH"
          value = "/var/lib/weaviate"
        }
        
        env {
          name  = "DEFAULT_VECTORIZER_MODULE"
          value = "none"
        }
        
        env {
          name  = "ENABLE_MODULES"
          value = "text2vec-openai"
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
        
        ports {
          container_port = 8080
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "5"
        "autoscaling.knative.dev/minScale" = "1"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.cloud_run]
}

# Cloud Run service for frontend
resource "google_cloud_run_service" "frontend" {
  name     = "ai-diary-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/ai-diary-images/frontend:latest"
        
        env {
          name  = "VITE_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
        
        env {
          name  = "VITE_FIREBASE_API_KEY"
          value = var.firebase_api_key
        }
        
        env {
          name  = "VITE_FIREBASE_AUTH_DOMAIN"
          value = "${var.project_id}.firebaseapp.com"
        }
        
        env {
          name  = "VITE_FIREBASE_PROJECT_ID"
          value = var.project_id
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "256Mi"
          }
        }
        
        ports {
          container_port = 5173
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "autoscaling.knative.dev/minScale" = "0"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.cloud_run]
}

# Service account for backend
resource "google_service_account" "backend_sa" {
  account_id   = "ai-diary-backend-sa"
  display_name = "AI Diary Backend Service Account"
}

# IAM binding for Cloud Run services (allow public access)
resource "google_cloud_run_service_iam_member" "backend_public" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "weaviate_backend" {
  service  = google_cloud_run_service.weaviate.name
  location = google_cloud_run_service.weaviate.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.backend_sa.email}"
}

# Firestore database
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"
  
  depends_on = [google_project_service.firestore]
}

# IAM roles for backend service account
resource "google_project_iam_member" "backend_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

resource "google_project_iam_member" "backend_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

