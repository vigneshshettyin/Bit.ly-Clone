from django.db import models
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()


class Link(models.Model):
    short_code = models.CharField(blank=True, null=True, max_length=6, unique=True)
    long_url = models.URLField()
    clicks = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.short_code

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Link'
        verbose_name_plural = 'Links'

    def shorten(self):
        while True:
            short_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
            if not Link.objects.filter(short_code=short_code).exists():
                break
        return short_code

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.shorten()
        super(Link, self).save(*args, **kwargs)
