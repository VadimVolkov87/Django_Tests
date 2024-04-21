"""Модуль тестов маршрутизации."""
from http import HTTPStatus

from django.test.client import Client

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

DETAIL_URL = pytest.lazy_fixture('detail_url')
HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
COMMENT_EDIT_URL = pytest.lazy_fixture('comment_edit_url')
COMMENT_DELETE_URL = pytest.lazy_fixture('comment_delete_url')
ANONYMOUS_CLIENT = Client()
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (DETAIL_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (HOME_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (COMMENT_EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (COMMENT_DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
    )
)
def test_pages_availability_for_various_users(url,
                                              parametrized_client,
                                              expected_status):
    """
    Функция тестов.

    Проверка доступности главной страницы, страницы новости
    и страниц регистрации для незарегистрированного пользователя.
    А также проверка доступности редактирования и удаления комментария
    для автора и зарегистрированного пользователя.
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'fixture_url',
    (COMMENT_EDIT_URL, COMMENT_DELETE_URL),
)
def test_redirect_for_anonymous_client(client, fixture_url, login_url):
    """
    Функция тестов.

    Проверка пересылки незарегистрированного пользователя
    при попытке отредактировать или удалить чужой комментарий.
    """
    expected_url = f'{login_url}?next={fixture_url}'
    response = client.get(fixture_url)
    assertRedirects(response, expected_url)
