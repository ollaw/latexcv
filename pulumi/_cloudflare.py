from pulumi_cloudflare import Record

import pulumi
from pulumi import Input


def setup(name: Input[str]):
    config = pulumi.Config().require_object("cloudflare")
    Record(
        "dns",
        zone_id=config.get("zoneid"),
        name=config.get("record").get("name"),
        value=name,
        type=config.get("record").get("type"),
        ttl=config.get("record").get("ttl"),
    )
