from django.db import models


class OffreService(models.Model):
    LANGUE_CHOICES = [('fr', 'Français'), ('en', 'English')]

    langue         = models.CharField(max_length=2, choices=LANGUE_CHOICES, default='fr')
    societe        = models.CharField(max_length=200, blank=True)
    destinataires  = models.JSONField(default=list, blank=True)
    texte_custom   = models.TextField(blank=True)
    date_creation  = models.DateTimeField(auto_now_add=True)
    date_modif     = models.DateTimeField(auto_now=True)
    is_deleted     = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Offre de service'
        verbose_name_plural = 'Offres de service'
        ordering            = ['-date_creation']

    def __str__(self):
        return f"{self.societe or 'Sans société'} ({self.langue.upper()}) — {self.date_creation.strftime('%d/%m/%Y')}"

    def soft_delete(self):
        from django.utils import timezone
        self.is_deleted       = True
        self.date_suppression = timezone.now()
        self.save(update_fields=['is_deleted', 'date_suppression'])

    def restore(self):
        self.is_deleted       = False
        self.date_suppression = None
        self.save(update_fields=['is_deleted', 'date_suppression'])