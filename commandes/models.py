from django.db import models
from decimal import Decimal


class BonCommande(models.Model):

    STATUT_CHOICES = [
        ('BROUILLON',  'Brouillon'),
        ('ENVOYE',     'Envoyé au fournisseur'),
        ('RECU',       'Reçu partiellement'),
        ('RECU_TOTAL', 'Reçu en totalité'),
        ('ANNULE',     'Annulé'),
    ]

    # Identification
    numero              = models.CharField(max_length=50, unique=True, blank=True)
    statut              = models.CharField(max_length=15, choices=STATUT_CHOICES, default='BROUILLON')

    # Fournisseur
    fournisseur_nom     = models.CharField(max_length=200)
    fournisseur_contact = models.CharField(max_length=100, blank=True)
    fournisseur_tel     = models.CharField(max_length=20, blank=True)
    fournisseur_email   = models.EmailField(blank=True)
    fournisseur_adresse = models.TextField(blank=True)

    # Dates
    date_commande       = models.DateField(auto_now_add=True)
    date_modification   = models.DateTimeField(auto_now=True)
    date_livraison_prev = models.DateField(null=True, blank=True)

    # Montants
    total_ht            = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    retenue_5pct        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    bic_2pct            = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net           = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # PDF
    pdf_file            = models.FileField(upload_to='pdfs/commandes/', null=True, blank=True)

    # Notes
    notes               = models.TextField(blank=True)
    objet               = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name        = 'Bon de Commande'
        verbose_name_plural = 'Bons de Commande'
        ordering            = ['-date_commande']

    def __str__(self):
        return f"{self.numero} — {self.fournisseur_nom}"

    def calculer_totaux(self):
        """Recalcule tous les montants depuis les lignes."""
        total               = sum(ligne.total_ht for ligne in self.lignes.all())
        self.total_ht       = total
        self.retenue_5pct   = round(total * Decimal('0.05'), 2)
        self.bic_2pct       = round(total * Decimal('0.02'), 2)
        self.total_net      = round(total - self.retenue_5pct - self.bic_2pct, 2)
        self.save(update_fields=['total_ht', 'retenue_5pct', 'bic_2pct', 'total_net'])

    def generer_numero(self):
        """Génère le numéro auto : ESVE25-BC-0001"""
        if not self.numero:
            from datetime import date
            annee       = date.today().strftime('%y')
            count       = BonCommande.objects.count() + 1
            self.numero = f"ESVE{annee}-BC-{str(count).zfill(4)}"
            self.save(update_fields=['numero'])


class LigneBonCommande(models.Model):

    bon_commande        = models.ForeignKey(BonCommande, on_delete=models.CASCADE, related_name='lignes')
    description         = models.CharField(max_length=300)
    reference           = models.CharField(max_length=100, blank=True)
    prix_unitaire_ht    = models.DecimalField(max_digits=14, decimal_places=2)
    quantite            = models.DecimalField(max_digits=10, decimal_places=2)
    total_ht            = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unite               = models.CharField(max_length=50, blank=True)
    ordre               = models.IntegerField(default=0)

    class Meta:
        verbose_name        = 'Ligne de Bon de Commande'
        verbose_name_plural = 'Lignes de Bon de Commande'
        ordering            = ['ordre']

    def __str__(self):
        return f"{self.description} — {self.quantite} x {self.prix_unitaire_ht}"

    def save(self, *args, **kwargs):
        self.total_ht = round(self.prix_unitaire_ht * self.quantite, 2)
        super().save(*args, **kwargs)
        self.bon_commande.calculer_totaux()