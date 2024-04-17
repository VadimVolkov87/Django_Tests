"""Модуль тестов логики работы приложения."""
import pytest
from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

NEW_COMMENT_TEXT = {'text': 'Новый комментарий'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, id_for_args):
    """
    Функция тестов.

    Проверка, что анонимный пользователь
    не может создать комментарий.
    """
    url = reverse('news:detail', args=id_for_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        not_author_client, not_author, news, form_data
     ):
    """
    Функция тестов.

    Проверка, что зарегистрированный пользователь
    может создать комментарий.
    """
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == not_author


@pytest.mark.django_db
def test_user_cant_use_bad_words(not_author_client, id_for_args):
    """
    Функция тестов.

    Проверка, что любой зарегистрированный пользователь не
    может использовать запрещённые слова.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(
        reverse('news:detail', args=id_for_args),
        data=bad_words_data
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    """
    Функция тестов.

    Проверка, что автор комментария
    может удалить свой комментарий.
    """
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.delete(reverse('news:delete', args=(comment.id,)))
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment
     ):
    """
    Функция тестов.

    Проверка, что любой зарегистрированный пользователь не
    может удалить комментарий другого пользователя.
    """
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        id_for_args, comment
     ):
    """
    Функция тестов.

    Проверка, что автор комментария
    может отредактировать свой комментарий.
    """
    response = author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=NEW_COMMENT_TEXT
    )
    url_to_comments = reverse('news:detail', args=id_for_args) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    """
    Функция тестов.

    Проверка, что любой зарегистрированный пользователь не
    может отредактировать комментарий другого пользователя.
    """
    previous_comment_text = comment.text
    response = not_author_client.post(
        reverse('news:edit', args=(comment.id,)),
        data=NEW_COMMENT_TEXT
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == previous_comment_text
