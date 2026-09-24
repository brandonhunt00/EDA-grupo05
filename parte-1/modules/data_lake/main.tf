locals {
  prefix = "eda262-${var.grupo}"
}

resource "aws_s3_bucket" "trusted" {
  bucket = "${local.prefix}-lake-trusted"
}

resource "aws_glue_catalog_database" "this" {
  name = "eda262_${replace(var.grupo, "-", "_")}_clinica"
}

resource "aws_glue_catalog_table" "agendamentos" {
  name          = "agendamentos"
  database_name = aws_glue_catalog_database.this.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "skip.header.line.count" = "1"
    "classification"         = "csv"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.trusted.bucket}/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.OpenCSVSerde"
      parameters = {
        "separatorChar" = ","
        "quoteChar"     = "\""
      }
    }

    columns { name = "agendamento_id"    type = "string" }
    columns { name = "paciente_id"       type = "string" }
    columns { name = "clinica_id"        type = "string" }
    columns { name = "especialidade"     type = "string" }
    columns { name = "profissional_id"   type = "string" }
    columns { name = "data_agendamento"  type = "date" }
    columns { name = "data_consulta"     type = "date" }
    columns { name = "hora_consulta"     type = "string" }
    columns { name = "status"            type = "string" }
    columns { name = "canal_agendamento" type = "string" }
    columns { name = "tipo_consulta"     type = "string" }
  }
}

resource "aws_athena_workgroup" "this" {
  name = "${local.prefix}-athena"

  configuration {
    enforce_workgroup_configuration = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.trusted.bucket}/athena-results/"
    }
  }
}
