from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chats.models import Conversation
from chats.serializers import ConversationListSerializer
from drf_spectacular.utils import extend_schema

# Create your views here.
    
class ConversationListView(APIView):
    serializer_class = ConversationListSerializer

    @extend_schema(
        responses={200: ConversationListSerializer(many=True)},
        description="Get list of conversations for the logged in user.",
    )
    def get(self, request):
        user = request.user
        if user.role == 'user':
            conversations = Conversation.objects.filter(user=user).select_related('lawyer__lawyer_profile')
        elif user.role == 'lawyer':
            conversations = Conversation.objects.filter(lawyer=user).select_related('user')
        elif user.role== 'admin':
            conversations = Conversation.objects.all()
        else:
            return Response({'error': "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ConversationListSerializer(conversations, many=True, context={'request': request})
        return Response({'data': serializer.data, 'message': "Conversations retrieved successfully."}, status=status.HTTP_200_OK)
    

