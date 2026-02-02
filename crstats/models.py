from django.db import models


class BattleLog(models.Model):
    battle_time = models.DateTimeField(db_index=True)
    player_tag = models.CharField(max_length=255, db_index=True)
    enemy_tag = models.CharField(max_length=255)
    starting_trophies = models.IntegerField()
    trophy_change = models.IntegerField()
    raw_data = models.JSONField()

    class Meta:
        ordering = ['-battle_time']
        indexes = [
            models.Index(fields=['player_tag', '-battle_time'], name='player_time_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['player_tag', 'battle_time'],
                name='unique_player_battle'
            )
        ]

    def __str__(self):
        return f"{self.player_tag} - {self.battle_time}"
