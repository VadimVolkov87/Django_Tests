"""Модуль тестов логики работы приложения."""
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

NEW_COMMENT_TEXT = {'text': 'Новый комментарий'}


def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    """
    Функция тестов.

    Проверка, что анонимный пользователь
    не может создать комментарий.
    """
    before_response_comments_count = Comment.objects.count()
    client.post(detail_url, data=form_data)
    after_response_comments_count = Comment.objects.count()
    assert after_response_comments_count == before_response_comments_count


def test_user_can_create_comment(not_author_client, not_author,
                                 news, form_data, detail_url, url_to_comments):
    """
    Функция тестов.

    Проверка, что зарегистрированный пользователь
    может создать комментарий.
    """
    before_response_comments_count = Comment.objects.count()
    response = not_author_client.post(detail_url, data=form_data)
    assertRedirects(response, url_to_comments)
    after_response_comments_count = Comment.objects.count()
    assert after_response_comments_count == before_response_comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == not_author


def test_user_cant_use_bad_words(not_author_client, detail_url):
    """
    Функция тестов.

    Проверка, что любой зарегистрированный пользователь не
    может использовать запрещённые слова.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    before_response_comments_count = Comment.objects.count()
    response = not_author_client.post(
        detail_url,
        data=bad_words_data
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    after_response_comments_count = Comment.objects.count()
    assert after_response_comments_count == before_response_comments_count


def test_author_can_delete_comment(author_client, url_to_comments,
                                   comment_delete_url):
    """
    Функция тестов.

    Проверка, что автор комментария
    может удалить свой комментарий.
    """
    before_response_comments_count = Comment.objects.count()
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    after_response_comments_count = Comment.objects.count()
    assert after_response_comments_count == before_response_comments_count - 1


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_delete_url
        ):
    """
    Функция тестов.

    Проверка, что любой зарегистрированный пользователь не
    может удалить комментарий другого пользователя.
    """
    before_response_comments_count = Comment.objects.count()
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    after_response_comments_count = Comment.objects.count()
    assert after_response_comments_count == before_response_comments_count


def test_author_can_edit_comment(
        author_client, comment_edit_url,
        url_to_comments, author, news
        ):
    """
    Функция тестов.

    Проверка, что автор комментария
    может отредактировать свой комментарий.
    """
    before_response_comments_count = Comment.objects.count()
    response = author_client.post(
        comment_edit_url,
        data=NEW_COMMENT_TEXT
    )
    after_response_comments_count = Comment.objects.count()
    assert after_response_comments_count == before_response_comments_count
    assertRedirects(response, url_to_comments)
    new_comment = Comment.objects.get()
    assert new_comment.text == NEW_COMMENT_TEXT['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_user_cant_edit_comment_of_another_user(not_author_client, detail_url,
                                                comment, comment_edit_url):
    """
    Функция тестов.

    Проверка, что любой зарегистрированный пользователь не
    может отредактировать комментарий другого пользователя.
    """
    before_response_comments_count = Comment.objects.count()
    response = not_author_client.post(
        comment_edit_url,
        data=NEW_COMMENT_TEXT
    )
    after_response_comments_count = Comment.objects.count()
    assert after_response_comments_count == before_response_comments_count
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get()
    assert new_comment.text == comment.text
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news
