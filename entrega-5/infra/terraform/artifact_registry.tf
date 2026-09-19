resource "google_artifact_registry_repository" "hda" {
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Hogar de los Alpes POC container images"
  format        = "DOCKER"

  labels = {
    environment = var.environment
    app         = "hda"
  }

  depends_on = [google_project_service.required]
}
