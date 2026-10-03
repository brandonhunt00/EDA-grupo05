variable "aws_region" {
  description = "Região AWS utilizada para o backend remoto."
  type        = string
  default     = "us-east-1"
}

variable "prefixo" {
  description = "Prefixo utilizado nos recursos de backend."
  type        = string
  default     = "eda262-g05"
}