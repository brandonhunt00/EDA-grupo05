module "lake" {
  source = "./modules/lake"

  prefixo       = var.prefixo
  teto_bytes    = var.teto_bytes
  dataset_local = var.dataset_local
}
