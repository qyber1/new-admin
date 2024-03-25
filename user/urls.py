from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginUser

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

]