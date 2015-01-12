from django.test import TestCase
from .models import TestModel


class TestSimple(TestCase):

    def test_a(self):
        model = TestModel.objects.create(char='a')
        self.assertEqual(model.char, 'a')