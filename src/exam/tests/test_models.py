from django.test import TestCase

from exam import models
from django.contrib.auth import get_user_model


def sample_user(username='arturbartecki', password='testpassword'):
    """Helper function for creating sample user"""
    return get_user_model().objects.create_user(username, password)


class ModelTests(TestCase):

    def test_exam_sheet_str(self):
        """Test exam sheet str representation"""
        exam_sheet = models.ExamSheet.objects.create(
            owner=sample_user(),
            description="Simple exam sheet description"
        )

        self.assertEqual(str(exam_sheet), exam_sheet.description)

    def test_exam_task_str(self):
        """Test exam task str representation"""
        exam_sheet = models.ExamSheet.objects.create(
            owner=sample_user(),
            description='Test'
        )
        exam_task = models.ExamTask.objects.create(
            exam_sheet=exam_sheet,
            title='First task'
        )

        self.assertEqual(
            str(exam_task),
            f'{exam_task.title} in exam sheet {exam_sheet.id}')
