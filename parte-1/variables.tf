variable "aws_region" {
  description = "Região AWS utilizada pelo projeto."
  type        = string
  default     = "us-east-1"
}

variable "prefixo" {
  description = "Prefixo utilizado nos recursos da AV1."
  type        = string
  default     = "eda262-g05"
}

variable "teto_bytes" {
  description = "Limite máximo de bytes processados por consulta no Athena."
  type        = number
  default     = 117455962
}

variable "dataset_local" {
  description = "Caminho local do dataset trusted."
  type        = string
  default     = "../dados/trusted/agendamentos.csv"
}