from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from legal_case.models import LegalCase
from legal_case.serializers import LegalCaseSerializer
from drf_spectacular.utils import extend_schema

# Create your views here.

class LegalCaseView(APIView):
    serializer_class = LegalCaseSerializer

    @extend_schema(request=LegalCaseSerializer, responses=LegalCaseSerializer)
    def post(self, request):

        if request.user.role != 'user':
            return Response({'detail': 'Only users can create legal cases.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = LegalCaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=LegalCaseSerializer(many=True))
    def get(self, request):
        legal_cases = LegalCase.objects.filter(user=request.user)
        serializer = LegalCaseSerializer(legal_cases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
