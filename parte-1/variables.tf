variable "aws_region" { type = string, default = "us-east-1" }
variable "prefixo"    { type = string, default = "eda262-g05" }

variable "teto_bytes" {
  type        = number
  description = "Ajustar depois de medir Data scanned no Athena."
  default     = 117455962
}

variable "dataset_local" {
  type    = string
  default = "../dados/trusted/agendamentos.csv"
}
