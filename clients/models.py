from django.db import models


class Client(models.Model):
    REGIME_CHOICES = [
        ('RNI', 'Régime Normal d\'Imposition'),
        ('RSI', 'Régime Simplifié d\'Imposition'),
        ('AI',  'Auto-Entrepreneur'),
    ]

    # Infos principales
    nom_entreprise      = models.CharField(max_length=200)
    contact_nom         = models.CharField(max_length=100, blank=True)
    telephone           = models.CharField(max_length=20, blank=True)
    email               = models.EmailField(blank=True)
    adresse             = models.TextField(blank=True)

    # Infos fiscales
    rccm                = models.CharField(max_length=100, blank=True)
    ifu                 = models.CharField(max_length=50, blank=True)
    regime_imposition   = models.CharField(max_length=10, choices=REGIME_CHOICES, blank=True)
    division_fiscale    = models.CharField(max_length=100, blank=True)

    # Métadonnées
    date_creation       = models.DateTimeField(auto_now_add=True)
    date_modification   = models.DateTimeField(auto_now=True)
    actif               = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Client'
        verbose_name_plural = 'Clients'
        ordering            = ['nom_entreprise']

    def __str__(self):
        return self.nom_entreprise