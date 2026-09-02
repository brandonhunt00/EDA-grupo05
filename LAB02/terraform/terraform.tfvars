# Copie este arquivo para terraform.tfvars e preencha.
#   cp terraform.tfvars.example terraform.tfvars

sufixo = "eda-grupo05"        # so minusculas, numeros e hifen

# DECISAO 05 — medido via CLI (consulta larga sem WHERE, 4 particoes):
# DataScannedInBytes = 13570081. Consulta estreita (1 particao): 3392411.
# Piso 10485760 / Topo 117455962. Teto escolhido: entre o piso (com margem)
# e o que a larga realmente escaneia -> mata a larga, deixa passar a estreita.
teto_bytes = 12000000

# DECISAO 04 — os dias registrados como particao (>= 3, incluindo hoje).
dias_particao = ["2026-08-26", "2026-08-29", "2026-09-01", "2026-09-02"]
