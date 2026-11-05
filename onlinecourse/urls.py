"""URL routes for the Online Course App.

Includes the two exam routes required by the Course 9 final project:
  - <course_id>/submit/            -> views.submit
  - course/<course_id>/submission/<submission_id>/result/
                                   -> views.show_exam_result
"""
from django.urls import path

from . import views

app_name = 'onlinecourse'
urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<int:course_id>/', views.CourseDetailView.as_view(),
         name='course_details'),
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),
    path('<int:course_id>/submit/', views.submit, name='submit'),
    path('course/<int:course_id>/submission/<int:submission_id>/result/',
         views.show_exam_result, name='show_exam_result'),
    path('registration/', views.registration_request, name='registration'),
]
