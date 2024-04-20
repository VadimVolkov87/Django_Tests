"""Модуль фикстур для тестов приложения."""
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура создания объекта автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура создания объекта пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура создания аутентифицированного автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура создания аутентифицированного пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура создания объекта новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )
    return news


@pytest.fixture
def comment(author, news):
    """Фикстура создания объекта комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def id_for_args(news):  # убрать фикстуру
    """Фикстура создающая id новости."""
    return (news.id,)


@pytest.fixture
def bunch_of_news():
    """Фикстура создающая несколько объектов новостей."""
    today = datetime.now()
    all_news = [
        News(title=f'Новость {index}', text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def bunch_of_comments(author, news):
    """Фикстура создающая несколько объектов комментариев."""
    for index in range(10):
        Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )


@pytest.fixture
def form_data():
    """Фикстура создающая данные для формы комментария."""
    return {
        'text': 'Текст комментария'
    }


@pytest.fixture
def home_url():
    """Фикстура создания маршрута главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """Фикстура создания маршрута страницы отдельной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_edit_url(comment):
    """Фикстура создания маршрута редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    """Фикстура создания маршрута удаления комментария."""
    return reverse('news:delete', args=(comment.id,))
