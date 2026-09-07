variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Primary GCP zone for the zonal GKE cluster"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment label"
  type        = string
  default     = "dev"
}

variable "artifact_registry_repository" {
  description = "Artifact Registry Docker repository ID"
  type        = string
  default     = "hda-poc"
}

variable "gke_cluster_name" {
  description = "GKE Standard cluster name"
  type        = string
  default     = "hda-poc"
}

variable "gke_machine_type" {
  description = "Machine type for the single GKE node pool"
  type        = string
  default     = "e2-standard-2"
}

variable "gke_min_node_count" {
  description = "Minimum nodes in the pool"
  type        = number
  default     = 1
}

variable "gke_max_node_count" {
  description = "Maximum nodes in the pool"
  type        = number
  default     = 2
}

variable "gke_disk_size_gb" {
  description = "Boot disk size for GKE nodes"
  type        = number
  default     = 50
}

variable "cloud_sql_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "hda-postgres"
}

variable "cloud_sql_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-f1-micro"
}

variable "cloud_sql_database_version" {
  description = "PostgreSQL version for Cloud SQL"
  type        = string
  default     = "POSTGRES_15"
}

variable "db_name" {
  description = "Application database name"
  type        = string
  default     = "hda"
}

variable "db_user" {
  description = "Application database user"
  type        = string
  default     = "hda"
}

variable "work_orchestration_k8s_namespace" {
  description = "Kubernetes namespace for workloads"
  type        = string
  default     = "hda"
}

variable "work_orchestration_k8s_sa" {
  description = "Kubernetes ServiceAccount name for Work Orchestration"
  type        = string
  default     = "work-orchestration"
}
