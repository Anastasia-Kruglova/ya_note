from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    TEMPLATE_NAME = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Залогиненный пользователь')
        cls.note = Note.objects.create(
            title='tit',
            text='tet',
            author=cls.user
        )

    def test_anonymous_without_list(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertNotContains(response, self.TEMPLATE_NAME)

    def test_user_with_list(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:home', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(
                'Пользователь может выбрать в меню - список всех записей',
                name=name,
            ):
                self.client.force_login(self.user)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertContains(response, self.TEMPLATE_NAME)
