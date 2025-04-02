# import pulumi
# import pulumi_gcp as gcp

# # Get the GCP project and zone from Pulumi config
# config = pulumi.Config()
# gcp_project = config.require("gcp_project")
# gcp_zone = config.get("gcp_zone") or "us-central1-a" # Default to us-central1-a

# # Specify the machine type (f1-micro is part of the GCP Free Tier)
# machine_type = "f1-micro"

# # Specify the boot disk image (using a common Debian image)
# # Check GCP documentation for free tier eligible images if needed
# boot_disk = gcp.compute.InstanceBootDiskArgs(
#     initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
#         image="debian-cloud/debian-11"
#     )
# )

# # Get the default network
# default_network = gcp.compute.get_network(name="default")

# # Create a GCP compute instance
# instance = gcp.compute.Instance("free-tier-instance",
#     project=gcp_project,
#     zone=gcp_zone,
#     machine_type=machine_type,
#     boot_disk=boot_disk,
#     # Allow HTTP traffic for basic testing (optional)
#     network_interfaces=[gcp.compute.InstanceNetworkInterfaceArgs(
#         network=default_network.id,
#         # Access config needed to assign a public IP
#         access_configs=[gcp.compute.InstanceNetworkInterfaceAccessConfigArgs()],
#     )],
#     tags=["http-server", "https-server"], # Example tags, adjust as needed
#     # Define metadata for startup script (optional)
#     # metadata_startup_script="echo 'Hello, World!' > /var/www/html/index.html", # Example for a web server
#     metadata={
#         "Name": "free-tier-instance-gcp",
#     })

# # Export the public IP address of the instance
# pulumi.export("instance_public_ip", instance.network_interfaces[0].access_configs[0].nat_ip)
# # Export the instance name
# pulumi.export("instance_name", instance.name)
