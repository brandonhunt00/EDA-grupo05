variable "sufixo" {
  type        = string
  description = "Sufixo unico dos nomes (so minusculas e numeros)."
}

variable "teto_bytes" {
  type        = number
  description = "BytesScannedCutoffPerQuery do workgroup."
}
