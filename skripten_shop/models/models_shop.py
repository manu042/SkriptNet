# Django Packages
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# My Packages
from .models_skripten import Article
from .models_users import Student


class ServedArticle(models.Model):
    """
    Ausgegeben Artikel
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, verbose_name='Ausgegeben am')

    class Meta:
        verbose_name = 'Ausgebener Artikel'
        verbose_name_plural = 'Ausgegebene Artikel'

    def __str__(self):
        text = '%s Ausgegeben an %s' % (self.article.name, self.student.user.last_name)
        return text
