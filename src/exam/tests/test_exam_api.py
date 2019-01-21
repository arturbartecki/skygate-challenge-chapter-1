from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from exam.models import ExamSheet

from exam.serializers import ExamSheetSerializer

EXAM_SHEETS_URL = reverse('exam:examsheet-list')


class PublicExamApiTests(TestCase):
    """Test if exam API is available without login"""

    def setUp(self):
        self.client = APIClient()

    def test_exam_list_without_login(self):
        """Test if login is required for retrieving exam sheets"""
        res = self.client.get(EXAM_SHEETS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateExamApiTests(TestCase):
    """Test the authorized user exam API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_exam_sheet_list(self):
        """Test retrieving owned exam sheet list """

        ExamSheet.objects.create(
            owner=self.user,
            description='Short description'
        )
        ExamSheet.objects.create(
            owner=self.user,
            description='Short description 2'
        )

        res = self.client.get(EXAM_SHEETS_URL)

        sheets = ExamSheet.objects.all()
        serializer = ExamSheetSerializer(sheets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
