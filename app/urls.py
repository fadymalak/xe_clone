from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignupView, SendMoneyView
from .views import OTPRequestView
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('forget-password/', OTPRequestView.as_view(), name='forget-password'),
    path('send-money/', SendMoneyView.as_view(), name='send-money'),

]
