from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('translate/', views.translate_text, name='translate_text'),
    path('clear-history/', views.clear_history, name='clear_history'),
    path('delete-history-item/', views.delete_history_item, name='delete_history_item'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
