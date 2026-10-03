#!/usr/bin/env bash
set -u

PREFIXO="${PREFIXO:-eda262-g05}"
REGION="${AWS_REGION:-us-east-1}"
LAKE="${PREFIXO}-lake-trusted"
DB="$(echo "${PREFIXO}_clinica" | tr '-' '_')"
TABLE="agendamentos"
WG="${PREFIXO}-athena"

passa(){ echo "[PASSA] $1"; }
falha(){ echo "[FALHA] $1"; }

if [[ "${1:-}" == "--pos-destroy" ]]; then
  aws s3api head-bucket --bucket "$LAKE" 2>/dev/null && falha "Bucket ainda existe" || passa "Bucket removido"
  aws glue get-database --name "$DB" --region "$REGION" >/dev/null 2>&1 && falha "Glue Database ainda existe" || passa "Glue Database removido"
  aws athena get-work-group --work-group "$WG" --region "$REGION" >/dev/null 2>&1 && falha "Athena Workgroup ainda existe" || passa "Athena Workgroup removido"
  exit 0
fi

aws s3api head-bucket --bucket "$LAKE" 2>/dev/null && passa "Bucket do Data Lake existe" || falha "Bucket não existe"
aws glue get-database --name "$DB" --region "$REGION" >/dev/null 2>&1 && passa "Glue Database existe" || falha "Glue Database não existe"
aws glue get-table --database-name "$DB" --name "$TABLE" --region "$REGION" >/dev/null 2>&1 && passa "Glue Table existe" || falha "Glue Table não existe"
aws athena get-work-group --work-group "$WG" --region "$REGION" >/dev/null 2>&1 && passa "Athena Workgroup existe" || falha "Athena Workgroup não existe"
