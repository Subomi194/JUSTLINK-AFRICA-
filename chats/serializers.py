from rest_framework import serializers
from chats.models import Conversation
from django.contrib.auth import get_user_model

User = get_user_model()
    
class ConversationListSerializer(serializers.ModelSerializer):
    
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    lawyer_id = serializers.IntegerField(source='lawyer.id', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.name', read_only=True)
    specialization = serializers.CharField(source='lawyer.lawyer_profile.specialization', read_only=True)
    issue_category = serializers.CharField(source='case.issue_category', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'case', 'issue_category', 'user_id', 'user_name', 'lawyer_id', 'lawyer_name', 'specialization', 'created_at', 'is_active']