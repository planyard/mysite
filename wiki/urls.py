from django.urls import path, re_path
from . import views

app_name = 'wiki'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    re_path(r'^Register/', views.register_page, name='register'),
    re_path(r'^Login/', views.WikiLoginView.as_view(), name='login'),
    re_path(r'^Logout/', views.WikiLogoutView.as_view(), name='logout'),
    re_path(r'^Upload/', views.upload_file, name='upload'),
    path('Delete/<int:pk>/', views.delete_file, name='delete'),
    path('<str:pk>/', views.PageView.as_view(), name='pageview'),
    path('<str:pk>/edit/', views.EditView.as_view(), name='edit'),
]