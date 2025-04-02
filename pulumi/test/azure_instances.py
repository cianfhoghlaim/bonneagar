import pulumi
import pulumi_azure_native as azure_native
from pulumi_azure_native import compute, network, resources

# Get configuration values
config = pulumi.Config()
location = config.get("azure_location") or "WestUS" # Default location

# Create an Azure Resource Group
resource_group = resources.ResourceGroup("free-tier-rg", location=location)

# Create a Virtual Network
vnet = network.VirtualNetwork("free-tier-vnet",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ))

# Create a Subnet
subnet = network.Subnet("free-tier-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24")

# Create a Public IP Address
public_ip = network.PublicIPAddress("free-tier-pip",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    public_ip_allocation_method=network.IPAllocationMethod.DYNAMIC) # Dynamic is often sufficient for free tier

# Create a Network Security Group allowing SSH
nsg = network.NetworkSecurityGroup("allow-ssh-nsg",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    security_rules=[network.SecurityRuleArgs(
        name="SSH",
        priority=1000,
        direction=network.SecurityRuleDirection.INBOUND,
        access=network.SecurityRuleAccess.ALLOW,
        protocol=network.SecurityRuleProtocol.TCP,
        source_port_range="*",
        destination_port_range="22",
        source_address_prefix="*",
        destination_address_prefix="*",
    )])

# Create a Network Interface
nic = network.NetworkInterface("free-tier-nic",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
        name="webserveripcfg",
        subnet=network.SubnetArgs(id=subnet.id),
        private_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
        public_ip_address=network.PublicIPAddressArgs(id=public_ip.id),
    )],
    network_security_group=network.NetworkSecurityGroupArgs(id=nsg.id))

# Define the VM Admin Username and Password (consider using SSH keys for production)
admin_username = "azureuser"
admin_password = config.require_secret("adminPassword") # Require password from config

# Create a Virtual Machine
vm = compute.VirtualMachine("free-tier-vm",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    network_profile=compute.NetworkProfileArgs(
        network_interfaces=[compute.NetworkInterfaceReferenceArgs(id=nic.id)],
    ),
    hardware_profile=compute.HardwareProfileArgs(
        vm_size="Standard_B1s", # B1s is eligible for Azure free tier
    ),
    os_profile=compute.OSProfileArgs(
        computer_name="hostname",
        admin_username=admin_username,
        admin_password=admin_password,
        linux_configuration=compute.LinuxConfigurationArgs( # Use password auth for simplicity here
            disable_password_authentication=False,
        ),
    ),
    storage_profile=compute.StorageProfileArgs(
        os_disk=compute.OSDiskArgs(
            create_option=compute.DiskCreateOptionTypes.FROM_IMAGE,
            name="myosdisk1",
        ),
        image_reference=compute.ImageReferenceArgs(
            publisher="Canonical",
            offer="UbuntuServer",
            sku="18.04-LTS", # Choose a free-tier eligible image SKU
            version="latest",
        ),
    ),
    tags={
        "Name": "free-tier-instance-azure",
    })

# Get the public IP address after the VM is created
public_ip_addr = pulumi.Output.all(resource_group.name, public_ip.name).apply(
    lambda args: network.get_public_ip_address(
        resource_group_name=args[0],
        public_ip_address_name=args[1]
    )
)

# Export the Public IP address
pulumi.export("public_ip", public_ip_addr.ip_address)
# Export the VM Hostname
pulumi.export("vm_hostname", vm.os_profile.apply(lambda p: p.computer_name if p else None))