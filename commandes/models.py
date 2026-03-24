from django.db import models
from decimal import Decimal
from datetime import date


class BonCommande(models.Model):

    STATUT_CHOICES = [
        ('BROUILLON',  'Brouillon'),
        ('ENVOYE',     'Envoyé au fournisseur'),
        ('RECU',       'Reçu partiellement'),
        ('RECU_TOTAL', 'Reçu en totalité'),
        ('ANNULE',     'Annulé'),
    ]

    # Identification
    numero                       = models.CharField(max_length=50, unique=True, blank=True)
    statut                       = models.CharField(max_length=15, choices=STATUT_CHOICES, default='BROUILLON')

    # Fournisseur
    fournisseur_nom              = models.CharField(max_length=200)
    fournisseur_contact          = models.CharField(max_length=100, blank=True)
    fournisseur_tel              = models.CharField(max_length=20,  blank=True)
    fournisseur_email            = models.EmailField(blank=True)
    fournisseur_adresse          = models.TextField(blank=True)
    fournisseur_ifu              = models.CharField(max_length=50,  blank=True)
    fournisseur_rccm             = models.CharField(max_length=100, blank=True)
    fournisseur_division_fiscale = models.CharField(max_length=100, blank=True)
    fournisseur_regime           = models.CharField(max_length=100, blank=True)

    # Référence proforma fournisseur
    ref_proforma_fournisseur     = models.CharField(max_length=100, blank=True)
    date_proforma_fournisseur    = models.DateField(null=True, blank=True)

    # Termes
    termes_paiement              = models.CharField(max_length=200, blank=True)
    termes_livraison             = models.CharField(max_length=200, blank=True)
    delais_livraison             = models.CharField(max_length=100, blank=True)

    # Dates
    date_commande                = models.DateField(auto_now_add=True)
    date_modification            = models.DateTimeField(auto_now=True)
    date_livraison_prev          = models.DateField(null=True, blank=True)

    # Options de calcul
    appliquer_tva                = models.BooleanField(default=False)
    appliquer_retenue            = models.BooleanField(default=False)
    appliquer_bic                = models.BooleanField(default=False)

    # Montants
    total_ht                     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tva_18pct                    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    retenue_5pct                 = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    bic_2pct                     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net                    = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # PDF et infos
    pdf_file                     = models.FileField(upload_to='pdfs/commandes/', null=True, blank=True)
    notes                        = models.TextField(blank=True)
    objet                        = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name        = 'Bon de Commande'
        verbose_name_plural = 'Bons de Commande'
        ordering            = ['-date_commande']

    def __str__(self):
        return f"{self.numero} — {self.fournisseur_nom}"

    def calculer_totaux(self):
        total             = sum(ligne.total_ht for ligne in self.lignes.all())
        self.total_ht     = total
        self.tva_18pct    = round(total * Decimal('0.18'), 2) if self.appliquer_tva     else Decimal('0')
        self.retenue_5pct = round(total * Decimal('0.05'), 2) if self.appliquer_retenue else Decimal('0')
        self.bic_2pct = round((total + self.tva_18pct) * Decimal('0.02'), 2) if self.appliquer_bic else Decimal('0')
        self.total_net    = round(total + self.tva_18pct - self.retenue_5pct - self.bic_2pct, 2)
        self.save(update_fields=['total_ht', 'tva_18pct', 'retenue_5pct', 'bic_2pct', 'total_net'])

    def generer_numero(self):
        annee        = date.today().strftime('%y')
        prefix_full  = f'ESVE{annee}-BC-'

        # Trouver le dernier numéro valide
        derniers = BonCommande.objects.filter(
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

        # S'assurer que le numéro est unique
        while True:
            nouveau_numero = f"{prefix_full}{str(count).zfill(4)}"
            if not BonCommande.objects.filter(numero=nouveau_numero).exists():
                break
            count += 1

        self.numero = nouveau_numero
        self.save(update_fields=['numero'])


class LigneBonCommande(models.Model):

    bon_commande            = models.ForeignKey(BonCommande, on_delete=models.CASCADE, related_name='lignes')
    description             = models.CharField(max_length=300)
    reference_client        = models.CharField(max_length=100, blank=True)
    reference_fournisseur   = models.CharField(max_length=100, blank=True)
    prix_unitaire_ht        = models.DecimalField(max_digits=14, decimal_places=2)
    quantite                = models.DecimalField(max_digits=10, decimal_places=2)
    total_ht                = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unite                   = models.CharField(max_length=50,  blank=True)
    delais                  = models.CharField(max_length=100, blank=True)
    ordre                   = models.IntegerField(default=0)

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