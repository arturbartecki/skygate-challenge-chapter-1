from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from exam.models import ExamSheet, ExamTask
from exam.serializers import ExamSheetSerializer, ExamSheetDetailSerializer, \
                            ExamSheetArchiveSerializer, ExamTaskSerializer
from exam.permissions import IsOwnerOrReadOnly


class ExamSheetViewSet(viewsets.ModelViewSet):
    """Manage exam sheets in database"""
    serializer_class = ExamSheetSerializer
    queryset = ExamSheet.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        """Return queryset depending on action"""
        if self.action in ['retrieve', 'not_filtered_list']:
            # Base queryset without filtering
            return self.queryset
        elif self.action == 'archive_list':
            # Queryet for archived exam sheet list
            return self.queryset.filter(
                owner=self.request.user,
                is_archived=1
            )
        elif self.action == 'change_archive_status':
            # Queryset without filtering is_archive
            # for changing is_archive state
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
            # Serializer only with id and is_archived status
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

    @action(
        methods=['GET'], detail=True,
        url_path='archive', url_name='archive'
    )
    def change_archive_status(self, request, pk=None):
        """Change is_archived status"""
        exam_sheet = self.get_object()
        if exam_sheet.is_archived:
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

    # @action(
    #     methods=['PATCH'], detail=True,
    #     url_path='archive', url_name='archive'
    # )
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

    @action(detail=False, url_path='nofilter', url_name='nofilter')
    def not_filtered_list(self, request):
        """Get list of every sheet"""
        # print(self.action)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ExamTaskViewSet(viewsets.ModelViewSet):
    """Manage exam sheets in database"""
    serializer_class = ExamTaskSerializer
    queryset = ExamTask.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return queryset depending on action"""
        # Queryset without filtering out by user
        if self.action == 'task_list_for_sheet':
            return self.queryset
        # Basic exam task list for requesting user
        return self.queryset.filter(
            exam_sheet__owner =  self.request.user
        )

    def get_serializer_class(self):
        """Return appropriate serializer class for ExamTask viewset"""
        return self.serializer_class
    
    @action(detail=True, url_path='sheet', url_name='sheet')
    def task_list_for_sheet(self, request, pk=None):
        """Get list of all tasks for given sheet pk"""
        obj = self.get_queryset().filter(exam_sheet__pk=pk)
        return Response(self.get_serializer(obj, many=True).data)
    