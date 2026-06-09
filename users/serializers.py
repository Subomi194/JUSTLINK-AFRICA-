from rest_framework import serializers
from users.models import LawyerProfile
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.utils import normalize_phone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'language', 'country', 'created_at', 'password']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):

        if data.get('role') == 'user':
            if not data.get('phone_number'):
                raise serializers.ValidationError("Phone number is required for users.")

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            role='user',  # Default role is 'user' for regular users
            password=validated_data.get('password'),
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
            language=validated_data['language'],
            country=validated_data['country']
        )
        return user
    
    def validate_phone_number(self, value):
        try:
            return normalize_phone(value)
        except Exception:
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def get_token(self, attrs):
        data = super().get_token(attrs)

        # Add custom claims
        data['user'] = {
            'id': self.user.id,
            'name': self.user.name,
            'role': self.user.role,
            'country': self.user.country,
            'language': self.user.language,     
       }
        return data

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()


class LawyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawyerProfile
        fields = ['law_firm', 'license_number']

class LawyerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    lawyer_profile = LawyerProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone_number', 'country', 'created_at', 'password', 'lawyer_profile']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if not data.get('email'):
            raise serializers.ValidationError("Email is required for lawyers.")
        return data

    def create(self, validated_data):
        lawyer_profile_data = validated_data.pop('lawyer_profile') # Extract lawyer profile data from the validated data
        user = User.objects.create_user(
            role='lawyer',  # Default role is 'lawyer' for lawyers
            email=validated_data['email'],
            password=validated_data.get('password'),
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
            country=validated_data['country']
        )
        LawyerProfile.objects.create(user=user, **lawyer_profile_data) #create profile linked to user using the extracted lawyer profile data
        return user
    
    def validate_phone_number(self, value):
        try:
            return normalize_phone(value)
        except Exception:
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

class LawyerProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawyerProfile
        fields = ['specialization', 'bio']

class AllUsersProfileSerializer(serializers.ModelSerializer):
    lawyer_profile = LawyerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'language', 'country', 'created_at', 'role', 'lawyer_profile']
    