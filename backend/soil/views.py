from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import SoilAnalysis
from .serializers import SoilAnalysisSerializer

class SoilAnalysisListCreateView(generics.ListCreateAPIView):
    serializer_class = SoilAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SoilAnalysis.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
