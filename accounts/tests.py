from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import DonorProfile, OrphanageProfile, Review, Favorite

User = get_user_model()

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test donor
        self.donor_user = User.objects.create_user(
            username='donor_test', 
            email='donor@test.com', 
            password='password123',
            is_donor=True
        )
        self.donor_profile = DonorProfile.objects.create(
            user=self.donor_user,
            full_name='Donor Test',
            phone_number='1234567890',
            address='Test Address'
        )

        # Create a test orphanage (approved)
        self.orphanage_user = User.objects.create_user(
            username='orphanage_approved', 
            email='approved@test.com', 
            password='password123',
            is_orphanage=True
        )
        self.orphanage_profile = OrphanageProfile.objects.create(
            user=self.orphanage_user,
            orphanage_name='Approved Orphanage',
            phone='0987654321',
            address='Approved Address',
            description='Test Description',
            is_approved=True
        )

        # Create a test orphanage (pending approval)
        self.pending_user = User.objects.create_user(
            username='orphanage_pending', 
            email='pending@test.com', 
            password='password123',
            is_orphanage=True
        )
        self.pending_profile = OrphanageProfile.objects.create(
            user=self.pending_user,
            orphanage_name='Pending Orphanage',
            phone='1112223333',
            address='Pending Address',
            description='Test Description',
            is_approved=False
        )

    def test_user_creation_roles(self):
        """Test user role verification flags work correctly."""
        self.assertTrue(self.donor_user.is_donor)
        self.assertFalse(self.donor_user.is_orphanage)
        
        self.assertTrue(self.orphanage_user.is_orphanage)
        self.assertFalse(self.orphanage_user.is_donor)

    def test_login_flow(self):
        """Test authentication redirects correctly based on user roles."""
        # Test client login
        logged_in = self.client.login(username='donor_test', password='password123')
        self.assertTrue(logged_in)
        
        response = self.client.get(reverse('dashboard'))
        # Dashboard router should redirect to donor dashboard
        self.assertRedirects(response, reverse('donor_dashboard'))

    def test_unapproved_orphanage_restriction(self):
        """Test unapproved orphanages are restricted by middleware to pending approval page."""
        self.client.login(username='orphanage_pending', password='password123')
        
        # Try accessing profile page
        response = self.client.get(reverse('profile'))
        # Should redirect to pending approval
        self.assertRedirects(response, reverse('pending_approval'))

    def test_review_creation(self):
        """Test donor can create review for approved orphanage."""
        review = Review.objects.create(
            donor=self.donor_profile,
            orphanage=self.orphanage_profile,
            rating=5,
            comment="Excellent",
            is_moderated=False
        )
        self.assertEqual(self.orphanage_profile.average_rating, 0.0) # 0 because is_moderated=False
        
        review.is_moderated = True
        review.save()
        self.assertEqual(self.orphanage_profile.average_rating, 5.0) # 5 because is_moderated=True
