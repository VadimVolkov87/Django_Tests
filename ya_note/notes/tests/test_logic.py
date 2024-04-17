"""Модуль тестирования логики работы приложения."""
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Класс проверки создания заметки."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки.'

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных для тестов."""
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}

    def test_anonymous_user_cant_create_note(self):
        """Метод проверки невозможности создания заметки анонимом."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Метод тестов.

        Проверка возможности создания заметки
        зарегистрированным пользователем.
        """
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):
    """Класс тестов редактирования и удаления заметки."""

    NEW_NOTE_TEXT = 'Новый текст.'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных для тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст заметки',
            slug='probe'
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {'title': 'Заголовок', 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        """Метод проверки, что автор может удалить заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Метод теста.

        Проверка невозможности удаления заметки
        зарегистрированным пользователем.
        """
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Метод проверки, что автор может отредактировать заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Метод теста.

        Проверка, что зарегистрированный пользователь
        не может отредактировать чужую заметку.
        """
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)


class TestAddNoteRepeatedSlug(TestCase):
    """Класс теста невозможности создания заметок с повторяющимcя slug."""

    NEW_NOTE_TEXT = 'Новый текст.'
    NOTE_SLUG = 'probe'

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных для тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст заметки',
            slug=cls.NOTE_SLUG
        )
        cls.add_url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок 2',
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_user_cant_use_repeated_slug(self):
        """Метод проверки невозможности создания заметок с одинаковым slug."""
        response = self.reader_client.post(self.add_url, self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.NOTE_SLUG}{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestAddNoteEmptySlug(TestCase):
    """Класс теста, что slug создается автоматически."""

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных для тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.add_url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
        }

    def test_empty_slug(self):
        """Метод проверки, что slug создается автоматически."""
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug
