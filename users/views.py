from rest_framework import viewsets, generics, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import PaymentSerializer, UserPaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # Задание 4: Фильтрация и сортировка
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']  # Сортировка по умолчанию - новые сверху

    def get_queryset(self):
        queryset = super().get_queryset()

        # Дополнительная фильтрация для курсов и уроков
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        return queryset


# Дополнительное задание: Профиль пользователя с историей платежей
class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPaymentSerializer
    lookup_field = 'id'