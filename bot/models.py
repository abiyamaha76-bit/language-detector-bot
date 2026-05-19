from django.db import models


class DetectionLog(models.Model):
    user_id    = models.BigIntegerField(verbose_name="ID пользователя")
    username = models.CharField(max_length=100, blank=True, verbose_name="Username")
    input_text = models.TextField(verbose_name="Input Text")
    detected   = models.CharField(max_length=100, verbose_name="Detected Language")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="date and time")

    class Meta:
        verbose_name = "Language Detection Log"
        verbose_name_plural = "Language Detection Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"User {self.user_id} → {self.detected} ({self.created_at:%d.%m.%Y %H:%M})"


class FindLog(models.Model):
    user_id    = models.BigIntegerField(verbose_name="ID user")
    username = models.CharField(max_length=100, blank=True, verbose_name="Username")
    query      = models.CharField(max_length=200, verbose_name="Query")
    found      = models.BooleanField(verbose_name="Founded?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date and time")

    class Meta:
        verbose_name = "Language Search Log"
        verbose_name_plural = "Language Search Logs"
        ordering = ['-created_at']

    def __str__(self):
        status = "YES" if self.found else "NO"
        return f"User {self.user_id} [{status}] {self.query}"