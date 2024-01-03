from django.db import models

class Dentista(models.Model):
    class Meta:
        db_table = 'dentistas'

    nome = models.CharField(max_length=100)
    cfo = models.BigIntegerField()
    uf = models.CharField(max_length=2)

    def __str__(self):
        return self.nome