import os
import django
import sys
from datetime import datetime, timedelta

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helping_hands.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from accounts.models import DonorProfile, OrphanageProfile, Review, Favorite
from donations.models import Category, DonationRequest, Donation
from core.models import Notification, ContactMessage

User = get_user_model()

def clear_database():
    print("Clearing existing database records...")
    ContactMessage.objects.all().delete()
    Notification.objects.all().delete()
    Donation.objects.all().delete()
    DonationRequest.objects.all().delete()
    Category.objects.all().delete()
    Review.objects.all().delete()
    Favorite.objects.all().delete()
    DonorProfile.objects.all().delete()
    OrphanageProfile.objects.all().delete()
    User.objects.all().delete()
    print("Database cleared.")

def seed_data():
    clear_database()
    
    print("\nCreating default categories...")
    categories_data = [
        ('Food', 'fa-utensils'),
        ('Clothes', 'fa-shirt'),
        ('Books', 'fa-book'),
        ('Educational Materials', 'fa-school'),
        ('Toys', 'fa-gamepad'),
        ('Medicines', 'fa-kit-medical'),
        ('Electronics', 'fa-desktop'),
        ('Furniture', 'fa-chair'),
        ('Money Donation', 'fa-hand-holding-dollar'),
    ]
    categories = {}
    for name, icon in categories_data:
        cat = Category.objects.create(name=name, icon=icon)
        categories[name] = cat
        print(f"Created category: {name}")

    print("\nCreating users and profiles...")
    
    # 1. Admin
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@helpinghands.org',
        password='admin123'
    )
    print("Created Admin superuser: admin@helpinghands.org / admin123")

    # Mock File Content helper
    def get_mock_image():
        # A tiny valid 1x1 transparent GIF file
        gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        return ContentFile(gif_bytes, name='mock_image.gif')

    # 2. Donors
    donors_data = [
        ('john_doe', 'john@gmail.com', 'John Doe', '1234567890', '456 Compassion St, New York, NY'),
        ('jane_smith', 'jane@gmail.com', 'Jane Smith', '9876543210', '789 Generosity Ave, Los Angeles, CA'),
        ('charity_fond', 'charity@foundation.org', 'Charity Foundation', '5551234567', '100 Philanthropy Blvd, Boston, MA')
    ]
    donors = []
    for username, email, full_name, phone, address in donors_data:
        user = User.objects.create_user(username=username, email=email, password='donor123', is_donor=True)
        profile = DonorProfile.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone,
            address=address,
            profile_picture=get_mock_image()
        )
        donors.append(profile)
        print(f"Created Donor: {full_name}")

    # 3. Orphanages
    # Approved
    o1_user = User.objects.create_user(username='hope_home', email='hope@home.org', password='orphanage123', is_orphanage=True)
    o1_profile = OrphanageProfile.objects.create(
        user=o1_user,
        orphanage_name="Hope Children's Home",
        phone="5554443333",
        address="12 Hope Lane, Chicago, IL",
        description="Hope Children's Home is dedicated to nurturing orphaned, abandoned, and underprivileged children. We provide shelter, food, primary education, and a caring family environment to help children build a brighter future.",
        registration_certificate=get_mock_image(),
        profile_image=get_mock_image(),
        is_approved=True
    )
    print("Created Approved Orphanage: Hope Children's Home")

    # Pending
    o2_user = User.objects.create_user(username='sunny_care', email='sunny@care.org', password='orphanage123', is_orphanage=True)
    o2_profile = OrphanageProfile.objects.create(
        user=o2_user,
        orphanage_name="Sunny Days Care Center",
        phone="5551112222",
        address="99 Sunshine St, Miami, FL",
        description="Sunny Days Care Center provides daycare, nursery education, and general foster assistance for children under the age of 12. We strive to bring happiness and learning into the daily lives of foster kids.",
        registration_certificate=get_mock_image(),
        profile_image=get_mock_image(),
        is_approved=False # Pending admin review
    )
    print("Created Pending Orphanage: Sunny Days Care Center")

    # Suspended
    o3_user = User.objects.create_user(username='green_pastures', email='green@pastures.org', password='orphanage123', is_orphanage=True, is_active=False)
    o3_profile = OrphanageProfile.objects.create(
        user=o3_user,
        orphanage_name="Green Pastures Sanctuary",
        phone="5556667777",
        address="88 Wilderness Rd, Portland, OR",
        description="An isolated orphanage sanctuary focusing on rural child nurture. Suspended due to verification issues.",
        registration_certificate=get_mock_image(),
        profile_image=get_mock_image(),
        is_approved=True # Approved, but user account deactivated (suspended) by admin
    )
    print("Created Suspended Orphanage: Green Pastures Sanctuary")

    print("\nCreating donation requests...")
    requests_data = [
        # Approved Orphanage Requests
        (o1_profile, "Winter Blankets & Sweaters", 'Clothes', "With winter approaching, our kids need warm clothes and heavy blankets. We need approximately 100 sets of sweaters and thermal blankets for all age ranges (4 to 16 years).", 100, 0, 'Urgent', 30, 'Open'),
        
        (o1_profile, "Grade 1-8 Academic Notebooks", 'Educational Materials', "Starting of new term. We need textbooks, notebooks, drawing papers, and stationery kits (pens, pencils, rulers) for 50 primary school students.", 50, 25, 'High', 15, 'In Progress'),
        
        (o1_profile, "Monthly Rice & Grain Provisions", 'Food', "Daily meals support. Looking for bulk supply of dry ingredients: 100kg Rice, 50kg Wheat Flour, 25kg Lentils, and cooking oils.", 200, 150, 'Urgent', 5, 'In Progress'),
        
        (o1_profile, "Recreational Toys & Board Games", 'Toys', "Recreational kit for kids. Board games, lego sets, soccer balls, and soft plush toys for indoor/outdoor leisure.", 30, 30, 'Medium', 60, 'Completed')
    ]
    requests = []
    for orphanage, title, cat_name, desc, needed, fulfilled, priority, days_ahead, status in requests_data:
        deadline = timezone.now().date() + timedelta(days=days_ahead)
        req = DonationRequest.objects.create(
            orphanage=orphanage,
            title=title,
            category=categories[cat_name],
            description=desc,
            quantity_needed=needed,
            quantity_fulfilled=fulfilled,
            priority=priority,
            deadline=deadline,
            image=get_mock_image(),
            status=status
        )
        requests.append(req)
        print(f"Created Request: '{title}' ({status})")

    print("\nCreating donation histories and tracking workflow...")
    # John Doe made a donation to Request 2 (Academic Notebooks)
    d1 = Donation.objects.create(
        donor=donors[0], # John Doe
        request=requests[1], # Notebooks
        donation_type='Items',
        quantity_donated=25,
        status='In Transit' # status In Transit
    )
    
    # Jane Smith completed a donation for Toys (Request 4)
    d2 = Donation.objects.create(
        donor=donors[1], # Jane Smith
        request=requests[3], # Toys
        donation_type='Items',
        quantity_donated=30,
        status='Completed' # status Completed
    )
    
    # Charity Foundation made a general money donation (Not request specific)
    d3 = Donation.objects.create(
        donor=donors[2], # Charity Foundation
        request=None,
        donation_type='Money',
        amount=500.00,
        status='Pending'
    )
    
    # Jane Smith made a donation of Dry Grains (Request 3)
    d4 = Donation.objects.create(
        donor=donors[1], # Jane Smith
        request=requests[2], # Grains
        donation_type='Items',
        quantity_donated=100,
        status='Accepted'
    )
    print("Created mock Donations tracking history.")

    print("\nCreating reviews feedback...")
    Review.objects.create(
        donor=donors[0],
        orphanage=o1_profile,
        rating=5,
        comment="Hope Children's Home is exceptionally well managed. Their transparent delivery updates and request timelines give donors immense confidence in supporting them.",
        is_moderated=True
    )
    Review.objects.create(
        donor=donors[1],
        orphanage=o1_profile,
        rating=4,
        comment="Highly professional foster home! They updated the status of my toys donation immediately after arrival. Recommended for contributions.",
        is_moderated=True
    )
    # Pending review
    Review.objects.create(
        donor=donors[0],
        orphanage=o2_profile,
        rating=3,
        comment="Sunny Days Care Center seems to have good initiatives. Waiting for their verification certificate approval so we can start donating.",
        is_moderated=False # Held for admin moderation
    )
    print("Created reviews (2 Approved, 1 Pending).")

    print("\nCreating favorites bookmarked connections...")
    Favorite.objects.create(donor=donors[0], orphanage=o1_profile) # John Doe favorited Hope Home
    Favorite.objects.create(donor=donors[1], orphanage=o1_profile) # Jane Smith favorited Hope Home
    print("Created favorites bookmarks.")

    print("\nCreating sample notifications...")
    Notification.objects.create(
        recipient=admin_user,
        title="New Orphanage Registered",
        message="Sunny Days Care Center has registered and is pending approval.",
        notification_type="Info",
        is_read=False
    )
    Notification.objects.create(
        recipient=o1_user,
        title="Donation In Transit",
        message="John Doe has shipped 25 items for your request 'Grade 1-8 Academic Notebooks'.",
        notification_type="Success",
        is_read=False
    )
    Notification.objects.create(
        recipient=donors[1].user,
        title="Donation Completed",
        message="Your donation for 'Recreational Toys & Board Games' has been successfully completed and verified.",
        notification_type="Success",
        is_read=True
    )
    print("Created sample notifications.")

    print("\nCreating sample contact queries...")
    ContactMessage.objects.create(
        name="Sarah Jenkins",
        email="sarah@corp.com",
        subject="Corporate Sponsorship Opportunity",
        message="Greetings, we represent a tech corporation looking to run an annual CSR event. We want to align with Helping Hands to sponsor multiple orphanages simultaneously. Please get in touch.",
        is_read=False
    )
    ContactMessage.objects.create(
        name="Alex Mercer",
        email="alex@gmail.com",
        subject="Donation Receipt Inquiry",
        message="Are donation receipt reports tax-deductible? Can I download my annual donation summaries in Excel formats?",
        is_read=True
    )
    print("Created sample contact queries.")
    
    print("\nDATABASE SEEDING COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    seed_data()
