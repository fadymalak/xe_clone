from django.urls import path
from .views import SignUpView, ForgetPasswordView, SendMoneyView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget_password'),
    path('send-money/', SendMoneyView.as_view(), name='send_money'),
]
