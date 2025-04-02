import pulumi
import pulumi_aws as aws

# Get the AWS region from Pulumi config, default to 'us-west-2' if not set
config = pulumi.Config()
aws_region = config.get("aws_region") or "us-west-2"

# Specify the AMI ID for Amazon Linux 2 (HVM), SSD Volume Type (Free Tier eligible in many regions)
# You might need to update this based on the chosen region and desired OS
# Find free tier eligible AMIs: https://aws.amazon.com/free/free-tier-details/
ami_id = "ami-0abcdef1234567890" # Replace with a valid free-tier AMI for your region

# Specify the instance type (t2.micro is Free Tier eligible)
instance_type = "t2.micro"

# Create an AWS security group that allows SSH ingress
sec_group = aws.ec2.SecurityGroup("allow-ssh",
    description="Allow SSH inbound traffic",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ])

# Create an AWS EC2 instance
instance = aws.ec2.Instance("free-tier-instance",
    ami=ami_id,
    instance_type=instance_type,
    vpc_security_group_ids=[sec_group.id], # Associate the security group
    tags={
        "Name": "free-tier-instance",
    })

# Export the public IP of the instance
pulumi.export("instance_public_ip", instance.public_ip)
# Export the public DNS of the instance
pulumi.export("instance_public_dns", instance.public_dns)