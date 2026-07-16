from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Payment, Subscription


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'is_active', 'is_staff']
        read_only_fields = ['is_active', 'is_staff']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'city', 'avatar']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date', 'course', 'lesson', 'amount',
            'payment_method', 'payment_status', 'stripe_payment_intent_id',
            'stripe_checkout_session_id', 'stripe_price_id', 'stripe_product_id',
            'checkout_url'
        ]
        read_only_fields = ['payment_date', 'payment_status', 'checkout_url']


class UserPaymentSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user
        course = attrs.get('course')

        if course and course.owner == user:
            raise serializers.ValidationError("Нельзя подписаться на свой собственный курс")

        return attrs


class StripePaymentCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания платежа через Stripe
    """
    course_id = serializers.IntegerField(
        help_text="ID курса для оплаты",
        required=True
    )

    def validate_course_id(self, value):
        from materials.models import Course
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Курс с таким ID не найден")
        return value


class StripePaymentResponseSerializer(serializers.Serializer):
    """
    Сериализатор ответа при создании платежа через Stripe
    """
    payment_id = serializers.IntegerField(help_text="ID платежа в системе")
    checkout_url = serializers.URLField(help_text="Ссылка на оплату в Stripe")
    payment = PaymentSerializer(help_text="Данные платежа")