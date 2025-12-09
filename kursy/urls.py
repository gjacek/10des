from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Frontend views
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('begin/', views.begin, name='begin'),
    path('student/my-courses/', views.StudentMyCoursesView.as_view(), name='student_my_courses'),
    path('instructor/dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('instructor/courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('instructor/courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('instructor/courses/<int:pk>/enrollments/', views.EnrollmentManagerView.as_view(), name='instructor_course_enrollments'),
    
    # API endpoints
    path('api/auth/login/', api_views.login_view_api, name='api_login'),
    path('api/courses/', api_views.course_list_create_api, name='api_course_list_create'),
    path('api/courses/<int:pk>/', api_views.course_detail_api, name='api_course_detail'),
    path('api/courses/<int:course_id>/enrollments/', api_views.enrollment_list_api, name='api_enrollment_list'),
    path('api/courses/<int:course_id>/enrollments/bulk-update/', api_views.enrollment_bulk_update_api, name='api_enrollment_bulk_update'),
    # path('api/auth/register/', api_views.register_view_api, name='api_register'),
]
