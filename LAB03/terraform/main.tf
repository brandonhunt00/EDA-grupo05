# Raiz: uma unica chamada ao modulo. Os recursos vivem em modules/lake/.
module "lake" {
  source     = "./modules/lake"
  sufixo     = var.sufixo
  teto_bytes = var.teto_bytes
}
