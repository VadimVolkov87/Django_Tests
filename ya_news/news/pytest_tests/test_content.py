"""Модуль тестов контента страниц."""
import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, bunch_of_news):
    """Функция проверки соответствия количества новостей установленному."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, bunch_of_news):
    """
    Функция тестов.

    Проверка соответствия порядка выведения новостей установленному.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(not_author_client, bunch_of_comments):
    """Функция тестов.

    Проверка соответствия порядка выведения комментариев установленному.
    """
    detail_url = reverse('news:detail', args=(bunch_of_comments.news.id,))
    response = not_author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_for_args):
    """
    Функция тестов.

    Проверка, что анонимный пользователь не получает
    на странице форму комментария.
    """
    detail_url = reverse('news:detail', args=id_for_args)
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(not_author_client, id_for_args):
    """
    Функция тестов.

    ПРоверка, что зарегистрированный пользователь получает
    на странице форму для комментария и она соответствует
    форме.
    """
    detail_url = reverse('news:detail', args=id_for_args)
    response = not_author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
