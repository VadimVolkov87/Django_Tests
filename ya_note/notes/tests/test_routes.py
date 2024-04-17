"""Модуль тестов для маршрутов."""
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс тестов работы маршрутизации."""

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных для тестов."""
        cls.author = User.objects.create(username='Petrov')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст заметки'
        )

    def test_pages_availability(self):
        """Тест доступности страниц для незарегистрированных пользователей."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Метод тестов.

        Проверка, что зарегистрованному пользователю доступны
        страницы списка заметок, добавления и успешного
        завершения добавления.
        """
        self.client.force_login(self.author)
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest(user=self.author, name=name):
                url = reverse(name)
                responce = self.client.get(url)
                self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Тест для зарегистрованного пользователя.

        Проверка доступности записи, её правки и удаления
        для автора и стороннего зарегистрованного пользователя.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест проверки пересылки незарегистрированного пользователя."""
        login_url = reverse('users:login')
        for name in (
                'notes:add', 'notes:detail', 'notes:success',
                'notes:edit', 'notes:delete', 'notes:list'
        ):
            with self.subTest(name=name):
                if (name == 'notes:add' or name == 'notes:list'
                   or name == 'notes:success'):
                    url = reverse(name)
                else:
                    url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
