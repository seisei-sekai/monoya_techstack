output "backend_url" {
  description = "URL of the backend Cloud Run service"
  value       = google_cloud_run_service.backend.status[0].url
}

output "frontend_url" {
  description = "URL of the frontend Cloud Run service"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "weaviate_url" {
  description = "URL of the Weaviate Cloud Run service"
  value       = google_cloud_run_service.weaviate.status[0].url
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = google_artifact_registry_repository.docker_repo.name
}

output "backend_service_account" {
  description = "Email of the backend service account"
  value       = google_service_account.backend_sa.email
}

