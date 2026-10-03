output "lake_bucket_name"           { value = module.lake.lake_bucket_name }
output "athena_results_bucket_name" { value = module.lake.athena_results_bucket_name }
output "glue_database_name"         { value = module.lake.glue_database_name }
output "glue_table_name"            { value = module.lake.glue_table_name }
output "athena_workgroup_name"      { value = module.lake.athena_workgroup_name }
output "workspace"                  { value = terraform.workspace }
