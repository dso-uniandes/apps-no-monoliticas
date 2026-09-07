output "tfstate_bucket" {
  description = "GCS bucket name for Terraform remote state"
  value       = google_storage_bucket.tfstate.name
}

output "tfstate_prefix" {
  description = "Suggested state object prefix"
  value       = "hda-poc"
}
