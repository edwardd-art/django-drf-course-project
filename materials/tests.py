from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from users.models import User, Subscription
from materials.models import Course, Lesson
from materials.serializers import LessonSerializer


class LessonCRUDTests(APITestCase):
    """
    Тесты для CRUD операций уроков
    """

    def setUp(self):
        """
        Подготовка тестовых данных
        """
        # Создаем группы
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')

        # Создаем пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='user123456',
            first_name='Test',
            last_name='User'
        )

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='mod123456',
            first_name='Moderator',
            last_name='Test'
        )
        self.moderator.groups.add(self.moderator_group)

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='other123456',
            first_name='Other',
            last_name='User'
        )

        # Создаем курс
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Description',
            owner=self.user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Lesson Description',
            video_url='https://www.youtube.com/watch?v=test123',
            course=self.course,
            owner=self.user
        )

        # URL для тестов
        self.lessons_url = '/api/lessons/'
        self.lesson_detail_url = f'/api/lessons/{self.lesson.id}/'

    def test_create_lesson_with_valid_youtube_url(self):
        """
        Тест создания урока с валидной YouTube ссылкой
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'New Lesson',
            'description': 'New Description',
            'video_url': 'https://www.youtube.com/watch?v=valid123',
            'course': self.course.id
        }

        response = self.client.post(self.lessons_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Lesson')
        self.assertEqual(response.data['owner'], self.user.id)

    def test_create_lesson_with_invalid_youtube_url(self):
        """
        Тест создания урока с невалидной ссылкой (не YouTube)
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'Invalid Lesson',
            'description': 'Invalid Description',
            'video_url': 'https://vimeo.com/watch?v=invalid',
            'course': self.course.id
        }

        response = self.client.post(self.lessons_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', response.data)
        self.assertIn('YouTube', str(response.data['video_url']))

    def test_create_lesson_without_youtube_url(self):
        """
        Тест создания урока без ссылки (допустимо)
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'No Video Lesson',
            'description': 'No Video Description',
            'course': self.course.id
        }

        response = self.client.post(self.lessons_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'No Video Lesson')

    def test_get_lessons_list(self):
        """
        Тест получения списка уроков
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lessons_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Lesson')

    def test_get_lesson_detail(self):
        """
        Тест получения одного урока
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson')
        self.assertEqual(response.data['owner'], self.user.id)

    def test_update_lesson_owner(self):
        """
        Тест обновления урока владельцем
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'Updated Lesson Name',
            'description': 'Updated Description',
            'video_url': 'https://www.youtube.com/watch?v=updated123',
            'course': self.course.id
        }

        response = self.client.put(self.lesson_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Lesson Name')

    def test_update_lesson_other_user(self):
        """
        Тест обновления урока другим пользователем (должен быть запрет)
        """
        self.client.force_authenticate(user=self.other_user)

        data = {
            'name': 'Hacked Lesson',
            'description': 'Hacked Description',
            'video_url': 'https://www.youtube.com/watch?v=hacked123',
            'course': self.course.id
        }

        response = self.client.put(self.lesson_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_lesson_owner(self):
        """
        Тест удаления урока владельцем
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator(self):
        """
        Тест удаления урока модератором (должен быть запрет)
        """
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_moderator(self):
        """
        Тест создания урока модератором (должен быть запрет на создание)
        """
        self.client.force_authenticate(user=self.moderator)

        data = {
            'name': 'Moderator Lesson',
            'description': 'Moderator Description',
            'video_url': 'https://www.youtube.com/watch?v=mod123',
            'course': self.course.id
        }

        response = self.client.post(self.lessons_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_lesson_moderator(self):
        """
        Тест просмотра урока модератором (может видеть все)
        """
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson')

    def test_update_lesson_moderator(self):
        """
        Тест обновления урока модератором (может обновлять)
        """
        self.client.force_authenticate(user=self.moderator)

        data = {
            'name': 'Moderator Updated',
            'description': 'Updated by Moderator',
            'video_url': 'https://www.youtube.com/watch?v=mod_update',
            'course': self.course.id
        }

        response = self.client.put(self.lesson_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Moderator Updated')


class SubscriptionTests(APITestCase):
    """
    Тесты для функционала подписки
    """

    def setUp(self):
        """
        Подготовка тестовых данных
        """
        # Создаем пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='user123456',
            first_name='Test',
            last_name='User'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='other123456',
            first_name='Other',
            last_name='User'
        )

        # Создаем курс от имени другого пользователя
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Description',
            owner=self.other_user
        )

        # Создаем свой курс (для проверки запрета подписки на свой курс)
        self.my_course = Course.objects.create(
            name='My Course',
            description='My Description',
            owner=self.user
        )

        # URL для тестов
        self.subscriptions_url = '/api/subscriptions/'

    def test_create_subscription(self):
        """
        Тест создания подписки
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'course': self.course.id
        }

        response = self.client.post(self.subscriptions_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Подписка успешно создана')
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(Subscription.objects.first().user, self.user)
        self.assertEqual(Subscription.objects.first().course, self.course)

    def test_create_duplicate_subscription(self):
        """
        Тест создания дублирующей подписки
        """
        self.client.force_authenticate(user=self.user)

        # Создаем первую подписку через API
        data = {'course': self.course.id}
        response1 = self.client.post(self.subscriptions_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Пытаемся создать вторую
        response2 = self.client.post(self.subscriptions_url, data, format='json')

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('уже подписаны', str(response2.data['detail']))

    def test_create_subscription_to_own_course(self):
        """
        Тест создания подписки на свой курс (должен быть запрет)
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'course': self.my_course.id
        }

        response = self.client.post(self.subscriptions_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверяем наличие ошибки в ответе
        self.assertIn('detail', response.data)
        self.assertIn('свой собственный курс', str(response.data['detail']))

    def test_delete_subscription(self):
        """
        Тест удаления подписки
        """
        self.client.force_authenticate(user=self.user)

        # Создаем подписку через API
        data = {'course': self.course.id}
        create_response = self.client.post(self.subscriptions_url, data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        subscription_id = create_response.data['subscription']['id']

        # Удаляем
        response = self.client.delete(f'{self.subscriptions_url}{subscription_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Подписка успешно удалена')
        self.assertEqual(Subscription.objects.count(), 0)

    def test_delete_other_user_subscription(self):
        """
        Тест удаления чужой подписки (должен быть запрет)
        """
        self.client.force_authenticate(user=self.user)

        # Создаем подписку для другого пользователя
        subscription = Subscription.objects.create(user=self.other_user, course=self.course)

        # Пытаемся удалить
        response = self.client.delete(f'{self.subscriptions_url}{subscription.id}/')

        # Должен быть 404, так как пользователь не видит чужие подписки
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_subscriptions(self):
        """
        Тест получения списка подписок
        """
        self.client.force_authenticate(user=self.user)

        # Создаем подписки
        Subscription.objects.create(user=self.user, course=self.course)
        Subscription.objects.create(user=self.other_user, course=self.course)

        response = self.client.get(self.subscriptions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа (с пагинацией или без)
        if 'results' in response.data:
            # С пагинацией
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['user'], self.user.id)
        else:
            # Без пагинации (если отключена)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['user'], self.user.id)

    def test_is_subscribed_field_in_course(self):
        """
        Тест поля is_subscribed в сериализаторе курса
        """
        self.client.force_authenticate(user=self.user)

        # Создаем курс от имени другого пользователя
        another_user = User.objects.create_user(
            email='another@test.com',
            password='another123456'
        )
        course = Course.objects.create(
            name='Another Course',
            description='Another Description',
            owner=another_user
        )

        # Создаем подписку через API
        data = {'course': course.id}
        create_response = self.client.post(self.subscriptions_url, data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Получаем курс
        response = self.client.get(f'/api/courses/{course.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_is_subscribed_field_without_auth(self):
        """
        Тест поля is_subscribed без авторизации
        """
        # Не авторизуемся
        response = self.client.get(f'/api/courses/{self.course.id}/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination_for_courses(self):
        """
        Тест пагинации для курсов
        """
        self.client.force_authenticate(user=self.other_user)

        # Создаем несколько курсов
        for i in range(8):
            Course.objects.create(
                name=f'Course {i}',
                description=f'Description {i}',
                owner=self.other_user
            )

        response = self.client.get('/api/courses/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 5)  # page_size = 5

    def test_pagination_for_lessons(self):
        """
        Тест пагинации для уроков
        """
        self.client.force_authenticate(user=self.user)

        # Создаем несколько уроков
        for i in range(15):
            Lesson.objects.create(
                name=f'Lesson {i}',
                description=f'Description {i}',
                video_url='https://www.youtube.com/watch?v=test123',
                course=self.course,
                owner=self.user
            )

        response = self.client.get('/api/lessons/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(len(response.data['results']), 10)  # page_size = 10

    def test_pagination_with_page_size_param(self):
        """
        Тест пагинации с параметром page_size
        """
        self.client.force_authenticate(user=self.other_user)

        # Создаем несколько курсов
        for i in range(15):
            Course.objects.create(
                name=f'Course {i}',
                description=f'Description {i}',
                owner=self.other_user
            )

        response = self.client.get('/api/courses/?page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)


class VideoURLValidationTests(APITestCase):
    """
    Тесты для валидации YouTube ссылок
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='user123456'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_valid_youtube_com_url(self):
        """
        Тест валидной ссылки youtube.com
        """
        data = {
            'name': 'Test Lesson',
            'description': 'Test Description',
            'video_url': 'https://www.youtube.com/watch?v=valid123',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_youtu_be_url(self):
        """
        Тест валидной ссылки youtu.be
        """
        data = {
            'name': 'Test Lesson',
            'description': 'Test Description',
            'video_url': 'https://youtu.be/valid123',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_m_youtube_url(self):
        """
        Тест валидной ссылки m.youtube.com
        """
        data = {
            'name': 'Test Lesson',
            'description': 'Test Description',
            'video_url': 'https://m.youtube.com/watch?v=valid123',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_url_vimeo(self):
        """
        Тест невалидной ссылки (Vimeo)
        """
        data = {
            'name': 'Test Lesson',
            'description': 'Test Description',
            'video_url': 'https://vimeo.com/123456',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('YouTube', str(response.data['video_url']))

    def test_invalid_url_google(self):
        """
        Тест невалидной ссылки (Google)
        """
        data = {
            'name': 'Test Lesson',
            'description': 'Test Description',
            'video_url': 'https://google.com',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('YouTube', str(response.data['video_url']))

    def test_invalid_url_other(self):
        """
        Тест невалидной ссылки (другой сайт)
        """
        data = {
            'name': 'Test Lesson',
            'description': 'Test Description',
            'video_url': 'https://example.com/video',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('YouTube', str(response.data['video_url']))