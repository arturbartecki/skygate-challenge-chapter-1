from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from exam.models import ExamSheet, ExamTask

from exam.serializers import ExamSheetSerializer, ExamSheetDetailSerializer, \
                            ExamTaskSerializer

EXAM_SHEETS_URL = reverse('exam:examsheet-list')
ARCHIVED_EXAM_SHEETS_URL = reverse('exam:examsheet-archive-list')
NO_FILTERING_EXAM_SHEETS_URL = reverse('exam:examsheet-nofilter')

EXAM_TASK_URL = reverse('exam:examtask-list')


def detail_url(exam_sheet_id):
    """Return exam sheet detail url"""
    return reverse('exam:examsheet-detail', args=[exam_sheet_id])


def archive_sheet_url(exam_sheet_id):
    """Return url that changes archive status"""
    return reverse('exam:examsheet-archive', args=[exam_sheet_id])


def exam_tasks_for_sheet(exam_sheet_id):
    """Url for retrieving list of tasks for exam sheet"""
    return reverse('exam:examtask-sheet', args=[exam_sheet_id])


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

    def test_retreive_exam_list_with_archived_status(self):
        """Test that exam list doesn't show archived exam sheets"""
        archived = ExamSheet.objects.create(
            owner=self.user,
            description='Test object',
            is_archived=True
        )
        valid_sheet = ExamSheet.objects.create(
            owner=self.user,
            description='2nd Test object',
        )

        res = self.client.get(EXAM_SHEETS_URL)

        serializer1 = ExamSheetSerializer(archived)
        serializer2 = ExamSheetSerializer(valid_sheet)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_retrieve_exam_sheet_detail(self):
        """Test viewing an exam_sheet detail"""
        exam_sheet1 = ExamSheet.objects.create(
            owner=self.user,
            description='Test sheet',
        )
        exam_sheet2 = ExamSheet.objects.create(
            owner=self.user,
            description='Test sheet 2'
        )
        exam_task1 = ExamTask.objects.create(
            exam_sheet=exam_sheet1,
            title='Test title'
        )
        exam_task2 = ExamTask.objects.create(
            exam_sheet=exam_sheet2,
            title='Test title 2'
        )

        url = detail_url(exam_sheet1.id)
        res = self.client.get(url)

        serializer = ExamSheetDetailSerializer(exam_sheet1)

        task_serializer1 = ExamTaskSerializer(exam_task1)
        task_serializer2 = ExamTaskSerializer(exam_task2)

        self.assertEqual(res.data, serializer.data)
        self.assertIn(task_serializer1.data, res.data['tasks'])
        self.assertNotIn(task_serializer2.data, res.data['tasks'])

    def test_partial_update_exam_sheet(self):
        """Test updating exam sheet with patch"""
        grade = 'F'
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description='Test description',
            grade=grade
        )
        payload = {
            'description': 'New description',
        }
        url = detail_url(exam_sheet.id)
        self.client.patch(url, payload)

        exam_sheet.refresh_from_db()
        self.assertEqual(exam_sheet.description, payload['description'])
        self.assertEqual(exam_sheet.grade, grade)

    def test_full_update_exam_sheet(self):
        """Test updating a exam sheet with put"""
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description='Test description',
            grade='F'
        )
        payload = {
            'description': 'New description',
            'grade': 'B'
        }

        url = detail_url(exam_sheet.id)
        self.client.put(url, payload)

        exam_sheet.refresh_from_db()
        self.assertEqual(exam_sheet.description, payload['description'])
        self.assertEqual(exam_sheet.grade, payload['grade'])

    def test_archived_exam_sheet_list(self):
        """Test list archived sheets view """
        ExamSheet.objects.create(
            owner=self.user,
            description='archived sheet',
            is_archived=True
        )
        ExamSheet.objects.create(
            owner=self.user,
            description='active sheet'
        )

        res = self.client.get(ARCHIVED_EXAM_SHEETS_URL)

        archived_sheets = ExamSheet.objects.filter(
            owner=self.user,
            is_archived=True
        )
        serializer = ExamSheetSerializer(archived_sheets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    # Both versions of  action 'change_archive_status' are tested
    # Commented part tests action with method='PATCH'

    def test_change_status_to_archive_true(self):
        """Test that archive view can change exam sheet status to true"""
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description='Test description',
            is_archived=False
        )

        url = archive_sheet_url(exam_sheet.id)
        res = self.client.get(url)
        exam_sheet.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(exam_sheet.is_archived, True)

    def test_change_status_to_archive_false(self):
        """Test that archive view can change exam sheet status to false"""
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description='Test description',
            is_archived=True
        )

        url = archive_sheet_url(exam_sheet.id)
        res = self.client.get(url)
        exam_sheet.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(exam_sheet.is_archived, False)

    # def test_change_status_to_archive_true(self):
    #     """Test that archive view can change exam sheet status to true"""
    #     exam_sheet = ExamSheet.objects.create(
    #         owner=self.user,
    #         description='Test description',
    #         is_archived=False
    #     )

    #     url = archive_sheet_url(exam_sheet.id)
    #     res = self.client.patch(url)
    #     exam_sheet.refresh_from_db()

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(exam_sheet.is_archived, True)

    # def test_change_status_to_archive_false(self):
    #     """Test that archive view can change exam sheet status to false"""
    #     exam_sheet = ExamSheet.objects.create(
    #         owner=self.user,
    #         description='Test description',
    #         is_archived=True
    #     )

    #     url = archive_sheet_url(exam_sheet.id)
    #     res = self.client.patch(url)
    #     exam_sheet.refresh_from_db()

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(exam_sheet.is_archived, False)

    def test_exam_sheet_deletion(self):
        """Test that viewset can delete exam_sheet object"""
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description="Test 1"
        )
        exam_sheet2 = ExamSheet.objects.create(
            owner=self.user,
            description="Test 2"
        )
        url = detail_url(exam_sheet.id)
        self.client.delete(url)

        sheets_left = ExamSheet.objects.all()

        self.assertEqual(len(sheets_left), 1)
        self.assertIn(exam_sheet2, sheets_left)

    def test_exam_sheet_list_without_filtering(self):
        """Test view that shows every exam sheet"""
        user2 = get_user_model().objects.create_user(
            username='testuser2',
            password='testpassword'
        )
        ExamSheet.objects.create(
            owner=self.user,
            description="Test sheet"
        )
        ExamSheet.objects.create(
            owner=self.user,
            description='Test sheet2',
            is_archived=True
        )
        ExamSheet.objects.create(
            owner=user2,
            description='Test sheet3'
        )

        res = self.client.get(NO_FILTERING_EXAM_SHEETS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)


class PublicExamTaskApiTests(TestCase):
    """Test if exam task API is available without login"""

    def setUp(self):
        self.client = APIClient()

    def test_exam_task_without_login(self):
        """Test if login is required for retrieving exam tasks"""
        
        res = self.client.get(EXAM_TASK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateExamTaskApiTests(TestCase):
    """Test exam task api with authorized user"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='arturbartecki',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_exam_task_list_for_exam_sheet(self):
        """Test that view list all exam tasks for given exam sheet"""
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description="test exam sheet"
        )
        exam_sheet2 = ExamSheet.objects.create(
            owner=self.user,
            description='Test exam sheet 2'
        )
        exam_task = ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title='Task 1'
        )
        ExamTask.objects.create(
            exam_sheet=exam_sheet2,
            title='Task 2'
        )
        url = exam_tasks_for_sheet(exam_sheet.id)
        res = self.client.get(url)

        serializer = ExamTaskSerializer(exam_task)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer.data, res.data)
    
    def test_exam_task_list_for_user(self):
        """Test that view list all exam tasks for given user"""
        user2 = get_user_model().objects.create_user(
            username='testuser123',
            password='testpassword123'
        )
        exam_sheet = ExamSheet.objects.create(
            owner=self.user,
            description="test description"
        )
        exam_sheet2 = ExamSheet.objects.create(
            owner=user2,
            description='Test description2'
        )
        exam_task = ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title='Test title'
        )
        exam_task2 = ExamTask.objects.create(
            exam_sheet=exam_sheet2,
            title='Test title2'
        )

        res = self.client.get(EXAM_TASK_URL)
        serializer = ExamTaskSerializer(exam_task)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer.data, res.data)
