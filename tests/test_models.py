from django.test import TestCase
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson
from users.models import Payment
from decimal import Decimal

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

class CourseModelTest(TestCase):
    def test_create_course(self):
        course = Course.objects.create(
            name='Test Course',
            description='Test Description'
        )
        self.assertEqual(course.name, 'Test Course')
        self.assertEqual(str(course), 'Test Course')

    def test_course_lessons_count(self):
        course = Course.objects.create(name='Test Course')
        Lesson.objects.create(
            course=course,
            name='Lesson 1',
            description='Test Lesson'
        )
        Lesson.objects.create(
            course=course,
            name='Lesson 2',
            description='Test Lesson 2'
        )
        self.assertEqual(course.lessons.count(), 2)

class LessonModelTest(TestCase):
    def test_create_lesson(self):
        course = Course.objects.create(name='Test Course')
        lesson = Lesson.objects.create(
            course=course,
            name='Test Lesson',
            description='Test Description',
            video_url='https://www.youtube.com/watch?v=test'
        )
        self.assertEqual(lesson.course, course)
        self.assertEqual(str(lesson), 'Test Lesson')

class PaymentModelTest(TestCase):
    def test_create_payment(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        course = Course.objects.create(name='Test Course')
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal('1000.00'),
            payment_method='cash'
        )
        self.assertEqual(payment.amount, Decimal('1000.00'))
        self.assertEqual(payment.payment_method, 'cash')
        self.assertIsNotNone(payment.payment_date)