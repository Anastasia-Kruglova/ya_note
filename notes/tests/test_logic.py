from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    INITIAL, ADD, DELETE = 1, 2, 0
    TITLE_1, TITLE_2 = 'Заголовок_1', 'Заголовок_2'
    TEXT = 'Текст'
    SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)

        cls.note = Note.objects.create(
            title=cls.TITLE_1,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.user
        )
        cls.notes_url = reverse('notes:add')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.form_data = {'title': cls.TITLE_2, 'text': cls.TEXT}
        cls.form_data_slug = {
            'title': cls.TITLE_2,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def test_anonymous_cant_add_notes(self):
        self.client.post(self.notes_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.INITIAL)

    def test_user_can_add_note(self):
        response = self.user_client.post(self.notes_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.ADD)

        note = Note.objects.last()
        self.assertEqual((note.title, note.text), (self.TITLE_2, self.TEXT))
        self.assertEqual(note.slug, slugify(self.TITLE_2))
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_exist_slug(self):
        response = self.user_client.post(
            self.notes_url,
            data=self.form_data_slug
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.INITIAL)

    def test_author_can_delete_note(self):
        response = self.user_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.DELETE)

    def test_user_cant_delete_comment_of_another_user(self):
        response = self.another_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.INITIAL)

    def test_author_can_edit_comment(self):
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE_2)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.another_user_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE_1)
