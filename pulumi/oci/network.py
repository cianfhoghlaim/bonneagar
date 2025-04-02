"""A Pulumi program to create OCI resources using Pulumi ESC variables."""

import os

import pulumi_oci as oci

import pulumi

# Retrieve secrets and environment variables from Pulumi ESC configuration
compartment_ocid = os.getenv("TF_VAR_tenancy_ocid")
oci_region = os.getenv("TF_VAR_region")
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
    display_name="sc_list",
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
    "r_private_subnet",
    cidr_block="10.0.1.0/24",
    compartment_id=compartment_ocid,
    vcn_id=free_vcn.id,
    display_name="private_subnet",
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

free_instances = {
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


for instance in free_instances.values():
    for i in range(instance["quantity"]):
        oci.core.Instance(
            f"free-{instance['shape']}-{i}",
            availability_domain=availability_domain_name.name,
            compartment_id=compartment_ocid,
            shape=instance["shape"],
            create_vnic_details=oci.core.InstanceCreateVnicDetailsArgs(
                assign_private_dns_record=True,
                assign_public_ip="true",
                display_name=f"pulumidemo_instance_{i}",
                subnet_id=free_public_subnet.id,
            ),
            metadata={"ssh_authorized_keys": ssh_key},
            source_details=oci.core.InstanceSourceDetailsArgs(
                source_type="image",
                source_id=instance["image_id"],
                boot_volume_size_in_gbs=instance["boot_volume_size_in_gbs"],
            ),
            shape_config=oci.core.InstanceShapeConfigArgs(
                ocpus=instance["ocpus"],
                memory_in_gbs=instance["memory_in_gbs"],
            ),
        )

instance = oci.core.Instance(
    "-instance",
    # Replace with your desired availability domain.
    availability_domain=test_availability_domains.availability_domains[0].name,
    # Replace with your compartment ID.
    compartment_id="ocid1.compartment.oc1..xxxxxxxx",
    # Using VM.Standard.E4.Flex shape.
    shape="VM.Standard.E4.Flex",
    # Replace with your subnet ID.
    create_vnic_details=oci.core.InstanceCreateVnicDetailsArgs(
        assign_private_dns_record=True,
        assign_public_ip="true",
        display_name="pulumideminst",
        subnet_id=free_public_subnet.id,
    ),
    # Metadata for the instance, including SSH keys for access.
    metadata={
        "ssh_authorized_keys": public_ssh_key
        # "ssh_authorized_keys": std.file_output(input=public_ssh_key).apply(lambda invoke: invoke.result)
    },
    # Use an Oracle-provided image or your own custom image.
    source_details=oci.core.InstanceSourceDetailsArgs(
        source_type="image",
        # Replace with the image OCID.
        source_id="ocid1.image.oc1.iad.aaaaaaaalbjc2slze7i3rbpho3p4ict6u4k2l6r2r3igvvkopbfd4xt2wwla",
    ),
    # Specifying the OCPU and memory configurations.
    shape_config=oci.core.InstanceShapeConfigArgs(
        ocpus=2.0,  # Number of OCPUs.
        memory_in_gbs=8.0,  # Amount of RAM in GBs.
    ),
    # Additional arguments like display name, can be specified here.
    display_name="pulumidemo_instance",
)


# Exporting the public IP of the instance.
(pulumi.export("instance_public_ip", instance.public_ip),)
pulumi.export("create_shape", instance.shape)
pulumi.export("create_vnic", instance.create_vnic_details)
pulumi.export("create_vnic", instance.create_vnic_details["display_name"])


# Export Outputs
pulumi.export("vcn_id", free_vcn.id)
pulumi.export("internet_gateway_id", free_internet_gateway.id)
pulumi.export("route_table_id", free_route_table.id)
pulumi.export("public_subnet_id", free_public_subnet.id)
pulumi.export("private_subnet_id", test_private_subnet.id)
