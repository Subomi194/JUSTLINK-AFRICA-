from rest_framework import serializers
from chats.models import Conversation
from users.models import LawyerProfile
from lawyers.serializers import LawyerProfileSummarySerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationSerializer(serializers.ModelSerializer):
    lawyer_id = serializers.IntegerField(write_only=True)

    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.name', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'user_id', 'user_name', 'lawyer_id', 'lawyer_name', 'created_at']
        read_only_fields = ['id', 'user_id', 'user_name', 'lawyer_name', 'created_at']


    def validate_lawyer_id(self, value):
        # check lawyer exists AND has role='lawyer'
        try:
            lawyer = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Lawyer with this ID does not exist.")
        if lawyer.role != 'lawyer':
            raise serializers.ValidationError("The selected user is not a lawyer.")
        return value

    def validate(self, data):
        request = self.context['request']

         # make sure the logged in person is a user not a lawyer
        if request.user.role != 'user':
            raise serializers.ValidationError("Only users can create conversations.")
        
        # make sure the logged in user is not trying to create a conversation with themselves as the lawyer
        if request.user.id == data['lawyer_id']:
            raise serializers.ValidationError("You cannot create a conversation with yourself.")
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        lawyer_id = validated_data.pop('lawyer_id')
        lawyer = User.objects.get(id=lawyer_id, role='lawyer')
        
        conversation = Conversation.objects.create(user=user, lawyer=lawyer, **validated_data)
        return conversation
    
class ConversationListSerializer(serializers.ModelSerializer):
    
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    lawyer_id = serializers.IntegerField(source='lawyer.id', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.name', read_only=True)
    lawyer_role = serializers.CharField(source='lawyer.role', read_only=True)
    specialization = serializers.CharField(source='lawyer.lawyer_profile.specialization', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'user_id', 'user_name', 'user_role', 'lawyer_id', 'lawyer_name', 'lawyer_role', 'specialization', 'created_at']