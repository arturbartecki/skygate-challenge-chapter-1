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


class ExamTask(models.Model):
    exam_sheet = models.ForeignKey(
        'ExamSheet',
        related_name='tasks',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.title} in exam sheet {self.exam_sheet.id}'
