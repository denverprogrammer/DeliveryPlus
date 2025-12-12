from typing import Any
from django.core.management.base import BaseCommand
from mgmt.models import Company
from tracking.models import Campaign
from tracking.models import Recipient
from tracking.models import Token
from tracking.models import Tracking


class Command(BaseCommand):
    help = "Create a test recipient with token abc123"
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

        # Get or create the recipient
        recipient, created = Recipient.objects.get_or_create(
            company=company,
            defaults={
                "first_name": "Test",
                "last_name": "Recipient",
                "email": "test@example.com",
                "phone_number": "555-123-4567",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created recipient: {recipient}"))
        else:
            self.stdout.write(self.style.WARNING(f"Recipient already exists: {recipient}"))

        # Get or create the tracking
        tracking, created = Tracking.objects.get_or_create(
            campaign=campaign,
            recipient=recipient,
            company=company,
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created tracking: {tracking}"))
        else:
            self.stdout.write(self.style.WARNING(f"Tracking already exists: {tracking}"))

        # Get or create the token
        token, created = Token.objects.get_or_create(
            value=self.testToken,
            defaults={"tracking": tracking, "status": "active"},
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created token abc123 for tracking: {token}"))
        else:
            # Update token if it exists but doesn't have the tracking
            if token.tracking != tracking:
                token.tracking = tracking
                token.save()
                self.stdout.write(
                    self.style.WARNING(f"Updated existing token abc123 to use tracking: {token}")
                )
            else:
                self.stdout.write(self.style.WARNING(f"Token abc123 already exists: {token}"))
