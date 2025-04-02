"""Main entry point for deploying multi-cloud free-tier resources."""

# Import Oracle Cloud Infrastructure (OCI) instances
from oci import instances as oci_instances

import pulumi

# Export Oracle instance details
for instance in oci_instances:
    pulumi.export(f"{instance._name}_id", instance.id)
    pulumi.export(f"{instance._name}_public_ip", instance.public_ip)

# Placeholder for AWS, GCP, and Azure instances
# These will be added later as separate modules (e.g., aws_instances, gcp_instances, azure_instances)
