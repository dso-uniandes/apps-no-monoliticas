resource "random_password" "db" {
  length  = 24
  special = false
}

resource "google_sql_database_instance" "hda" {
  name             = var.cloud_sql_instance_name
  database_version = var.cloud_sql_database_version
  region           = var.region
  project          = var.project_id

  deletion_protection = false

  settings {
    tier              = var.cloud_sql_tier
    edition           = "ENTERPRISE"
    availability_type = "ZONAL"
    disk_size         = 10
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.hda.id
      enable_private_path_for_google_cloud_services = true
    }

    backup_configuration {
      enabled = false
    }

    user_labels = {
      environment = var.environment
      app         = "hda"
    }
  }

  depends_on = [
    google_project_service.required,
    google_service_networking_connection.private_vpc,
  ]
}

resource "google_sql_database" "hda" {
  name     = var.db_name
  instance = google_sql_database_instance.hda.name
  project  = var.project_id
}

resource "google_sql_user" "hda" {
  name     = var.db_user
  instance = google_sql_database_instance.hda.name
  project  = var.project_id
  password = random_password.db.result
}
