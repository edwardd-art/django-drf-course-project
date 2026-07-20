from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Habit

User = get_user_model()


class HabitModelTest(TestCase):
    def test_create_habit(self):
        user = User.objects.create_user(
            email='test@test.com',
            password='test123'
        )
        habit = Habit.objects.create(
            user=user,
            place='Home',
            time='08:00:00',
            action='Morning exercise',
            execution_time=60,
            is_public=False
        )
        self.assertEqual(habit.action, 'Morning exercise')
        self.assertEqual(habit.user, user)

    def test_habit_validation_reward_and_related(self):
        user = User.objects.create_user(
            email='test@test.com',
            password='test123'
        )

        # Создаем приятную привычку
        pleasant = Habit.objects.create(
            user=user,
            place='Home',
            time='08:00:00',
            action='Pleasant habit',
            execution_time=60,
            is_pleasant=True
        )

        # Пытаемся создать полезную с reward и related_habit
        with self.assertRaises(Exception):
            Habit.objects.create(
                user=user,
                place='Home',
                time='08:00:00',
                action='Bad habit',
                execution_time=60,
                reward='Reward',
                related_habit=pleasant
            )


class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='user123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            'place': 'Home',
            'time': '08:00:00',
            'action': 'Exercise',
            'execution_time': 60,
            'is_public': False
        }

    def test_create_habit(self):
        response = self.client.post('/api/habits/', self.habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'Exercise')

    def test_list_habits(self):
        # Создаем привычку
        self.client.post('/api/habits/', self.habit_data, format='json')

        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_public_habits(self):
        # Создаем публичную привычку
        public_habit = self.habit_data.copy()
        public_habit['is_public'] = True
        self.client.post('/api/habits/', public_habit, format='json')

        # Другой пользователь должен видеть публичную
        other_user = User.objects.create_user(
            email='other@test.com',
            password='other123'
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)