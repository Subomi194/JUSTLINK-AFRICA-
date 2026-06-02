from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from lawyers.serializers import LawyerListSerializer

User = get_user_model()

# Create your views here.
class LawyerListView(generics.ListAPIView):
    serializer_class = LawyerListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['lawyer_profile__specialization', 'country']

    def get_queryset(self):
        queryset = User.objects.filter(role='lawyer')
        specialization = self.request.query_params.get('specialization')
        country = self.request.query_params.get('country')

        if specialization:
            queryset = queryset.filter(lawyer_profile__specialization__icontains=specialization)
        if country:
            queryset = queryset.filter(country__icontains=country)

        return queryset