from django.shortcuts import render
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from legal_case.models import LegalCase
from legal_case.serializers import LawyerConnectSerializer, CaseRespondSerializer
from chats.models import Conversation
from drf_spectacular.utils import extend_schema

# Create your views here.

class LawyerConnectView(APIView):
    serializer_class = LawyerConnectSerializer

    @extend_schema(request=LawyerConnectSerializer, responses=LawyerConnectSerializer)
    def post(self, request):

        serializer = LawyerConnectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            case = serializer.save()
            return Response({
                'detail': 'Successfully connected with lawyer. Waiting for lawyer to respond.',
                'data': LawyerConnectSerializer(
                    case,
                    context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=LawyerConnectSerializer(many=True))
    def get(self, request):
        user = request.user
        case_status = request.query_params.get('status')
        if user.role == 'user':
            legal_cases = LegalCase.objects.filter(user=user).select_related('lawyer')
        elif user.role == 'lawyer':
            legal_cases = LegalCase.objects.filter(lawyer=user).select_related('user')
        else:
            return Response({'error': "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)
        
        # apply status filter if provided
        if case_status:
            legal_cases = legal_cases.filter(status=case_status)

        serializer = LawyerConnectSerializer(legal_cases, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CaseRespondView(APIView):
    serializer_class = CaseRespondSerializer

    @extend_schema(request=CaseRespondSerializer, responses={200: LawyerConnectSerializer})
    def patch(self, request, case_id):

        if request.user.role != 'lawyer':
            return Response({'detail': 'Only lawyers can accept cases.'}, status=status.HTTP_403_FORBIDDEN)

        # get the case
        try:
            case = LegalCase.objects.get(id=case_id)
        except LegalCase.DoesNotExist:
            return Response({'detail': 'Case not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # make sure this case belongs to this lawyer
        if case.lawyer != request.user:
            return Response({'detail': 'You can only accept cases assigned to you.'}, status=status.HTTP_403_FORBIDDEN)

        # make sure case is still pending
        if case.status != 'pending':
            return Response(
                {'error': f'This case has already been {case.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CaseRespondSerializer(data=request.data)
        if serializer.is_valid():

            new_status = serializer.validated_data['status']
            case.status = new_status
            if new_status == 'accepted':
                case.accepted_at = timezone.now()
                case.save()

                # automatically create conversation when lawyer accepts
                conversation = Conversation.objects.create(
                    case=case,
                    users=case.user,
                    lawyer=request.user
                )

                return Response({
                    'message': 'Case accepted. Conversation started.',
                    'data': {
                        'case': LawyerConnectSerializer(case, context={'request': request}).data,
                        'conversation_id': conversation.id  # mobile dev uses this as Firebase room key
                    }
                }, status=status.HTTP_200_OK )

            case.save()

            return Response({
                'detail': f'Case rejected successfully.',
                'data': LawyerConnectSerializer(case, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    