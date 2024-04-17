"""Модуль тестов проверки контента страниц."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesListPage(TestCase):
    """Класс проверки страницы со списком заметок."""

    LIST_URL = reverse('notes:list')
    NOTES_COUNT = 11

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных к тестам."""
        cls.author = User.objects.create(username='Автор')
        all_notes = [
            Note(
                author=cls.author, title=f'Заголовок {index}',
                text=f'Tекст {index}', slug=f'probe{index}')
            for index in range(cls.NOTES_COUNT)
            ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        """Метод проверки порядка выведения списка заметок."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertIn('note_list', response.context)
        notes_list = response.context['object_list']
        all_id = [note.id for note in notes_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)

    def test_notes_count(self):
        """Метод проверки полноты выведения списка."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, self.NOTES_COUNT)


class TestListAddEditNotePages(TestCase):
    """Класс тестирования страниц создания и редакции заметки."""

    @ classmethod
    def setUpTestData(cls):
        """Метод подготовки данных к тестам."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            author=cls.author, title='Заголовок',
            text='Текст заметки'
        )

    def test_notes_list_for_different_users(self):
        """
        Метод тестов.

        Проверка, что список заметок доступен их автору и
        недоступен зарегистрированному пользователю.
        """
        users = (
            (self.author),
            (self.reader),
        )
        for user in users:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                if user == self.author:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_authorized_client_has_add_note_form(self):
        """Метод проверки наличия формы для страницы создания заметки."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_edit_note_form(self):
        """Метод проверки наличия формы для страницы редактирования заметки."""
        self.client.force_login(self.author)
        response = self.client.get(
            reverse('notes:edit', args=(self.note.slug,)))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
