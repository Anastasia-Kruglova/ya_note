from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.user
        )
        # Адрес страницы с новостью.
        cls.url = reverse('notes:add')

        cls.form_data = {'title': 'Заголовокк', 'text': 'Текст'}
        cls.form_data_slug = {'title': 'Заголовокк', 'text': 'Текст', 'slug': 'slug'}

    def test_anonymous_cant_add_notes(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_add_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.last()
        self.assertEqual((note.title, note.text), ('Заголовокк', 'Текст'))
        self.assertEqual(note.slug, slugify('Заголовокк'))
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_exist_slug(self):
        response = self.auth_client.post(self.url, data=self.form_data_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'slug{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_edit_and_delete(self):
        pass
