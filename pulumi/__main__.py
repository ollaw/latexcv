import pulumi
from pulumi_aws import s3, cloudfront, iam, kms
import pulumi_cloudflare as cloudflare

config = pulumi.Config()
tags = config.require_object("aws").get("tags") or {}
alias = config.require_object("aws").get("cloudfront").get("alias")


DISTRIBUTION_OAI = "origin-access-identity/cloudfront/latexcv"
DISTRIBUTION_ORIGIN_ID = "s3-latexcv"

# S3 bucket to host artifacts from Gitlab 
bucket = s3.Bucket(
    "bucket",
    bucket="latexcv-artifacts",
    acl="private",
    tags=tags,
    opts=pulumi.ResourceOptions(protect=False),
)

# Origin Access Control
oac = cloudfront.OriginAccessControl(
    "oac",
    description="latexcv-policy",
    origin_access_control_origin_type="s3",
    signing_behavior="always",
    signing_protocol="sigv4",
)

# Cloudfront distribution
distribution = cloudfront.Distribution(
    "distribution",
    origins=[
        cloudfront.DistributionOriginArgs(
            domain_name=bucket.bucket_regional_domain_name,
            origin_id=DISTRIBUTION_ORIGIN_ID,
            origin_access_control_id=oac.id,
        )
    ],
    enabled=True,
    aliases=[alias],
    default_cache_behavior=cloudfront.DistributionDefaultCacheBehaviorArgs(
        allowed_methods=[
            "GET",
            "HEAD",
        ],
        cached_methods=[
            "GET",
            "HEAD",
        ],
        forwarded_values=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=False,
            cookies=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="none",
            ),
        ),
        target_origin_id=DISTRIBUTION_ORIGIN_ID,
        viewer_protocol_policy="redirect-to-https",
        min_ttl=0,
        default_ttl=3600,
        max_ttl=86400,
    ),
    restrictions=cloudfront.DistributionRestrictionsArgs(
        geo_restriction=cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none"
        ),
    ),
    tags=tags,
    viewer_certificate=cloudfront.DistributionViewerCertificateArgs(
        acm_certificate_arn="arn:aws:acm:us-east-1:152119833031:certificate/6708be3d-91db-448b-931e-310f1a73b5e1",
        ssl_support_method="sni-only",
    ),
)

# Bucket policy definition
bucket_policy = iam.get_policy_document_output(
    statements=[
        iam.GetPolicyDocumentStatementArgs(
            principals=[
                iam.GetPolicyDocumentStatementPrincipalArgs(
                    type="Service",
                    identifiers=["cloudfront.amazonaws.com"],
                )
            ],
            actions=[
                "s3:GetObject",
            ],
            resources=[bucket.arn.apply(lambda arn: f"{arn}/*")],
            conditions=[
                iam.GetPolicyDocumentStatementConditionArgs(
                    test="StringEquals",
                    values=[distribution.arn],
                    variable="AWS:SourceArn",
                )
            ],
        )
    ]
)

# Bucket policy linking
bucket_policy = s3.BucketPolicy(
    "CloudFrontOACBucket Policy", bucket=bucket.id, policy=bucket_policy.json
)

# Record on Cloudflare
cloudflare_cfg = config.require_object("cloudflare")
dns = cloudflare.Record(
    "dns",
    zone_id=cloudflare_cfg.get("zoneid"),
    name=cloudflare_cfg.get("record").get("name"),
    value=distribution.domain_name,
    type=cloudflare_cfg.get("record").get("type"),
    ttl=cloudflare_cfg.get("record").get("ttl"),
)
