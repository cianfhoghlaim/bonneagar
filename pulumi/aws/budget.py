import pulumi
import pulumi_aws as aws
import os

# The email address to receive notifications
my_email = os.get_env("contact_email")

# Create a new Free Tier usage budget
budget = aws.budgets.Budget(
    "freeTierBudget",
    name="MyFreeTierUsageBudget",
    budget_type="USAGE",
    limit_amount="100",  # Set a hypothetical limit (e.g., 100 hours)
    limit_unit="USAGE_UNITS",
    time_unit="MONTHLY",
    cost_filters={
        "Service": ["Amazon Elastic Compute Cloud - Compute"],
        "UsageType": ["FreeTier"]
    },
    notifications=[
        aws.budgets.BudgetNotificationArgs(
            comparison_operator="GREATER_THAN",
            threshold=75,
            threshold_type="PERCENTAGE",
            notification_type="ACTUAL",
            subscriber_email_addresses=[my_email],
        ),
        aws.budgets.BudgetNotificationArgs(
            comparison_operator="GREATER_THAN",
            threshold=100,
            threshold_type="PERCENTAGE",
            notification_type="ACTUAL",
            subscriber_email_addresses=[my_email],
        ),
    ]
)

# Export the Budget name
pulumi.export('budget_name', budget.name)
