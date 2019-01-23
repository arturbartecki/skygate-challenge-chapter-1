from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from exam.models import ExamSheet
from exam.serializers import ExamSheetSerializer, ExamSheetDetailSerializer, ExamSheetArchiveSerializer


class ExamSheetViewSet(viewsets.ModelViewSet):
    """Manage exam sheets in database"""
    serializer_class = ExamSheetSerializer
    queryset = ExamSheet.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return queryset depending on action"""
        if self.action == 'archive_list':
            # Queryet for archived exam sheet list
            return self.queryset.filter(
                owner=self.request.user,
                is_archived=1
            )
        elif self.action == 'change_archive_status':
            # Queryset without filtering is_archive for changing is_archive state
            return self.queryset.filter(
            owner=self.request.user
        )
        # Basic queryset without archived exam sheets
        return self.queryset.filter(
            owner=self.request.user,
            is_archived=0
        )

    def get_serializer_class(self):
        """Return appropriate serializer class for ExamSheet viewset"""
        if self.action == 'retrieve':
            # Serializer that shows details of tasks
            return ExamSheetDetailSerializer
        elif self.action == 'change_archive_status':
            #Serializer only with id and is_archived status
            return ExamSheetArchiveSerializer
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

    # Both versions of 'change_archive_status' work. 
    # I'm not sure if using method 'GET' is acceptable.

    @action(methods=['GET'], detail=True, url_path='archive', url_name='archive')
    def change_archive_status(self, request, pk=None):
        """Change is_archived status"""
        exam_sheet = self.get_object()
        if exam_sheet.is_archived == True:
            data = {'is_archived': False}
        else:
            data = {'is_archived': True}

        serializer = self.get_serializer(exam_sheet, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # @action(methods=['PATCH'], detail=True, url_path='archive', url_name='archive')
    # def change_archive_status(self, request, pk=None):
    #     """Change is_archived status"""
    #     exam_sheet = self.get_object()
    #     if exam_sheet.is_archived == True:
    #         data = {
    #             'pk': pk,
    #             'is_archived': False
    #         }
    #     elif exam_sheet.is_archived == False:
    #         data = {
    #             'pk': pk,
    #             'is_archived': True
    #         }

    #     serializer = self.get_serializer(exam_sheet, data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(
    #             serializer.data,
    #             status=status.HTTP_200_OK
    #         )
    #     return Response(
    #         serializer.errors,
    #         status=status.HTTP_400_BAD_REQUEST
    #     )
