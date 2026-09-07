output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "zone" {
  value = var.zone
}

output "artifact_registry_repository" {
  value = google_artifact_registry_repository.hda.name
}

output "artifact_registry_url" {
  description = "Base URL for Docker images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.hda.repository_id}"
}

output "gke_cluster_name" {
  value = google_container_cluster.hda.name
}

output "gke_cluster_location" {
  value = google_container_cluster.hda.location
}

output "cloud_sql_instance_name" {
  value = google_sql_database_instance.hda.name
}

output "cloud_sql_connection_name" {
  value = google_sql_database_instance.hda.connection_name
}

output "cloud_sql_private_ip" {
  value = google_sql_database_instance.hda.private_ip_address
}

output "db_name" {
  value = google_sql_database.hda.name
}

output "db_user" {
  value = google_sql_user.hda.name
}

output "db_password" {
  description = "Generated database password for Work Orchestration"
  value       = random_password.db.result
  sensitive   = true
}

output "work_orchestration_gsa_email" {
  value = google_service_account.work_orchestration.email
}

output "k8s_namespace" {
  value = var.work_orchestration_k8s_namespace
}
