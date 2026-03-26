from django.db import models
from decimal import Decimal
from datetime import date
from clients.models import Client


TERMES_PAIEMENT_CHOICES = [
    ('100% à la commande',           '100% à la commande'),
    ('15 jours date de facturation', '15 jours date de facturation'),
    ('30 jours date de facturation', '30 jours date de facturation'),
    ('60 jours date de facturation', '60 jours date de facturation'),
]


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

    # Termes de paiement ← NOUVEAU
    termes_paiement     = models.CharField(
                            max_length=50,
                            choices=TERMES_PAIEMENT_CHOICES,
                            default='100% à la commande',
                            blank=True
                          )

    # Options de calcul
    appliquer_remise    = models.BooleanField(default=False)
    appliquer_tva       = models.BooleanField(default=False)
    appliquer_retenue   = models.BooleanField(default=False)
    appliquer_bic       = models.BooleanField(default=False)
    appliquer_transport = models.BooleanField(default=False)

    # Remise
    remise_pct          = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Transport (montant manuel)
    montant_transport   = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Montants calculés
    total_ht_brut       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    montant_remise      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_ht            = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tva_18pct           = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    retenue_5pct        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    bic_2pct            = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net           = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Fichiers et notes
    pdf_file            = models.FileField(upload_to='pdfs/factures/', null=True, blank=True)
    notes               = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Facture'
        verbose_name_plural = 'Factures'
        ordering            = ['-date_creation']

    def __str__(self):
        return f"{self.numero} — {self.client.nom_entreprise}"

    def calculer_totaux(self):
        total_brut         = sum(ligne.total_ht for ligne in self.lignes.all())
        self.total_ht_brut = total_brut

        if self.appliquer_remise and self.remise_pct > 0:
            self.montant_remise = round(total_brut * self.remise_pct / Decimal('100'), 2)
        else:
            self.montant_remise = Decimal('0')

        total_ht       = total_brut - self.montant_remise
        self.total_ht  = total_ht

        self.tva_18pct    = round(total_ht * Decimal('0.18'), 2) if self.appliquer_tva     else Decimal('0')
        self.retenue_5pct = round(total_ht * Decimal('0.05'), 2) if self.appliquer_retenue else Decimal('0')
        self.bic_2pct     = round((total_ht + self.tva_18pct) * Decimal('0.02'), 2) if self.appliquer_bic else Decimal('0')

        transport = self.montant_transport if self.appliquer_transport else Decimal('0')

        self.total_net = round(
            total_ht + self.tva_18pct - self.retenue_5pct - self.bic_2pct + transport, 2
        )

        self.save(update_fields=[
            'total_ht_brut', 'montant_remise', 'total_ht',
            'tva_18pct', 'retenue_5pct', 'bic_2pct', 'total_net'
        ])

    def generer_numero(self):
        annee       = self.date_creation.strftime('%y') if self.date_creation else date.today().strftime('%y')
        client_id   = str(self.client.id).zfill(4)
        prefix      = 'P' if self.type_doc == 'PROFORMA' else 'F'
        prefix_full = f'ESVE{annee}-ID{client_id}-{prefix}-'

        derniers = Facture.objects.filter(
            numero__startswith=prefix_full
        ).exclude(
            numero__startswith='TEMP'
        ).order_by('-numero')

        if derniers.exists():
            dernier_numero = derniers.first().numero
            try:
                dernier_count = int(dernier_numero.split('-')[-1])
                count = dernier_count + 1
            except (ValueError, IndexError):
                count = derniers.count() + 1
        else:
            count = 1

        while True:
            nouveau_numero = f"{prefix_full}{str(count).zfill(4)}"
            if not Facture.objects.filter(numero=nouveau_numero).exists():
                break
            count += 1

        self.numero = nouveau_numero
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