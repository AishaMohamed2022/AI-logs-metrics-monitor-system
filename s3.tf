resource "aws_s3_bucket" "s3-bucket" {
  bucket = "s3-bucket-projectTerraform"

  tags = {
    Name = "s3-bucket"
  }
}