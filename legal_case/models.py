from django.db import models
from django.conf import settings

# Create your models here.
class LegalCase(models.Model):

    ISSUE_CATEGORIES = [
        ('labour dispute', 'Labour Dispute'),
        ('inheritance', 'Inheritance Dispute'),
        ('property', 'Property Dispute'),
        ('family', 'Family Law'),
        ('domestic violence', 'Domestic Violence'),
        ('police abuse', 'Police Abuse'),
        ('other', 'Other'),
    ]

    CHANNEL_CHOICES = [
        ('web', 'Web'),
        ('mobile', 'Mobile'),
        ('ussd', 'USSD'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_cases')
    lawyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    issue_category = models.CharField(max_length=255, choices=ISSUE_CATEGORIES)
    description = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='web')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Legal Case {self.id} - {self.issue_category}"

