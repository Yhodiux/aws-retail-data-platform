terraform {
  backend "s3" {
    bucket       = "olist-retail-data-dev-us-east-1-793a6f"
    key          = "terraform/dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
