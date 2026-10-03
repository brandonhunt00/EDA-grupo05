provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      turma   = "eda262"
      grupo   = "g05"
      projeto = "engenharia-de-dados"
    }
  }
}
