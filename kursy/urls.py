from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Frontend views
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('logout/', views.logout_view, name='logout'),
    path('begin/', views.begin, name='begin'),
    path('student/my-courses/', views.StudentMyCoursesView.as_view(), name='student_my_courses'),
    path('student/courses/', views.StudentAvailableCoursesView.as_view(), name='student_available_courses'),
    path('student/courses/<int:pk>/', views.StudentCourseDetailView.as_view(), name='student_course_detail'),
    path('student/courses/<int:course_id>/lessons/<int:lesson_id>/', views.StudentLessonDetailView.as_view(), name='student_lesson_detail'),
    path('instructor/dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('instructor/courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('instructor/courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('instructor/courses/<int:pk>/enrollments/', views.EnrollmentManagerView.as_view(), name='instructor_course_enrollments'),
    path('instructor/courses/<int:course_id>/lessons/', views.CourseLessonsView.as_view(), name='instructor_course_lessons'),
    path('instructor/courses/<int:course_id>/lessons/create/', views.LessonCreateView.as_view(), name='instructor_lesson_create'),
    path('instructor/courses/<int:course_id>/lessons/<int:lesson_id>/edit/', views.LessonUpdateView.as_view(), name='instructor_lesson_edit'),
    
    # API endpoints
    path('api/auth/login/', api_views.login_view_api, name='api_login'),
    path('api/auth/register/', api_views.register_view_api, name='api_register'),
    path('api/auth/password-reset/', api_views.password_reset_api, name='api_password_reset'),
    path('api/courses/', api_views.course_list_create_api, name='api_course_list_create'),
    path('api/courses/<int:pk>/', api_views.course_detail_api, name='api_course_detail'),
    path('api/courses/<int:course_id>/enroll/', api_views.enroll_course_api, name='api_enroll_course'),
    path('api/courses/<int:course_id>/enrollments/', api_views.enrollment_list_api, name='api_enrollment_list'),
    path('api/courses/<int:course_id>/enrollments/bulk-update/', api_views.enrollment_bulk_update_api, name='api_enrollment_bulk_update'),
    path('api/courses/<int:course_id>/lessons/', api_views.lesson_list_create_api, name='api_lesson_list_create'),
    path('api/courses/<int:course_id>/lessons/<int:pk>/', api_views.lesson_detail_api, name='api_lesson_detail'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/attachments/', api_views.attachment_list_create_api, name='api_attachment_list_create'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/attachments/<int:pk>/', api_views.attachment_detail_api, name='api_attachment_detail'),
    # path('api/auth/register/', api_views.register_view_api, name='api_register'),
]
