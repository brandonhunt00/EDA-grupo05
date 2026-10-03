resource "aws_s3_bucket" "lake" {
  bucket        = "${var.prefixo}-lake-trusted"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "lake" {
  bucket                  = aws_s3_bucket.lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "results" {
  bucket        = "${var.prefixo}-athena-results"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "results" {
  bucket                  = aws_s3_bucket.results.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "dataset" {
  bucket = aws_s3_bucket.lake.id
  key    = "agendamentos/agendamentos.csv"
  source = var.dataset_local
  etag   = filemd5(var.dataset_local)
}

resource "aws_glue_catalog_database" "db" {
  name = replace("${var.prefixo}_clinica", "-", "_")
}

resource "aws_glue_catalog_table" "agendamentos" {
  name          = "agendamentos"
  database_name = aws_glue_catalog_database.db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification           = "csv"
    "skip.header.line.count" = "1"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.lake.bucket}/agendamentos/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.OpenCSVSerde"
      parameters = {
        separatorChar = ","
        quoteChar     = """
        escapeChar    = "\"
      }
    }

    columns { name = "agendamento_id"      type = "string" }
    columns { name = "paciente_id"         type = "string" }
    columns { name = "unidade_id"          type = "string" }
    columns { name = "estado_unidade"      type = "string" }
    columns { name = "regiao_unidade"      type = "string" }
    columns { name = "sexo"                type = "string" }
    columns { name = "faixa_etaria"        type = "string" }
    columns { name = "especialidade"       type = "string" }
    columns { name = "profissional_id"     type = "string" }
    columns { name = "data_agendamento"    type = "date" }
    columns { name = "data_consulta"       type = "date" }
    columns { name = "hora_consulta"       type = "string" }
    columns { name = "status"              type = "string" }
    columns { name = "canal_agendamento"   type = "string" }
    columns { name = "tipo_consulta"       type = "string" }
    columns { name = "valor_consulta"      type = "decimal(10,2)" }
    columns { name = "dias_antecedencia"   type = "int" }
    columns { name = "no_shows_anteriores" type = "int" }
    columns { name = "sistema_origem"      type = "string" }
  }
}

resource "aws_athena_workgroup" "wg" {
  name = "${var.prefixo}-athena"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true
    bytes_scanned_cutoff_per_query     = var.teto_bytes

    result_configuration {
      output_location = "s3://${aws_s3_bucket.results.bucket}/results/"
    }
  }
}
