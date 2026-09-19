data "google_project" "current" {
  project_id = var.project_id
}

resource "google_service_account" "work_orchestration" {
  account_id   = "hda-work-orchestration"
  display_name = "HDA Work Orchestration"
  project      = var.project_id

  depends_on = [google_project_service.required]
}

resource "google_project_iam_member" "work_orchestration_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.work_orchestration.email}"
}

resource "google_service_account_iam_member" "work_orchestration_workload_identity" {
  service_account_id = google_service_account.work_orchestration.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.work_orchestration_k8s_namespace}/${var.work_orchestration_k8s_sa}]"

  depends_on = [google_container_cluster.hda]
}

resource "google_project_iam_member" "gke_nodes_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"

  depends_on = [google_container_cluster.hda]
}
