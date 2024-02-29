from pulumi_aws.cloudfront import Distribution
from pulumi_aws.iam import (
    GetPolicyDocumentStatementArgs,
    GetPolicyDocumentStatementConditionArgs,
    GetPolicyDocumentStatementPrincipalArgs,
    get_policy_document_output,
)
from pulumi_aws.s3 import Bucket, BucketPolicy

import pulumi


def bucket() -> Bucket:
    tags = pulumi.Config().require_object("aws").get("tags") or {}
    return Bucket("bucket", bucket="latexcv-artifacts", acl="private", tags=tags)


def policies(bucket: Bucket, distribution: Distribution) -> Bucket:
    # Bucket policy definition
    bucket_policy = get_policy_document_output(
        statements=[
            GetPolicyDocumentStatementArgs(
                principals=[
                    GetPolicyDocumentStatementPrincipalArgs(
                        type="Service",
                        identifiers=["cloudfront.amazonaws.com"],
                    )
                ],
                actions=[
                    "s3:GetObject",
                ],
                resources=[bucket.arn.apply(lambda arn: f"{arn}/*")],
                conditions=[
                    GetPolicyDocumentStatementConditionArgs(
                        test="StringEquals",
                        values=[distribution.arn],
                        variable="AWS:SourceArn",
                    )
                ],
            )
        ]
    )

    # Bucket policy linking
    bucket_policy = BucketPolicy(
        "CloudFrontOACBucket Policy", bucket=bucket.id, policy=bucket_policy.json
    )
