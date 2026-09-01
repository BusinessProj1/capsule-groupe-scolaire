from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """Modèle utilisateur personnalisé avec rôle admin/étudiant."""

    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('etudiant', 'Étudiant'),
    ]

    NIVEAU_CHOICES = [
        ('1AP', '1ère Année Primaire'),
        ('2AP', '2ème Année Primaire'),
        ('3AP', '3ème Année Primaire'),
        ('4AP', '4ème Année Primaire'),
        ('5AP', '5ème Année Primaire'),
        ('6AP', '6ème Année Primaire'),
        ('1AC', '1ère Année Collège'),
        ('2AC', '2ème Année Collège'),
        ('3AC', '3ème Année Collège'),
        ('TCS', 'Tronc Commun Sciences'),
        ('1BAC_SE', '1ère Bac Sciences Expérimentales'),
        ('1BAC_SM', '1ère Bac Sciences Mathématiques'),
        ('2BAC_SE', '2ème Bac Sciences Expérimentales'),
        ('2BAC_SM', '2ème Bac Sciences Mathématiques'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='etudiant')
    niveau = models.CharField(max_length=10, choices=NIVEAU_CHOICES, blank=True, null=True)
    classe = models.ForeignKey('main.Classe', on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    # photo = models.ImageField(upload_to='photos_etudiants/', blank=True, null=True)  # Temporarily disabled - run: sqlite3 db.sqlite3 "ALTER TABLE accounts_utilisateur ADD COLUMN photo VARCHAR(200);"

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    @property
    def is_etudiant(self):
        return self.role == 'etudiant'
