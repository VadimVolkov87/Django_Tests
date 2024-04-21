"""Модуль тестирования логики работы приложения."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()
LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
NOTE_REDIRECT_URL = reverse('notes:success')
SLUG = 'title'
NOTE_DELETE_URL = reverse('notes:delete', args=(SLUG,))
NOTE_DETAIL_URL = reverse('notes:detail', args=(SLUG,))
NOTE_EDIT_URL = reverse('notes:edit', args=(SLUG,))


class TestNoteCreateEditDelete(TestCase):
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
            slug=SLUG
        )
        cls.form_data = {'title': 'Заголовок 3',
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': 'title_new'}

    def test_anonymous_user_cant_create_note(self):
        """Метод проверки невозможности создания заметки анонимом."""
        before_response_notes_count = Note.objects.count()
        self.client.post(NOTE_ADD_URL, data=self.form_data)
        after_response_notes_count = Note.objects.count()
        self.assertEqual(after_response_notes_count,
                         before_response_notes_count)

    def test_user_can_create_note(self):
        """Метод тестов.

        Проверка возможности создания заметки
        зарегистрированным пользователем.
        """
        Note.objects.get().delete()
        response = self.reader_client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTE_REDIRECT_URL)
        after_response_notes_count = Note.objects.count()
        self.assertEqual(after_response_notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.reader)

    def test_author_can_delete_note(self):
        """Метод проверки, что автор может удалить заметку."""
        before_deletion_notes_count = Note.objects.count()
        response = self.author_client.delete(NOTE_DELETE_URL)
        self.assertRedirects(response, NOTE_REDIRECT_URL)
        after_deletion_notes_count = Note.objects.count()
        self.assertEqual(after_deletion_notes_count,
                         before_deletion_notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Метод теста.

        Проверка невозможности удаления заметки
        зарегистрированным пользователем.
        """
        before_deletion_notes_count = Note.objects.count()
        response = self.reader_client.delete(NOTE_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        after_deletion_notes_count = Note.objects.count()
        self.assertEqual(after_deletion_notes_count,
                         before_deletion_notes_count)

    def test_author_can_edit_note(self):
        """Метод проверки, что автор может отредактировать заметку."""
        before_edit_notes_count = Note.objects.count()
        response = self.author_client.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertRedirects(response, NOTE_REDIRECT_URL)
        after_edit_notes_count = Note.objects.count()
        self.assertEqual(after_edit_notes_count, before_edit_notes_count)
        edit_note = Note.objects.get()
        self.assertEqual(edit_note.title, self.form_data['title'])
        self.assertEqual(edit_note.text, self.form_data['text'])
        self.assertEqual(edit_note.slug, self.form_data['slug'])
        self.assertEqual(edit_note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Метод теста.

        Проверка, что зарегистрированный пользователь
        не может отредактировать чужую заметку.
        """
        before_edit_notes_count = Note.objects.count()
        response = self.reader_client.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        after_edit_notes_count = Note.objects.count()
        self.assertEqual(after_edit_notes_count, before_edit_notes_count)
        initial_note = Note.objects.get()
        self.assertEqual(initial_note.title, self.note.title)
        self.assertEqual(initial_note.text, self.note.text)
        self.assertEqual(initial_note.slug, self.note.slug)
        self.assertEqual(initial_note.author, self.note.author)

    def test_user_cant_use_repeated_slug(self):
        """Метод проверки невозможности создания заметок с одинаковым slug."""
        before_trial_notes_count = Note.objects.count()
        self.form_data.pop('slug')
        self.form_data.update({'slug': SLUG})
        response = self.reader_client.post(NOTE_ADD_URL,
                                           self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{SLUG}{WARNING}'
        )
        after_trial_notes_count = Note.objects.count()
        self.assertEqual(after_trial_notes_count, before_trial_notes_count)

    def test_empty_slug(self):
        """Метод проверки, что slug создается автоматически."""
        Note.objects.get().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(NOTE_ADD_URL,
                                           data=self.form_data)
        self.assertRedirects(response, NOTE_REDIRECT_URL)
        after_trial_notes_count = Note.objects.count()
        self.assertEqual(after_trial_notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.author, self.author)
