from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from exam.models import ExamSheet
from exam.serializers import ExamSheetSerializer


class ExamSheetViewSet(viewsets.ModelViewSet):
    """Manage exam sheets in database"""
    serializer_class = ExamSheetSerializer
    queryset = ExamSheet.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return exam sheets owned by request user"""
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Create a new exam sheet"""
        serializer.save(owner=self.request.user)
