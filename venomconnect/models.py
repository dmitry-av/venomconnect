from django.db import models


class Wallet(models.Model):
    name = models.CharField(max_length=255, unique=True)
    seed_key = models.TextField()

    def __str__(self):
        return self.name


class Proxy(models.Model):
    host = models.CharField(max_length=255)
    port = models.SmallIntegerField()
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.host
