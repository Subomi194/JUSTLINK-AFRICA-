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

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issue_category = models.CharField(max_length=255, choices=ISSUE_CATEGORIES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Legal Case {self.id} - {self.issue_category}"