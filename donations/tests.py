from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from accounts.models import DonorProfile, OrphanageProfile
from .models import Category, DonationRequest, Donation

User = get_user_model()

class DonationsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create categories
        self.category = Category.objects.create(name='Food')

        # Create donor
        self.donor_user = User.objects.create_user(username='donor_u', password='password123', is_donor=True)
        self.donor = DonorProfile.objects.create(
            user=self.donor_user,
            full_name='Donor User',
            phone_number='123',
            address='Addr'
        )

        # Create orphanage
        self.orphanage_user = User.objects.create_user(username='orphanage_u', password='password123', is_orphanage=True)
        self.orphanage = OrphanageProfile.objects.create(
            user=self.orphanage_user,
            orphanage_name='Hope Home',
            phone='456',
            address='Addr',
            description='Desc',
            is_approved=True
        )

        # Create request
        self.request_item = DonationRequest.objects.create(
            orphanage=self.orphanage,
            title='Need Rice',
            category=self.category,
            description='Need 100 kg Rice',
            quantity_needed=100,
            priority='Medium',
            deadline=timezone.now().date() + timedelta(days=10),
            status='Open'
        )

    def test_request_details(self):
        """Test request parameters and fulfillment percentage properties."""
        self.assertEqual(self.request_item.fulfillment_percentage, 0)
        self.assertEqual(str(self.request_item), "Need Rice - Hope Home")

    def test_item_donation_workflow(self):
        """Test the multi-step item donation workflow and request status updates."""
        # 1. Create Donation
        donation = Donation.objects.create(
            donor=self.donor,
            request=self.request_item,
            donation_type='Items',
            quantity_donated=40,
            status='Pending'
        )
        self.assertEqual(donation.status, 'Pending')
        
        # 2. Update status to Accepted
        donation.status = 'Accepted'
        donation.save()
        self.assertEqual(donation.status, 'Accepted')

        # 3. Complete donation and check request updates
        donation.status = 'Completed'
        donation.save()
        
        # We manually update quantities in the view, let's simulate the view logic
        self.request_item.quantity_fulfilled += donation.quantity_donated
        if self.request_item.quantity_fulfilled >= self.request_item.quantity_needed:
            self.request_item.status = 'Completed'
        else:
            self.request_item.status = 'In Progress'
        self.request_item.save()

        # Refresh from database
        self.request_item.refresh_from_db()
        self.assertEqual(self.request_item.quantity_fulfilled, 40)
        self.assertEqual(self.request_item.status, 'In Progress')
        self.assertEqual(self.request_item.fulfillment_percentage, 40)

    def test_restrict_non_donor_donations(self):
        """Test that non-donors are forbidden from accessing item donation pages."""
        self.client.login(username='orphanage_u', password='password123')
        
        # Try to donate items
        response = self.client.get(reverse('donate_items', kwargs={'request_id': self.request_item.id}))
        self.assertEqual(response.status_code, 403)
