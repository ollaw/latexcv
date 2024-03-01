from pulumi_aws.acm import Certificate
from pulumi_aws.cloudfront import (
    Distribution,
    DistributionDefaultCacheBehaviorArgs,
    DistributionDefaultCacheBehaviorForwardedValuesArgs,
    DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs,
    DistributionOriginArgs,
    DistributionRestrictionsArgs,
    DistributionRestrictionsGeoRestrictionArgs,
    DistributionViewerCertificateArgs,
    OriginAccessControl,
)
from pulumi_aws.s3 import Bucket

import pulumi

DISTRIBUTION_OAI = "origin-access-identity/cloudfront/latexcv"
DISTRIBUTION_ORIGIN_ID = "s3-latexcv"


def setup(bucket: Bucket, certificate: Certificate) -> Distribution:

    # Origin Access Control
    oac = OriginAccessControl(
        "oac",
        description="latexcv-policy",
        origin_access_control_origin_type="s3",
        signing_behavior="always",
        signing_protocol="sigv4",
    )

    # Cloudfront distribution
    alias = pulumi.Config().require_object("aws").get("cloudfront").get("alias")
    return Distribution(
        "distribution",
        origins=[
            DistributionOriginArgs(
                domain_name=bucket.bucket_regional_domain_name,
                origin_id=DISTRIBUTION_ORIGIN_ID,
                origin_access_control_id=oac.id,
            )
        ],
        default_root_object="en.pdf",
        enabled=True,
        aliases=[alias],
        default_cache_behavior=DistributionDefaultCacheBehaviorArgs(
            allowed_methods=[
                "GET",
                "HEAD",
            ],
            cached_methods=[
                "GET",
                "HEAD",
            ],
            forwarded_values=DistributionDefaultCacheBehaviorForwardedValuesArgs(
                query_string=False,
                cookies=DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                    forward="none",
                ),
            ),
            target_origin_id=DISTRIBUTION_ORIGIN_ID,
            viewer_protocol_policy="redirect-to-https",
            min_ttl=0,
            default_ttl=3600,
            max_ttl=86400,
        ),
        restrictions=DistributionRestrictionsArgs(
            geo_restriction=DistributionRestrictionsGeoRestrictionArgs(
                restriction_type="none"
            ),
        ),
        tags=pulumi.Config().require_object("aws").get("tags") or {},
        viewer_certificate=DistributionViewerCertificateArgs(
            acm_certificate_arn=certificate.arn,
            ssl_support_method="sni-only",
        ),
    )
