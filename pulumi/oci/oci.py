"""A Pulumi program to create OCI free compute instance resources using Pulumi ESC variables."""

import os

import pulumi_oci as oci

# Retrieve secrets and environment variables from Pulumi ESC configuration
compartment_ocid = os.getenv("TF_VAR_tenancy_ocid")
ssh_key = os.getenv("SSH_KEY")  # SSH key from 1Password

# Create a New VCN
free_vcn = oci.core.Vcn(
    "free_vcn",
    compartment_id=compartment_ocid,
    cidr_block="10.0.0.0/16",
)

# Create an Internet Gateway
free_internet_gateway = oci.core.InternetGateway(
    "free_internet_gateway",
    compartment_id=compartment_ocid,
    vcn_id=free_vcn.id,
    enabled=True,
)

# Create a Route Table and attach it to the Internet Gateway
free_route_table = oci.core.RouteTable(
    "free_route_table",
    compartment_id=compartment_ocid,
    vcn_id=free_vcn.id,
    route_rules=[
        oci.core.RouteTableRouteRuleArgs(
            network_entity_id=free_internet_gateway.id,
            destination="0.0.0.0/0",
            destination_type="CIDR_BLOCK",
        )
    ],
)

# Create a Security List
security_list_resource = oci.core.SecurityList(
    "security_list_resource",
    compartment_id=compartment_ocid,
    vcn_id=free_vcn.id,
    egress_security_rules=[
        oci.core.SecurityListEgressSecurityRuleArgs(
            destination="0.0.0.0/0",
            protocol="all",
            destination_type="CIDR_BLOCK",
            stateless=False,
        )
    ],
    ingress_security_rules=[
        # Allow SSH access
        oci.core.SecurityListIngressSecurityRuleArgs(
            protocol="6",
            source="0.0.0.0/0",
            description="Allow SSH",
            tcp_options=oci.core.SecurityListIngressSecurityRuleTcpOptionsArgs(
                max=22,
                min=22,
            ),
            source_type="CIDR_BLOCK",
            stateless=False,
        ),
        # Allow ICMP traffic
        oci.core.SecurityListIngressSecurityRuleArgs(
            protocol="1",
            source="0.0.0.0/0",
            description="Allow ICMP",
            icmp_options=oci.core.SecurityListIngressSecurityRuleIcmpOptionsArgs(
                type=3,
                code=4,
            ),
            source_type="CIDR_BLOCK",
            stateless=False,
        ),
    ],
)

# Create a Public Subnet
free_public_subnet = oci.core.Subnet(
    "free_public_subnet",
    cidr_block="10.0.0.0/24",
    compartment_id=compartment_ocid,
    vcn_id=free_vcn.id,
    dns_label="publicsubnet",
    prohibit_internet_ingress=False,
    prohibit_public_ip_on_vnic=False,
    route_table_id=free_route_table.id,
    security_list_ids=[security_list_resource.id],
)

# Create a Private Subnet
free_private_subnet = oci.core.Subnet(
    "free_private_subnet",
    cidr_block="10.0.1.0/24",
    compartment_id=compartment_ocid,
    vcn_id=free_vcn.id,
    dns_label="privatesubnet",
    prohibit_internet_ingress=True,
    prohibit_public_ip_on_vnic=True,
)

availability_domain_name = oci.identity.get_availability_domain(
    compartment_id=compartment_ocid, ad_number=1
)

arm_image = oci.core.get_images(
    compartment_id=compartment_ocid,
    operating_system="Ubuntu",
    operating_system_version="22.04",
    shape="VM.Standard.A1.Flex",
    sort_by="TIMECREATED",
    sort_order="DESC",
)

amd_image = oci.core.get_images(
    compartment_id=compartment_ocid,
    operating_system="Ubuntu",
    operating_system_version="22.04",
    shape="VM.Standard.E2.1.Micro",
    sort_by="TIMECREATED",
    sort_order="DESC",
)

# Oracle Free Tier

"""
    Available Shapes
    Micro instances (AMD processor): 
    Two Always Free VM instances using the VM.Standard.E2.1.Micro
    
    ARM VM.Standard.A1.Flex:
    3,000 OCPU hours and 18,000 GB hours per month, this is equivalent to 4 OCPUs and 24 GB of memory.
    
    Free 200 GB of block storage, minimum 50GB per instance.
"""

free_instances_config = {
    "ARM": {
        "shape": "VM.Standard.A1.Flex",
        "ocpus": 4,
        "memory_in_gbs": 24,
        "image_id": arm_image.id,
        "boot_volume_size_in_gbs": 100,
        "quantity": 1,
    },
    "AMD": {
        "shape": "VM.Standard.E2.1.Micro",
        "ocpus": 1,
        "memory_in_gbs": 1,
        "image_id": amd_image.id,
        "boot_volume_size_in_gbs": 50,
        "quantity": 2,
    },
}

instances = []
for instance_type in free_instances_config.values():
    for i in range(instance_type["quantity"]):
        instance = oci.core.Instance(
            f"free-{instance_type['shape']}-{i}",
            availability_domain=availability_domain_name.name,
            compartment_id=compartment_ocid,
            shape=instance_type["shape"],
            create_vnic_details=oci.core.InstanceCreateVnicDetailsArgs(
                assign_private_dns_record=True,
                assign_public_ip="true",
                subnet_id=free_public_subnet.id,
            ),
            metadata={"ssh_authorized_keys": ssh_key},
            source_details=oci.core.InstanceSourceDetailsArgs(
                source_type="image",
                source_id=instance_type["image_id"],
                boot_volume_size_in_gbs=instance_type["boot_volume_size_in_gbs"],
            ),
            shape_config=oci.core.InstanceShapeConfigArgs(
                ocpus=instance_type["ocpus"],
                memory_in_gbs=instance_type["memory_in_gbs"],
            ),
        )

        instances.append(instance)
