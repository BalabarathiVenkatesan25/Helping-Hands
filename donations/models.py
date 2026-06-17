from django.db import models
from django.utils.text import slugify
from accounts.models import DonorProfile, OrphanageProfile

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class, e.g., fa-utensils")

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class DonationRequest(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    orphanage = models.ForeignKey(OrphanageProfile, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='requests')
    description = models.TextField()
    quantity_needed = models.IntegerField()
    quantity_fulfilled = models.IntegerField(default=0)
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='Medium')
    deadline = models.DateField()
    image = models.ImageField(upload_to='requests/', null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.orphanage.orphanage_name}"

    @property
    def fulfillment_percentage(self):
        if self.quantity_needed <= 0:
            return 100
        pct = (self.quantity_fulfilled / self.quantity_needed) * 100
        return min(int(pct), 100)

class Donation(models.Model):
    TYPE_CHOICES = [
        ('Items', 'Items'),
        ('Money', 'Money'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
    ]

    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='donations')
    request = models.ForeignKey(DonationRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donation_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Items')
    quantity_donated = models.IntegerField(default=0, help_text="Used if type is Items")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Used if type is Money")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.donation_type == 'Money':
            return f"Money Donation of ${self.amount} by {self.donor.full_name}"
        return f"{self.quantity_donated} items for '{self.request.title if self.request else 'General'}' by {self.donor.full_name}"
