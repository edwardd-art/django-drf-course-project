from rest_framework import serializers
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'course', 'lesson', 'amount', 'payment_method']
        read_only_fields = ['payment_date']


class UserPaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с историей платежей (дополнительное задание)"""
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']