output "bucket_trusted" {
  description = "Nome do bucket da camada trusted"
  value       = module.data_lake.bucket_trusted
}

output "glue_database" {
  description = "Nome do Glue Database"
  value       = module.data_lake.glue_database
}

output "athena_workgroup" {
  description = "Nome do Athena Workgroup"
  value       = module.data_lake.athena_workgroup
}
