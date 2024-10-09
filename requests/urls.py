"""requests URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from requests_handler.views import (login_view, dashboard_view, create_request_view,
                                    update_request_status_view, register_view, profile_view,
                                    delete_request_by_id, delete_user_by_id, admin_view,
                                    mark_feedback_as_read, mark_error_as_read, report_view,
                                    otp_login_view, add_otp_device, otp_device_qr)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('create/', create_request_view, name='create_request'),
    path('update/', update_request_status_view, name='update_request_status'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('admin/', admin_view, name='admin'),
    path('admin/delete_request/', delete_request_by_id, name='delete_request_by_id'),
    path('admin/delete_user/', delete_user_by_id, name='delete_user_by_id'),
    path('admin/feedback/<int:feedback_id>/mark_as_read/', mark_feedback_as_read, name='mark_feedback_as_read'),
    path('admin/mark_error_as_read/<int:error_id>/', mark_error_as_read, name='mark_error_as_read'),
    path('report/', report_view, name='report'),
    path('otp_login/', otp_login_view, name='otp_login'),
    path('add_otp_device/', add_otp_device, name='add_otp_device'),  # URL для добавления устройства
    path('show_qr_code/<int:device_id>/', otp_device_qr, name='show_qr_code'),  # URL для QR-кода
]