from django.urls import path
from .views import home,process_photo

urlpatterns = [
    path('', home, name='home'),
    path('process_photo/', process_photo, name='process_photo'),
]