from rest_framework import serializers
from users.models import LawyerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class LawyerProfileSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = LawyerProfile
        fields = ['specialization', 'bio', 'law_firm']

class LawyerListSerializer(serializers.ModelSerializer):
    lawyer_profile = LawyerProfileSummarySerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'country', 'lawyer_profile']