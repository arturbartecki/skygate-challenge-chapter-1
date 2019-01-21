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

    def test_retreive_exam_sheet_list_limited_to_user(self):
        """Test that exam sheets returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            username='test2',
            password='testpass123'
        )
        ExamSheet.objects.create(
            owner=user2,
            description='Short description'
        )
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description='Test description'
        )

        res = self.client.get(EXAM_SHEETS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['description'], exam_sheet.description)

    def test_create_exam_sheet_successful(self):
        """Test creating a new exam sheet"""
        payload = {
            'description': 'Test exam sheet',
        }
        res = self.client.post(EXAM_SHEETS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = ExamSheet.objects.filter(
            owner=self.user,
            description=payload['description']
        ).exists()

        self.assertTrue(exists)

    def test_create_exam_sheet_invalid(self):
        """Test creating an exam sheet with invalid payload"""
        payload = {'owner': ''}
        res = self.client.post(EXAM_SHEETS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
