"""Модуль тестов маршрутизации."""
from http import HTTPStatus

from django.test.client import Client
from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('detail_url'), Client(), HTTPStatus.OK),
        (reverse('news:home'), Client(), HTTPStatus.OK),
        (reverse('users:login'), Client(), HTTPStatus.OK),
        (reverse('users:logout'), Client(), HTTPStatus.OK),
        (reverse('users:signup'), Client(), HTTPStatus.OK),
        (pytest.lazy_fixture('comment_edit_url'),
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('comment_delete_url'),
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('comment_edit_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('comment_delete_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
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
    (pytest.lazy_fixture('comment_edit_url'),
     pytest.lazy_fixture('comment_delete_url')),
)
def test_redirect_for_anonymous_client(client, fixture_url):
    """
    Функция тестов.

    Проверка пересылки незарегистрированного пользователя
    при попытке отредактировать или удалить чужой комментарий.
    """
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={fixture_url}'
    response = client.get(fixture_url)
    assertRedirects(response, expected_url)
