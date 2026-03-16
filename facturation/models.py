from django.db import models
from decimal import Decimal
from clients.models import Client


class Facture(models.Model):

    TYPE_CHOICES = [
        ('PROFORMA', 'Facture Proforma'),
        ('FACTURE',  'Facture Définitive'),
    ]
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('ENVOYE',    'Envoyé'),
        ('VALIDE',    'Validé'),
        ('PAYE',      'Payé'),
        ('ANNULE',    'Annulé'),
    ]

    # Identification
    numero              = models.CharField(max_length=50, unique=True, blank=True)
    type_doc            = models.CharField(max_length=10, choices=TYPE_CHOICES, default='PROFORMA')
    statut              = models.CharField(max_length=10, choices=STATUT_CHOICES, default='BROUILLON')

    # Relations
    client              = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='factures')
    proforma_origine    = models.ForeignKey(
                            'self', null=True, blank=True,
                            on_delete=models.SET_NULL,
                            related_name='factures_generees'
                          )

    # Dates
    date_creation       = models.DateField(auto_now_add=True)
    date_modification   = models.DateTimeField(auto_now=True)
    validite_jours      = models.IntegerField(default=30)

    # Remise globale (en pourcentage, ex: 10 = 10%)
    remise_pct          = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Montants calculés
    total_ht_brut       = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # avant remise
    montant_remise      = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # montant remise
    total_ht            = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # après remise
    tva_18pct           = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # TVA 18%
    retenue_5pct        = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # retenue
    bic_2pct            = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # BIC
    total_net           = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # total final

    # PDF
    pdf_file            = models.FileField(upload_to='pdfs/factures/', null=True, blank=True)

    # Notes
    notes               = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Facture'
        verbose_name_plural = 'Factures'
        ordering            = ['-date_creation']

    def __str__(self):
        return f"{self.numero} — {self.client.nom_entreprise}"

    def calculer_totaux(self):
        """Recalcule tous les montants depuis les lignes."""
        # 1. Total brut (somme des lignes)
        total_brut          = sum(ligne.total_ht for ligne in self.lignes.all())
        self.total_ht_brut  = total_brut

        # 2. Remise
        self.montant_remise = round(total_brut * self.remise_pct / Decimal('100'), 2)

        # 3. Total HT après remise
        total_ht            = total_brut - self.montant_remise
        self.total_ht       = total_ht

        # 4. TVA 18%
        self.tva_18pct      = round(total_ht * Decimal('0.18'), 2)

        # 5. Retenue 5% et BIC 2%
        self.retenue_5pct   = round(total_ht * Decimal('0.05'), 2)
        self.bic_2pct       = round(total_ht * Decimal('0.02'), 2)

        # 6. Total net final
        self.total_net      = round(total_ht + self.tva_18pct - self.retenue_5pct - self.bic_2pct, 2)

        self.save(update_fields=[
            'total_ht_brut', 'montant_remise', 'total_ht',
            'tva_18pct', 'retenue_5pct', 'bic_2pct', 'total_net'
        ])

    def generer_numero(self):
        """Génère le numéro auto : ESVE26-ID0001-P-0001"""
        if not self.numero:
            annee       = self.date_creation.strftime('%y') if self.date_creation else '26'
            client_id   = str(self.client.id).zfill(4)
            count       = Facture.objects.filter(client=self.client).count()
            numero      = str(count).zfill(4)
            prefix      = 'P' if self.type_doc == 'PROFORMA' else 'F'
            self.numero = f"ESVE{annee}-ID{client_id}-{prefix}-{numero}"
            self.save(update_fields=['numero'])


class LigneFacture(models.Model):

    facture               = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    description           = models.CharField(max_length=300)
    reference_client      = models.CharField(max_length=100, blank=True)
    reference_fournisseur = models.CharField(max_length=100, blank=True)
    prix_unitaire_ht      = models.DecimalField(max_digits=14, decimal_places=2)
    quantite              = models.DecimalField(max_digits=10, decimal_places=2)
    total_ht              = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    delais                = models.CharField(max_length=100, blank=True)
    ordre                 = models.IntegerField(default=0)

    class Meta:
        verbose_name        = 'Ligne de Facture'
        verbose_name_plural = 'Lignes de Facture'
        ordering            = ['ordre']

    def __str__(self):
        return f"{self.description} — {self.quantite} x {self.prix_unitaire_ht}"

    def save(self, *args, **kwargs):
        self.total_ht = round(self.prix_unitaire_ht * self.quantite, 2)
        super().save(*args, **kwargs)
        self.facture.calculer_totaux()