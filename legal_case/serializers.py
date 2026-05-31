from rest_framework import serializers
from users.serializers import UserSerializer
from legal_case.models import LegalCase
from django.contrib.auth import get_user_model

User = get_user_model()

class LegalCaseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    

    class Meta:
        model = LegalCase
        fields = '__all__'
        read_only_fields = ['user', 'created_at']