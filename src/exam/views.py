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
