from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg

class User(AbstractUser):
    is_donor = models.BooleanField(default=False)
    is_orphanage = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class DonorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='donors/profiles/', null=True, blank=True)

    def __str__(self):
        return self.full_name

    @property
    def total_donations_count(self):
        return self.donations.count()

    @property
    def active_donations_count(self):
        return self.donations.exclude(status='Completed').count()

    @property
    def completed_donations_count(self):
        return self.donations.filter(status='Completed').count()

class OrphanageProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='orphanage_profile')
    orphanage_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    description = models.TextField()
    registration_certificate = models.FileField(upload_to='certificates/')
    profile_image = models.ImageField(upload_to='orphanages/profiles/')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.orphanage_name

    @property
    def average_rating(self):
        # Only count moderated (visible) reviews
        avg = self.reviews.filter(is_moderated=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    @property
    def active_reviews(self):
        return self.reviews.filter(is_moderated=True)

    @property
    def reviews_count(self):
        return self.reviews.filter(is_moderated=True).count()

class Review(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='reviews')
    orphanage = models.ForeignKey(OrphanageProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    is_moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.donor.full_name} on {self.orphanage.orphanage_name} - {self.rating} Stars"

class Favorite(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='favorites')
    orphanage = models.ForeignKey(OrphanageProfile, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('donor', 'orphanage')

    def __str__(self):
        return f"{self.donor.full_name} favorited {self.orphanage.orphanage_name}"
