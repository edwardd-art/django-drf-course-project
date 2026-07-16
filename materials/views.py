from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsOwnerOrModeratorOrReadOnly, IsModerator
from .paginators import CoursePaginator, LessonPaginator


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModeratorOrReadOnly]
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user

        # Все пользователи могут видеть все курсы (для подписок)
        # Но создавать/изменять/удалять могут только свои
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

        serializer.save(owner=self.request.user)

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

        # Обычные пользователи видят только свои уроки
        return Lesson.objects.filter(owner=user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModeratorOrReadOnly]

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