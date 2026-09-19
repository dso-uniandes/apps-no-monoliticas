variable "project_id" {
  description = "GCP project ID used for the remote Terraform state bucket"
  type        = string
}

variable "region" {
  description = "Region for the state bucket"
  type        = string
  default     = "us-central1"
}
