output "state_bucket_name" { value = aws_s3_bucket.tfstate.bucket }
output "lock_table_name"   { value = aws_dynamodb_table.tflock.name }

output "backend_hcl" {
  value = <<-EOT
bucket         = "${aws_s3_bucket.tfstate.bucket}"
key            = "parte-1/terraform.tfstate"
region         = "${var.aws_region}"
dynamodb_table = "${aws_dynamodb_table.tflock.name}"
encrypt        = true
EOT
}
