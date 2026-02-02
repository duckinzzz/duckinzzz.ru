from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crstats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battlelog',
            name='battle_time',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='battlelog',
            name='player_tag',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AddIndex(
            model_name='battlelog',
            index=models.Index(fields=['player_tag', '-battle_time'], name='player_time_idx'),
        ),
        migrations.AddConstraint(
            model_name='battlelog',
            constraint=models.UniqueConstraint(
                fields=['player_tag', 'battle_time'],
                name='unique_player_battle'
            ),
        ),
        migrations.AlterModelOptions(
            name='battlelog',
            options={'ordering': ['-battle_time']},
        ),
    ]