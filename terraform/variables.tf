

variable "project_id" {
  type        = string
  description = "The name of the project"
  default     = "de-reddit-reports"
}

variable "region" {
  type        = string
  description = "The default compute region"
  default     = "northamerica-northeast1"
}

variable "reddit_terra_dataset_id" {
  description = "The ID of the BigQuery dataset"
  type        = string
  default     = "reddit_dataset"  # Default value can be adjusted as needed
}



