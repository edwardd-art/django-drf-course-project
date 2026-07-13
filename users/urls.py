from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, UserProfileView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:id>/profile/', UserProfileView.as_view(), name='user-profile'),
]