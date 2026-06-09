from django.db import models
from django.conf import settings
from legal_case.models import LegalCase

# Create your models here.

class Conversation(models.Model):
    case = models.OneToOneField(LegalCase, on_delete=models.CASCADE, related_name='conversation')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    lawyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lawyer_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Conversation between {self.user.name} and {self.lawyer.name}"