# Generated by Django 2.1.5 on 2019-01-21 22:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0002_auto_20190121_0051'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('answer', models.TextField(blank=True, null=True)),
                ('points', models.IntegerField(blank=True, null=True)),
                ('exam_sheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='exam.ExamSheet')),
            ],
        ),
    ]
