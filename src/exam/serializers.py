from rest_framework import serializers

from exam.models import ExamSheet


class ExamSheetSerializer(serializers.ModelSerializer):
    """Serializer for exam sheet objects"""

    class Meta:
        model = ExamSheet
        fields = ('id', 'owner', 'student', 'description', 'grade', 'is_archived')
        read_only_fields = ('id', 'owner', 'is_archived')
