from django.urls import path
from authentication.api.views import RegisterView, VerifyEmail, LoginView, CreateGroupView

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('email-verify', VerifyEmail.as_view(), name="email-verify"),
    path('create-group', CreateGroupView.as_view(), name="create-group"),
]
