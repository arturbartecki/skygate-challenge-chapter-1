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
