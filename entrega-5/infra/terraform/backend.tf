# Configured via: terraform init -backend-config=backend.hcl
# Generate backend.hcl from backend.hcl.example (see scripts/generate-backend-hcl.sh).

terraform {
  backend "gcs" {}
}
