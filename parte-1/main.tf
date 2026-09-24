module "data_lake" {
  source = "./modules/data_lake"

  grupo      = var.grupo
  aws_region = var.aws_region
}
