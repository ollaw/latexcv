from pulumi_aws import Provider
from pulumi_aws.acm import Certificate, CertificateValidation
from pulumi_cloudflare import Record

import pulumi


def setup() -> Certificate:
    # Create certificate on ACM
    domain = pulumi.Config().require_object("aws").get("cloudfront").get("alias")

    # Create an AWS provider instance specifying the 'us-east-1' region.
    provider = Provider("aws-provider", region="us-east-1")

    certificate = Certificate(
        "cv-certificate",
        domain_name=domain,
        validation_method="DNS",
        opts=pulumi.ResourceOptions(provider=provider),
    )

    # Create validation record on cloudflare
    valiodation_record = Record(
        "validation-record",
        zone_id=pulumi.Config().require_object("cloudflare").get("zoneid"),
        name=certificate.domain_validation_options[0].resource_record_name,
        value=certificate.domain_validation_options[0].resource_record_value,
        type="CNAME",
        ttl=60,
    )

    CertificateValidation(
        "certificate-validation",
        certificate_arn=certificate.arn,
        validation_record_fqdns=[valiodation_record.hostname],
        opts=pulumi.ResourceOptions(provider=provider),
    )

    return certificate
