import os

from pulumi_gcp import compute

import pulumi
from pulumi import ResourceOptions

ssh_key = os.environ["SSH_KEY"]  # SSH key from 1Password

compute_network = compute.Network(
    "network",
    auto_create_subnetworks=True,
)

compute_firewall = compute.Firewall(
    "pangolin-firewall",
    network=compute_network.self_link,
    allows=[
        compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["22"],
        )
    ],
)

instance_addr = compute.address.Address("address")
compute_instance = compute.Instance(
    "instance",
    machine_type="f1-micro",
    metadata={"ssh-keys": ssh_key},
    # metadata_startup_script=startup_script,
    boot_disk=compute.InstanceBootDiskArgs(
        initialize_params=compute.InstanceBootDiskInitializeParamsArgs(
            image="debian-12-bookworm-v20250311"
        )
    ),
    network_interfaces=[
        compute.InstanceNetworkInterfaceArgs(
            network=compute_network.id,
            access_configs=[
                compute.InstanceNetworkInterfaceAccessConfigArgs(
                    nat_ip=instance_addr.address
                )
            ],
        )
    ],
    service_account=compute.InstanceServiceAccountArgs(
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    ),
    opts=ResourceOptions(depends_on=[compute_firewall]),
)

pulumi.export("instanceName", compute_instance.name)
pulumi.export("instanceIP", instance_addr.address)
