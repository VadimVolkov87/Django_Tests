"""Модуль тестов контента страниц."""
from django.conf import settings
import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, bunch_of_news, home_url):
    """Функция проверки соответствия количества новостей установленному."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, bunch_of_news, home_url):
    """
    Функция тестов.

    Проверка соответствия порядка выведения новостей установленному.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(not_author_client,
                        bunch_of_comments, news, detail_url):
    """Функция тестов.

    Проверка соответствия порядка выведения комментариев установленному.
    """
    response = not_author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    """
    Функция тестов.

    Проверка, что анонимный пользователь не получает
    на странице форму комментария.
    """
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, detail_url):
    """
    Функция тестов.

    ПРоверка, что зарегистрированный пользователь получает
    на странице форму для комментария и она соответствует
    форме.
    """
    response = not_author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
