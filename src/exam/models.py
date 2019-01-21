from django.db import models

from django.conf import settings


class ExamSheet(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='owned_exams',
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name='student_exams',
        on_delete=models.SET_NULL
    )
    description = models.CharField(max_length=255)
    grade = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.description
