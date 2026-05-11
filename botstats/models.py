from django.db import models


class BotData(models.Model):
    bot_name = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.bot_name} — {self.created_at:%Y-%m-%d %H:%M}'
