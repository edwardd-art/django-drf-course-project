from rest_framework import viewsets, generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from .models import User, Payment, Subscription
from .serializers import (
    UserSerializer, UserCreateSerializer, PaymentSerializer,
    UserPaymentSerializer, SubscriptionSerializer
)
from materials.models import Course


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def perform_create(self, serializer):
        if serializer.validated_data['user'] != self.request.user:
            raise PermissionDenied("Вы можете создавать платежи только для себя.")
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подписками
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data.get('course')

        # Проверка на дубликат
        if Subscription.objects.filter(user=user, course=course).exists():
            raise ValidationError({"detail": "Вы уже подписаны на этот курс"})

        # Проверка на подписку на свой курс
        if course.owner == user:
            raise ValidationError({"detail": "Нельзя подписаться на свой собственный курс"})

        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "detail": "Подписка успешно создана",
                    "subscription": serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except ValidationError as e:
            error_detail = e.detail if hasattr(e, 'detail') else str(e)
            return Response(
                {"detail": error_detail if isinstance(error_detail, str) else error_detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        Удаление подписки
        """
        instance = self.get_object()

        # Проверяем, что пользователь удаляет свою подписку
        if instance.user != request.user:
            return Response(
                {"detail": "Вы можете удалять только свои подписки"},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(
            {"detail": "Подписка успешно удалена"},
            status=status.HTTP_200_OK
        )