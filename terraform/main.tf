# main.tf

terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "reddit-terra-bucket" {
  name          = "reddit-terra-bucket"
  location      = var.region
  force_destroy = true
}


resource "google_bigquery_dataset" "reddit_terra_dataset" {
  dataset_id                  = var.reddit_terra_dataset_id
  location                    = var.region  # Adjust the location as needed
  project                     = var.project_id
}
