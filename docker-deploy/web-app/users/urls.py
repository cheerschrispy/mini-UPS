from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import packageCreateView


urlpatterns = [
    #path('', views.trackPackage, name='track'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    #path('trackPackage/', views.trackPackage, name='track'),
    path('ownPackages/', views.viewOwnOrder, name='viewOwnOrder'),
    path('<int:package_id>/update',views.updateInfo, name='update'),
    path('package/new/', packageCreateView.as_view(), name='package-create')
    ]