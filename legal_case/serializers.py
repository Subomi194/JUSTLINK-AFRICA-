from rest_framework import serializers
from legal_case.models import LegalCase
from django.contrib.auth import get_user_model

User = get_user_model()

class LawyerConnectSerializer(serializers.ModelSerializer):
    lawyer_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.name', read_only=True)

    class Meta:
        model = LegalCase
        fields = ['id', 'user_id', 'user_name', 'lawyer_id', 'lawyer_name', 
                  'issue_category', 'description', 'channel', 'status', 'created_at']
        read_only_fields = ['id', 'user_id', 'user_name', 'lawyer_name', 'channel', 'status', 'created_at']

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
            raise serializers.ValidationError("Only users can connect with lawyers.")
        
        # make sure the logged in user is not trying to create a conversation with themselves as the lawyer
        if request.user.id == data.get('lawyer_id'):
            raise serializers.ValidationError("You cannot connect with yourself.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        lawyer_id = validated_data.pop('lawyer_id')
        lawyer = User.objects.get(id=lawyer_id, role='lawyer')
        
        case = LegalCase.objects.create(user=user, lawyer=lawyer, **validated_data)
        return case

class CaseRespondSerializer(serializers.Serializer):
    # this serializer is only for lawyer accepting or rejecting
    STATUS_OPTIONS = [('accepted', 'Accepted'), ('rejected', 'Rejected')]
    status = serializers.ChoiceField(choices=STATUS_OPTIONS)
