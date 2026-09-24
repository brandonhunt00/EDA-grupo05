#!/usr/bin/env bash
set -u

GRUPO="${GRUPO:-gNN}"
REGION="${AWS_REGION:-us-east-1}"
BUCKET="eda262-${GRUPO}-lake-trusted"
GLUE_DB="eda262_${GRUPO}_clinica"
WORKGROUP="eda262-${GRUPO}-athena"

passa() { echo "[PASSA] $1"; }
falha() { echo "[FALHA] $1"; }

if aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
  passa "Bucket existe: $BUCKET"
else
  falha "Bucket não encontrado: $BUCKET"
fi

if aws glue get-database --name "$GLUE_DB" --region "$REGION" >/dev/null 2>&1; then
  passa "Glue Database existe: $GLUE_DB"
else
  falha "Glue Database não encontrado: $GLUE_DB"
fi

if aws glue get-table --database-name "$GLUE_DB" --name agendamentos --region "$REGION" >/dev/null 2>&1; then
  passa "Glue Table existe: agendamentos"
else
  falha "Glue Table não encontrada: agendamentos"
fi

if aws athena get-work-group --work-group "$WORKGROUP" --region "$REGION" >/dev/null 2>&1; then
  passa "Athena Workgroup existe: $WORKGROUP"
else
  falha "Athena Workgroup não encontrado: $WORKGROUP"
fi
