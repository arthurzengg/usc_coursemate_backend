from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityViewSet, JoinRequestViewSet

router = DefaultRouter()
router.register(r'communities', CommunityViewSet)
router.register(r'join-requests', JoinRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 