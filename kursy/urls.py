from django.urls import path
from . import views
from . import api_views  # Uncommented to enable API endpoints

urlpatterns = [
    # Frontend views
    path('', views.login_view, name='login'),
    path('begin/', views.begin, name='begin'),
    
    # API endpoints
    path('api/auth/login/', api_views.login_view_api, name='api_login'),
    path('api/auth/register/', api_views.register_view_api, name='api_register'),
]
