from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from exam.models import ExamSheet
from exam.serializers import ExamSheetSerializer, ExamSheetDetailSerializer


class ExamSheetViewSet(viewsets.ModelViewSet):
    """Manage exam sheets in database"""
    serializer_class = ExamSheetSerializer
    queryset = ExamSheet.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return exam sheets owned by request user that are not archived"""
        if self.action == 'archive_list':
            return self.queryset.filter(
                owner=self.request.user,
                is_archived=1
            )
        return self.queryset.filter(
            owner=self.request.user,
            is_archived=0
        )

    def get_serializer_class(self):
        """Return appropriate serializer class for ExamSheet viewset"""
        if self.action == 'retrieve':
            return ExamSheetDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new exam sheet"""
        serializer.save(owner=self.request.user)

    # Cutom actions and views for exam sheets

    @action(detail=False, url_path='archived')
    def archive_list(self, request):
        """Get list of archived sheets"""
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
