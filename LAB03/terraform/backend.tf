# Backend remoto compartilhado da disciplina. Bucket, key e lock vem de
# backend.hcl (-backend-config), para o nome da conta nao ir para o git.
terraform {
  backend "s3" {
    workspace_key_prefix = "eda-a12"
  }
}
