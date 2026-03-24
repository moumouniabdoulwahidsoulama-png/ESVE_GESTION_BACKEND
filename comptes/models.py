from django.db import models
from django.contrib.auth.models import User


class Profil(models.Model):
    ROLE_CHOICES = [
        ('ADMIN',   'Administrateur'),
        ('EMPLOYE', 'Employé'),
        ('CLIENT',  'Client'),
    ]
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYE')
    telephone  = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Profil'
        verbose_name_plural = 'Profils'

    def __str__(self):
        return f"{self.user.username} — {self.role}"


class DemandeApplication(models.Model):
    TYPE_CHOICES = [
    ('GESTION',   'Application de gestion'),
    ('ECOMMERCE', 'Site e-commerce'),
    ('VITRINE',   'Site vitrine'),
    ('MOBILE',    'Application mobile'),
    ('ERP',       'ERP / CRM'),
    ('AFFICHE',   'Affiche & Flyer'),
    ('LOGO',      'Logo & Identité visuelle'),
    ('PACK',      'Pack Digital Complet'),
    ('AUTRE',     'Autre'),
    ]
    BUDGET_CHOICES = [
        ('MOINS_500K',    'Moins de 500 000 FCFA'),
        ('500K_1M',       '500 000 — 1 000 000 FCFA'),
        ('1M_3M',         '1 000 000 — 3 000 000 FCFA'),
        ('PLUS_3M',       'Plus de 3 000 000 FCFA'),
        ('A_DISCUTER',    'À discuter'),
    ]
    STATUT_CHOICES = [
        ('NOUVEAU',       'Nouveau'),
        ('EN_COURS',      'En cours de traitement'),
        ('CONTACTE',      'Client contacté'),
        ('DEVIS_ENVOYE',  'Devis envoyé'),
        ('ACCEPTE',       'Accepté'),
        ('REFUSE',        'Refusé'),
    ]

    # Infos contact
    nom_entreprise  = models.CharField(max_length=200)
    nom_contact     = models.CharField(max_length=100)
    telephone       = models.CharField(max_length=20)
    email           = models.EmailField()
    pays            = models.CharField(max_length=100, default='Burkina Faso')
    ville           = models.CharField(max_length=100, blank=True)

    # Infos projet
    type_application = models.CharField(max_length=20, choices=TYPE_CHOICES, default='GESTION')
    budget           = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='A_DISCUTER')
    description      = models.TextField()
    fonctionnalites  = models.TextField(blank=True)
    delai_souhaite   = models.CharField(max_length=100, blank=True)

    # Gestion interne
    statut           = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU')
    notes_internes   = models.TextField(blank=True)
    date_demande     = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Demande Application'
        verbose_name_plural = 'Demandes Applications'
        ordering            = ['-date_demande']

    def __str__(self):
        return f"{self.nom_entreprise} — {self.type_application} — {self.statut}"