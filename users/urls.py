from django.urls import path
from django.contrib.auth.views import LoginView
from .views import register, login, forgotPassword, resetpassword_validate, resetPassword, user_profile, organizer_profile, my_orders, create_event, edit_event

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name = 'register'),

    path('forgotPassword/',  forgotPassword, name = 'forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', resetpassword_validate, name = 'resetpassword_validate'),
    path('resetPassword/', resetPassword, name = 'resetPassword'),

    path('user_profile/', user_profile, name='user_profile'),
    path('organizer_profile/', organizer_profile, name='organizer_profile'),

    path('my_orders/', my_orders, name='my_orders'),
    path('create_event/', create_event, name='create_event'),
    path('events/<int:event_id>/edit/', edit_event, name='edit_event'),
]
