from django.urls import path
from .views import GoogleLoginView, GoogleCallbackView, SyncUserView

urlpatterns = [
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    path('sync-user/', SyncUserView.as_view(), name='sync-user'),
]