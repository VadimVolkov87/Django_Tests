"""Модуль тестов проверки контента страниц."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()
LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
SLUG = 'zagolovok'
NOTE_EDIT_URL = reverse('notes:edit', args=(SLUG,))


class TestNotesListPage(TestCase):
    """Класс проверки страницы со списком заметок."""

    NOTES_COUNT = 11

    @classmethod
    def setUpTestData(cls):
        """Метод подготовки данных к тестам."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        all_notes = [
            Note(
                author=cls.author, title=f'Заголовок {index}',
                text=f'Tекст {index}', slug=f'probe{index}')
            for index in range(cls.NOTES_COUNT)
            ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        """Метод проверки порядка выведения списка заметок."""
        response = self.author_client.get(LIST_URL)
        self.assertIn('note_list', response.context)
        notes_list = response.context['object_list']
        all_id = [note.id for note in notes_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)

    def test_notes_count(self):
        """Метод проверки полноты выведения списка."""
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, self.NOTES_COUNT)


class TestListAddEditNotePages(TestCase):
    """Класс тестирования страниц создания и редакции заметки."""

    @ classmethod
    def setUpTestData(cls):
        """Метод подготовки данных к тестам."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author, title='Заголовок',
            text='Текст заметки',
            slug=SLUG
        )

    def test_notes_list_for_author(self):
        """Метод проверки, что список заметок доступен их автору."""
        response = self.author_client.get(LIST_URL)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, 1)
        list_note = response.context['object_list'].get()
        self.assertEqual(list_note.title, self.note.title)
        self.assertEqual(list_note.text, self.note.text)

    def test_notes_list_for_logged_user(self):
        """
        Метод тестов.

        Проверка, что список заметок недоступен
        зарегистрированному пользователю.
        """
        response = self.reader_client.get(LIST_URL)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, 0)

    def test_authorized_user_has_add_edit_note_form(self):
        """
        Метод тестов.

        Проверка наличия формы для страниц создания
        и редактирования заметки.
        """
        urls = (
            NOTE_ADD_URL,
            NOTE_EDIT_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
