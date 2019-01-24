from django.urls import path, include
from rest_framework.routers import DefaultRouter

from exam import views

router = DefaultRouter()
router.register('exam-sheets', views.ExamSheetViewSet)
router.register('exam-tasks', views.ExamTaskViewSet)

app_name = 'exam'

urlpatterns = [
    path('', include(router.urls))
]
