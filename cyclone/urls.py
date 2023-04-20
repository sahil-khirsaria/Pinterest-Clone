"""cyclone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

from user_account.views import HomePage, UserRegisterView, TodayPinsView

urlpatterns = [
    path('admin/', admin.site.urls),

    # User Login
    path('login', LoginView.as_view(
        template_name='user_account/login.html', redirect_authenticated_user=True), name='login'
    ),

    # User Logout
    path('logout/', LogoutView.as_view(), name='logout'),

    # User Registration
    path('register', UserRegisterView.as_view(), name='registration'),

    # Homepage
    path('', HomePage.as_view(), name='home'),
    path('today/<str:category_name>', TodayPinsView.as_view(), name='today'),

    # Our APPs
    path('user/', include('user_account.urls')),
    path('pinterest/', include('pinterest.urls')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )

handler404 = "pinterest.views.error_404"
