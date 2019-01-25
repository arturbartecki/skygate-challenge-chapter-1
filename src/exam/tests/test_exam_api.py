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


def sample_user(username='testusername', password='testpassword123'):
    """Create and return sample user"""
    return get_user_model().objects.create_user(
        username=username,
        password=password
    )


def sample_exam_sheet(
        owner, description='Test description',
        is_archived=False, grade='Z', student=None
        ):
    """Create and return sample exam sheet"""
    return ExamSheet.objects.create(
        owner=owner,
        description=description,
        is_archived=is_archived,
        grade=grade,
        student=student
    )


def sample_exam_task(
        exam_sheet, title='Test title',
        description=None, answer=None, points=None
        ):
    """Create and return sample exam task"""
    return ExamTask.objects.create(
        exam_sheet=exam_sheet,
        title=title,
        description=description,
        answer=answer,
        points=points
        )


def detail_url(exam_sheet_id):
    """Return exam sheet detail url"""
    return reverse('exam:examsheet-detail', args=[exam_sheet_id])


def archive_sheet_url(exam_sheet_id):
    """Return url that changes archive status"""
    return reverse('exam:examsheet-archive', args=[exam_sheet_id])


def exam_tasks_for_sheet(exam_sheet_id):
    """Url for retrieving list of tasks for exam sheet"""
    return reverse('exam:examtask-sheet', args=[exam_sheet_id])


def exam_task_detail(exam_task_id):
    """Return url for exam task detail"""
    return reverse('exam:examtask-detail', args=[exam_task_id])


def exam_task_answer(exam_task_id):
    """Return url for exam answer view"""
    return reverse('exam:examtask-answer', args=[exam_task_id])


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
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_exam_sheet_list(self):
        """Test retrieving owned exam sheet list """

        sample_exam_sheet(owner=self.user)
        sample_exam_sheet(owner=self.user)

        res = self.client.get(EXAM_SHEETS_URL)

        sheets = ExamSheet.objects.all()
        serializer = ExamSheetSerializer(sheets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retreive_exam_sheet_list_limited_to_user(self):
        """Test that exam sheets returned are for authenticated user"""
        user2 = sample_user(username='test2')
        sample_exam_sheet(
            owner=user2,
            description='Short description'
        )
        exam_sheet = sample_exam_sheet(
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
        archived = sample_exam_sheet(
            owner=self.user,
            description='Test object',
            is_archived=True
        )
        valid_sheet = sample_exam_sheet(
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
        exam_sheet1 = sample_exam_sheet(owner=self.user)
        exam_sheet2 = sample_exam_sheet(owner=self.user)
        exam_task1 = sample_exam_task(
            exam_sheet=exam_sheet1,
            title='Test title'
        )
        exam_task2 = sample_exam_task(
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
        exam_sheet = sample_exam_sheet(
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
        exam_sheet = sample_exam_sheet(
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

    def test_update_as_not_owner(self):
        """Test that it's impossible to update sheet as not owner"""
        user2 = sample_user(username='testuser123')
        grade_check = 'D'
        exam_sheet = sample_exam_sheet(
            owner=user2,
            description='Test description',
            grade=grade_check
        )
        payload = {
            'description': 'New description',
            'grade': 'A'
        }
        url = detail_url(exam_sheet.id)
        self.client.put(url, payload)

        exam_sheet.refresh_from_db()

        self.assertEqual(exam_sheet.grade, grade_check)
        self.assertNotEqual(exam_sheet.description, payload['description'])

    def test_archived_exam_sheet_list(self):
        """Test list archived sheets view """
        sample_exam_sheet(
            owner=self.user,
            description='archived sheet',
            is_archived=True
        )
        sample_exam_sheet(
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
        exam_sheet = sample_exam_sheet(
            owner=self.user,
            description='Test description',
            is_archived=False
        )

        url = archive_sheet_url(exam_sheet.id)
        res = self.client.get(url)
        exam_sheet.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(exam_sheet.is_archived)

    def test_change_status_to_archive_false(self):
        """Test that archive view can change exam sheet status to false"""
        exam_sheet = sample_exam_sheet(
            owner=self.user,
            description='Test description',
            is_archived=True
        )

        url = archive_sheet_url(exam_sheet.id)
        res = self.client.get(url)
        exam_sheet.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(exam_sheet.is_archived)

    def test_change_status_to_archive_not_as_user(self):
        """Test that only owner can chagne archive status"""
        user2 = sample_user(username='testuser2')
        exam_sheet = sample_exam_sheet(
            owner=user2,
            description='Test desc',
            is_archived=False
        )
        url = archive_sheet_url(exam_sheet.id)
        self.client.get(url)
        exam_sheet.refresh_from_db()

        self.assertFalse(exam_sheet.is_archived)

    # def test_change_status_to_archive_true(self):
    #     """Test that archive view can change exam sheet status to true"""
    #     exam_sheet = sample_exam_sheet(
    #         owner=self.user,
    #         description='Test description',
    #         is_archived=False
    #     )

    #     url = archive_sheet_url(exam_sheet.id)
    #     res = self.client.patch(url)
    #     exam_sheet.refresh_from_db()

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertTrue(exam_sheet.is_archived)

    # def test_change_status_to_archive_false(self):
    #     """Test that archive view can change exam sheet status to false"""
    #     exam_sheet = sample_exam_sheet(
    #         owner=self.user,
    #         description='Test description',
    #         is_archived=True
    #     )

    #     url = archive_sheet_url(exam_sheet.id)
    #     res = self.client.patch(url)
    #     exam_sheet.refresh_from_db()

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertFalse(exam_sheet.is_archived)

    # def test_change_status_to_archive_not_as_user(self):
    #     """Test that only owner can chagne archive status"""
    #     user2 = sample_user(username='testuser2')
    #     exam_sheet = sample_exam_sheet(
    #         owner=user2,
    #         description='Test desc',
    #         is_archived=False
    #     )
    #     url = archive_sheet_url(exam_sheet.id)
    #     res = self.client.patch(url)
    #     exam_sheet.refresh_from_db()

    #     self.assertFalse(exam_sheet.is_archived)

    def test_exam_sheet_deletion(self):
        """Test that owner can delete exam_sheet object"""
        exam_sheet = sample_exam_sheet(owner=self.user)
        exam_sheet2 = sample_exam_sheet(owner=self.user)
        url = detail_url(exam_sheet.id)
        self.client.delete(url)

        sheets_left = ExamSheet.objects.all()

        self.assertEqual(len(sheets_left), 1)
        self.assertIn(exam_sheet2, sheets_left)

    def test_exam_sheet_deletion_by_not_user(self):
        """Test that not owner can't delete exam_sheet"""
        user2 = sample_user(username='testuser123')
        exam_sheet = sample_exam_sheet(owner=user2)
        url = detail_url(exam_sheet.id)
        self.client.delete(url)

        sheets_left = ExamSheet.objects.all()

        self.assertEqual(len(sheets_left), 1)
        self.assertIn(exam_sheet, sheets_left)

    def test_exam_sheet_list_without_filtering(self):
        """Test view that shows every exam sheet"""
        user2 = sample_user(username='testuser2')

        sample_exam_sheet(owner=self.user)
        sample_exam_sheet(owner=self.user, is_archived=True)
        sample_exam_sheet(owner=user2)

        res = self.client.get(NO_FILTERING_EXAM_SHEETS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_exam_sheet_list_filter_by_students(self):
        """Test if passing student query param filters out sheets"""
        user2 = sample_user(username='testuser2')
        user3 = sample_user(username='testuser3')
        exam_sheet = sample_exam_sheet(
            owner=self.user,
            student=user2
        )
        exam_sheet2 = sample_exam_sheet(
            owner=self.user,
            student=user3
        )
        res = self.client.get(
            EXAM_SHEETS_URL,
            {'student': user2.id}
        )
        serializer1 = ExamSheetSerializer(exam_sheet)
        serializer2 = ExamSheetSerializer(exam_sheet2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


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
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_exam_task_list_for_exam_sheet(self):
        """Test that view list all exam tasks for given exam sheet"""
        exam_sheet = sample_exam_sheet(owner=self.user)
        exam_sheet2 = sample_exam_sheet(owner=self.user)
        exam_task = sample_exam_task(
            exam_sheet=exam_sheet,
            title='Task 1'
        )
        sample_exam_task(
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
        user2 = sample_user(username='testuser123')
        exam_sheet = sample_exam_sheet(owner=self.user)
        exam_sheet2 = sample_exam_sheet(owner=user2)
        exam_task = sample_exam_task(
            exam_sheet=exam_sheet,
            title='Test title'
        )
        sample_exam_task(
            exam_sheet=exam_sheet2,
            title='Test title2'
        )

        res = self.client.get(EXAM_TASK_URL)
        serializer = ExamTaskSerializer(exam_task)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer.data, res.data)

    def test_create_exam_task_successful(self):
        """Test creating a new exam sheet"""
        exam_sheet = sample_exam_sheet(owner=self.user)
        payload = {
            'exam_sheet': exam_sheet.pk,
            'title': 'Test title'
        }

        res = self.client.post(EXAM_TASK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = ExamTask.objects.filter(
            exam_sheet=exam_sheet,
            title=payload['title']
        ).exists()

        self.assertTrue(exists)

    def test_create_exam_task_invalid(self):
        """Test creating exam task with invalid payload"""
        payload = {'exam_sheet': ''}
        res = self.client.post(EXAM_TASK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owner_can_create_task(self):
        """Test that only owner can add task to sheet"""
        user2 = sample_user(username='studentuser')
        exam_sheet = sample_exam_sheet(
            owner=user2
        )
        payload = {
            'exam_sheet': exam_sheet.id,
            'title': 'test title'
        }
        self.client.post(EXAM_TASK_URL, payload)

        exam_tasks = ExamTask.objects.all()

        self.assertEqual(len(exam_tasks), 0)

    def test_student_can_change_answer(self):
        """Test that student can change answer in exam task"""
        user2 = sample_user(username='testuser123')
        exam_sheet = sample_exam_sheet(
            owner=user2,
            student=self.user
        )
        exam_task = sample_exam_task(
            exam_sheet=exam_sheet,
            title='Test',
            answer=''
        )
        payload = {'answer': 'test answer'}

        url = exam_task_answer(exam_task.id)
        self.client.patch(url, payload)

        exam_task.refresh_from_db()

        self.assertEqual(exam_task.answer, payload['answer'])

    def test_student_cant_change_more_than_answer(self):
        """Test that student can change only the answer"""
        user2 = sample_user(username='testuser123')
        exam_sheet = sample_exam_sheet(
            owner=user2,
            student=self.user
        )
        title_check = 'test title'
        answer_check = 'test answer'
        exam_task = sample_exam_task(
            exam_sheet=exam_sheet,
            title=title_check,
            answer=answer_check
        )
        payload = {
            'title': 'New title',
            'answer': 'New answer'
        }

        url = exam_task_answer(exam_task.id)
        self.client.patch(url, payload)

        exam_task.refresh_from_db()

        self.assertEqual(exam_task.title, title_check)
        self.assertEqual(exam_task.answer, payload['answer'])

    def test_owner_can_edit(self):
        """Test that owner can edit exam tasks"""
        exam_sheet = sample_exam_sheet(owner=self.user)
        exam_task = ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title='Test title',
            answer='Test answer'
        )
        payload = {
            'title': 'New title',
            'answer': 'New answer'
        }
        url = exam_task_detail(exam_task.id)
        self.client.patch(url, payload)

        exam_task.refresh_from_db()

        self.assertEqual(exam_task.title, payload['title'])
        self.assertEqual(exam_task.answer, payload['answer'])

    def test_not_owner_cant_edit(self):
        """Test that only owner can change data in exam tasks"""
        base_title = 'Check title'
        user2 = sample_user(username='testuser123')
        exam_sheet = sample_exam_sheet(owner=user2)
        exam_task = ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title=base_title,
            answer='test answer'
        )
        payload = {
            'title': 'new title',
            'answer': 'new answer'
        }
        url = exam_task_detail(exam_task.id)
        self.client.patch(url, payload)

        exam_task.refresh_from_db()

        self.assertEqual(exam_task.title, base_title)

    def test_owner_can_delete(self):
        """Test that owner can delete tasks"""
        exam_sheet = sample_exam_sheet(owner=self.user)
        exam_task = ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title='Test title'
        )
        exam_task2 = ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title='test title 2'
        )
        url = exam_task_detail(exam_task2.id)
        self.client.delete(url)

        task_list = ExamTask.objects.all()

        self.assertEqual(len(task_list), 1)
        self.assertIn(exam_task, task_list)
        self.assertNotIn(exam_task2, task_list)

    def test_not_owner_cant_delete(self):
        """Test that only owner can delete tasks"""
        user2 = sample_user(username='testuser')
        exam_sheet = sample_exam_sheet(owner=user2)
        exam_task = ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title='Test title'
        )
        url = exam_task_detail(exam_task.id)
        self.client.delete(url)

        task_list = ExamTask.objects.all()

        self.assertEqual(len(task_list), 1)
        self.assertIn(exam_task, task_list)
