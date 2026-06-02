from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chats.models import Conversation
from chats.serializers import ConversationSerializer, ConversationListSerializer
from drf_spectacular.utils import extend_schema


# Create your views here.

class StartConversationView(APIView):
    serializer_class = ConversationSerializer
    @extend_schema(
        request=ConversationSerializer,
        responses={201: ConversationSerializer},
        description="Start a new conversation between user and lawyer.",
    )
    def post(self, request):
        serializer = ConversationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            conversation = serializer.save()
            return Response({
                'message': "Conversation started successfully.",
                'data': ConversationSerializer(
                    conversation,
                    context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        else:
            return Response({'error': "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ConversationListSerializer(conversations, many=True, context={'request': request})
        return Response({'data': serializer.data, 'message': "Conversations retrieved successfully."}, status=status.HTTP_200_OK)
    

