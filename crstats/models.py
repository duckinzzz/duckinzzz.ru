from django.db import models

class BattleLog(models.Model):
    battle_time = models.DateTimeField()
    player_tag = models.CharField(max_length=255)
    enemy_tag = models.CharField(max_length=255)
    starting_trophies = models.IntegerField()
    trophy_change = models.IntegerField()
    raw_data = models.JSONField()

    class Meta:
        ordering = ['player_tag', 'battle_time']
