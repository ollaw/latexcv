import _bucket
import _certificate
import _cloudflare
import _distribution
import pulumi_cloudflare as cloudflare
from pulumi_aws import acm, cloudfront, iam, s3

certificate = _certificate.setup()

# S3 bucket to host artifacts from Gitlab
bucket = _bucket.bucket()
# Distribution on bucket
distribution = _distribution.setup(bucket, certificate)
# Access to bucket only from Cloudfront
_bucket.policies(bucket, distribution)
# Record on Cloudflare
_cloudflare.setup(distribution.domain_name)
