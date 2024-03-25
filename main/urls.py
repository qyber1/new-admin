from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import MainView, MISView, RegionView, TFOMSView, \
    CoreUsersView, MiniUsersView, UpdateRegionUserView, AddRegionUserView, UpdateUserView, AddUserView

urlpatterns = [
    path("", login_required(MainView.as_view()), name='main'),
    path("mis/", login_required(MISView.as_view()), name='mis'),
    path('mis/<int:pk>/', login_required(RegionView.as_view(template_name='mis/region.html')), name='one_mis_region'),
    path('mis/<int:pk>/update/<str:username>/',
         login_required(UpdateRegionUserView.as_view(template_name='mis/update_user.html')),
         name='update_user_mis'),
    path('mis/<int:pk>/add-user/', login_required(AddRegionUserView.as_view(template_name='mis/add_user.html')), name='add_user_mis'),
    path("tfoms/", login_required(TFOMSView.as_view()), name='tfoms'),
    path("tfoms/<int:pk>/", login_required(RegionView.as_view(template_name='tfoms/region.html')), name='one_tfoms_region'),
    path("tfoms/<int:pk>/update/<str:username>/",
         login_required(UpdateRegionUserView.as_view(template_name='tfoms/update_user.html')),
         name='update_user_tfoms'),
    path('tfoms/<int:pk>/add-user/', login_required(AddRegionUserView.as_view(template_name='tfoms/add_user.html')), name='add_user_tfoms'),
    path('users/general/', login_required(CoreUsersView.as_view()), name='core_users'),
    path('users/general/update/<str:username>/', login_required(UpdateUserView.as_view(template_name='core_users/update_user.html')), name='update_core_users'),
    path('users/general/add-user', login_required(AddUserView.as_view(template_name='core_users/add_user.html')), name='add_general_user'),
    path('users/mini/', login_required(MiniUsersView.as_view()), name='mini_users'),
    path('users/mini/update/<str:username>/', login_required(UpdateUserView.as_view(template_name='core_users/update_user.html')), name='update_mini_users'),
    path('users/mini/add-user', login_required(AddUserView.as_view(template_name='core_users/add_user.html')), name='add_mini_user'),

]
