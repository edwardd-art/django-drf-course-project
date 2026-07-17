from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsOwnerOrModeratorOrReadOnly, IsModerator
from .paginators import CoursePaginator, LessonPaginator
from .tasks import send_course_update_notifications  # Импортируем задачу


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModeratorOrReadOnly]
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Course.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModeratorOrReadOnly]
    pagination_class = LessonPaginator

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if not self.request.user.is_superuser:
            try:
                from django.contrib.auth.models import Group
                moderator_group = Group.objects.get(name='moderators')
                is_moderator = self.request.user.groups.filter(id=moderator_group.id).exists()
            except Group.DoesNotExist:
                is_moderator = False

            if not is_moderator and course.owner != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Вы можете создавать уроки только для своих курсов.")

        lesson = serializer.save(owner=self.request.user)

        # Задание 2: Отправляем уведомления подписчикам после создания урока
        # Вызываем задачу асинхронно
        send_course_update_notifications.delay(course.id, lesson.id)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Lesson.objects.all()

        try:
            from django.contrib.auth.models import Group
            moderator_group = Group.objects.get(name='moderators')
            if user.groups.filter(id=moderator_group.id).exists():
                return Lesson.objects.all()
        except Group.DoesNotExist:
            pass

        return Lesson.objects.filter(owner=user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModeratorOrReadOnly]

    def perform_create(self, serializer):
        lesson = serializer.save()
        course = lesson.course

        # Отправляем уведомление только если Celery доступен
        try:
            send_course_update_notifications.delay(course.id, lesson.id)
        except Exception as e:
            # В тестовой среде просто игнорируем
            import sys
            if 'test' not in sys.argv:
                # В продакшене логируем ошибку
                print(f"Celery notification failed: {e}")

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Lesson.objects.all()

        try:
            from django.contrib.auth.models import Group
            moderator_group = Group.objects.get(name='moderators')
            if user.groups.filter(id=moderator_group.id).exists():
                return Lesson.objects.all()
        except Group.DoesNotExist:
            pass

        return Lesson.objects.filter(owner=user)