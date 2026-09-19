resource "google_container_cluster" "hda" {
  name     = var.gke_cluster_name
  location = var.zone
  project  = var.project_id

  network    = google_compute_network.hda.name
  subnetwork = google_compute_subnetwork.hda.name

  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false

  min_master_version = "1.34.9-gke.1655001"

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "STABLE"
  }

  depends_on = [
    google_project_service.required,
    google_service_networking_connection.private_vpc,
  ]
}

resource "google_container_node_pool" "primary" {
  name     = "primary"
  location = var.zone
  cluster  = google_container_cluster.hda.name
  project  = var.project_id

  node_count = var.gke_min_node_count

  node_config {
    machine_type = var.gke_machine_type
    disk_size_gb = var.gke_disk_size_gb
    disk_type    = "pd-standard"
    preemptible  = false

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = {
      environment = var.environment
      app         = "hda"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
