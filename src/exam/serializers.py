from rest_framework import serializers

from exam.models import ExamSheet, ExamTask


class ExamSheetSerializer(serializers.ModelSerializer):
    """Serializer for exam sheet objects"""
    tasks = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ExamTask.objects.all()
    )

    class Meta:
        model = ExamSheet
        fields = (
            'id', 'owner', 'student',
            'description', 'tasks', 'grade', 'is_archived'
            )
        read_only_fields = ('id', 'owner', 'is_archived')


class ExamTaskSerializer(serializers.ModelSerializer):
    """Serializer for exam task"""
    class Meta:
        model = ExamTask
        fields = (
            'id', 'exam_sheet', 'title',
            'description', 'answer', 'points'
        )
        read_only_fields = ('id',)


class ExamTaskStudentSerializer(serializers.ModelSerializer):
    """Exam task serializer for student"""

    class Meta:
        model = ExamTask
        fields = (
            'title', 'description', 'answer',
        )
        read_only_fields = (
            'title', 'description',
        )


class ExamSheetDetailSerializer(ExamSheetSerializer):
    """Serializer for exam sheet detail views"""
    tasks = ExamTaskSerializer(many=True)


class ExamSheetArchiveSerializer(serializers.ModelSerializer):
    """Serializer for changing is_archived status"""
    class Meta:
        model = ExamSheet
        fields = ('id', 'is_archived')
