terraform {
  required_version = ">= 1.10"
  required_providers {
    aws  = { source = "hashicorp/aws", version = "~> 5.0" }
    helm = { source = "hashicorp/helm", version = "~> 2.13" }
  }
  backend "s3" {
    bucket       = "uma-tfstate-493667572687"
    key          = "dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true # bloqueo del estado (Terraform >= 1.10, sin DynamoDB)
  }
}

provider "aws" {
  region = var.region
}
