"""Модуль тестов для маршрутов."""
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()
HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
NOTE_REDIRECT_URL = reverse('notes:success')
SLUG = 'title'
NOTE_DELETE_URL = reverse('notes:delete', args=(SLUG,))
NOTE_DETAIL_URL = reverse('notes:detail', args=(SLUG,))
NOTE_EDIT_URL = reverse('notes:edit', args=(SLUG,))
USERS_LOGIN_URL = reverse('users:login')
USERS_LOGOUT_URL = reverse('users:logout')
USERS_SIGNUP_URL = reverse('users:signup')


class TestRoutes(TestCase):
    """Класс тестов работы маршрутизации."""

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных для тестов."""
        cls.author = User.objects.create(username='Petrov')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст заметки',
            slug=SLUG,
        )
        cls.urls = (
            HOME_URL,
            LIST_URL,
            NOTE_ADD_URL,
            NOTE_REDIRECT_URL,
            NOTE_DETAIL_URL,
            NOTE_EDIT_URL,
            NOTE_DELETE_URL,
            USERS_SIGNUP_URL,
            USERS_LOGOUT_URL,
            USERS_LOGIN_URL,
        )

    def test_pages_availability_for_anonymous(self):
        """
        Метод тестов.

        Проверка доступности страниц для незарегистрированных пользователей
        и их пересылки при недоступности.
        """
        urls_for_anonymous = (HOME_URL, USERS_LOGIN_URL,
                              USERS_LOGOUT_URL, USERS_SIGNUP_URL)
        for url in self.urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                if url in urls_for_anonymous:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    redirect_url = f'{USERS_LOGIN_URL}?next={url}'
                    self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_auth_user(self):
        """
        Метод тестов.

        Проверка доступности страниц для зарегистрированного пользователя.
        """
        urls_for_author = (NOTE_DETAIL_URL, NOTE_EDIT_URL, NOTE_DELETE_URL)
        for url in self.urls:
            response = self.reader_client.get(url)
            with self.subTest(name=url):
                if url in urls_for_author:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        """Проверка доступности страниц для автора."""
        for url in self.urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
