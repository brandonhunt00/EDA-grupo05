variable "grupo" {
  description = "Número do grupo no formato gNN"
  type        = string
  default     = "gNN"
}

variable "aws_region" {
  description = "Região AWS utilizada no projeto"
  type        = string
  default     = "us-east-1"
}
