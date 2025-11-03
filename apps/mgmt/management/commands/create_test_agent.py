from typing import Any
from django.core.management.base import BaseCommand
from mgmt.models import Company
from tracking.models import Agent
from tracking.models import Campaign


class Command(BaseCommand):
    help = "Create a test agent with token abc123"
    testToken = "abc123"

    def handle(self, *args: Any, **options: Any) -> None:
        # Get or create a company
        company, created = Company.objects.get_or_create(
            name="Test Company",
            defaults={
                "address": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zip_code": "12345",
                "phone": "555-123-4567",
                "email": "test@example.com",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created company: {company}"))

        # Get or create a campaign
        campaign, created = Campaign.objects.get_or_create(
            name="Test Campaign",
            company=company,
            defaults={"description": "Test campaign for tracking"},
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created campaign: {campaign}"))

        # Get or create the agent
        agent, created = Agent.objects.get_or_create(
            token=self.testToken,
            campaign=campaign,
            defaults={
                "first_name": "Test",
                "last_name": "Agent",
                "email": "test@example.com",
                "phone_number": "555-123-4567",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created agent with token abc123: {agent}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"Agent with token abc123 already exists: {agent}")
            )
