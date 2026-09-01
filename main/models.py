from django.db import models
from django.conf import settings


class Temoignage(models.Model):
    """Témoignage / avis laissé par un élève ou parent."""
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default='Élève / Parent')
    texte = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Témoignage'
        verbose_name_plural = 'Témoignages'

    def __str__(self):
        return f"{self.nom} — {self.date_creation.strftime('%d/%m/%Y')}"

    @property
    def avatar(self):
        return self.nom[0].upper() if self.nom else '?'


class ContactMessage(models.Model):
    """Message de réservation / contact."""
    FORMAT_CHOICES = [
        ('domicile', 'À domicile'),
        ('enseignant', "Chez l'enseignant"),
        ('en_ligne', 'En ligne'),
    ]

    nom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=100)
    format_cours = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='domicile')
    details = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'

    def __str__(self):
        return f"{self.nom} — {self.niveau} ({self.date_creation.strftime('%d/%m/%Y')})"


class Professeur(models.Model):
    """Professeur / enseignant."""
    MATIERE_CHOICES = [
        ('mathematiques', 'Mathématiques'),
        ('physique_chimie', 'Physique-Chimie'),
        ('svt', 'SVT'),
        ('francais', 'Français'),
        ('anglais', 'Anglais'),
        ('arabe', 'Arabe'),
        ('informatique', 'Informatique'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    matiere = models.CharField(max_length=30, choices=MATIERE_CHOICES, default='mathematiques')
    is_active = models.BooleanField(default=True, help_text="Détermine si le professeur est actif dans l'établissement.")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nom', 'prenom']
        verbose_name = 'Professeur'
        verbose_name_plural = 'Professeurs'

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_matiere_display()})"

    @property
    def initiales(self):
        return f"{self.prenom[0]}{self.nom[0]}".upper() if self.prenom and self.nom else '?'


class Classe(models.Model):
    """Classe d'étudiants (ex: 3ème Année - Informatique et Réseau (3-IIR))."""
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

    nom = models.CharField(max_length=200, help_text="Ex: 3ème Année - Informatique et Réseau (3-IIR)")
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['niveau', 'nom']
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'

    def __str__(self):
        return self.nom


class CreneauHoraire(models.Model):
    """Créneau horaire personnalisable pour l'emploi du temps."""
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage dans l'emploi du temps")
    
    class Meta:
        ordering = ['ordre', 'heure_debut']
        verbose_name = 'Créneau horaire'
        verbose_name_plural = 'Créneaux horaires'
    
    def __str__(self):
        return f"{self.heure_debut.strftime('%H:%M')} - {self.heure_fin.strftime('%H:%M')}"
    
    @property
    def label(self):
        return f"{self.heure_debut.strftime('%H:%M')} - {self.heure_fin.strftime('%H:%M')}"
    
    @property
    def val(self):
        return f"{self.heure_debut.strftime('%H:%M')}-{self.heure_fin.strftime('%H:%M')}"


class Cours(models.Model):
    """Cours planifié."""
    JOUR_CHOICES = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]
    CRENEAU_CHOICES = [
        ('08:30-10:20', '08:30 - 10:20'),
        ('10:30-12:20', '10:30 - 12:20'),
        ('14:30-16:20', '14:30 - 16:20'),
        ('16:30-18:20', '16:30 - 18:20'),
    ]
    
    COULEUR_CHOICES = [
        ('#4a90e2', 'Bleu'),
        ('#50e3c2', 'Turquoise'),
        ('#b8e986', 'Vert clair'),
        ('#f5a623', 'Orange'),
        ('#e74c3c', 'Rouge'),
        ('#9b59b6', 'Violet'),
        ('#34495e', 'Bleu marine'),
        ('#1abc9c', 'Émeraude'),
    ]

    titre = models.CharField(max_length=200)
    professeur = models.ForeignKey(Professeur, on_delete=models.SET_NULL, null=True, blank=True, related_name='cours')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='cours', null=True)
    niveau = models.CharField(max_length=100, blank=True, null=True) # Conservé temporairement pour compatibilité
    jour = models.CharField(max_length=10, choices=JOUR_CHOICES, default='lundi')
    creneau = models.CharField(max_length=20, choices=CRENEAU_CHOICES, default='08:30-10:20')
    heure_debut = models.TimeField(null=True, blank=True) # Gardé pour rétrocompatibilité
    heure_fin = models.TimeField(null=True, blank=True)
    salle = models.CharField(max_length=50, blank=True, default='Salle 1')
    couleur = models.CharField(max_length=20, choices=COULEUR_CHOICES, default='#4a90e2')
    date_exacte = models.DateField(null=True, blank=True, verbose_name="Date exacte (Optionnel)")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['jour', 'heure_debut']
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'

    def __str__(self):
        heure = self.heure_debut.strftime('%H:%M') if self.heure_debut else '--:--'
        return f"{self.titre} — {self.get_jour_display()} {heure}"


class Presence(models.Model):
    """Présence d'un étudiant à un cours."""
    STATUT_CHOICES = [
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('retard', 'En retard'),
    ]

    etudiant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='presences')
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='present')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Présence'
        verbose_name_plural = 'Présences'
        unique_together = ['etudiant', 'cours', 'date']

    def __str__(self):
        return f"{self.etudiant} — {self.cours.titre} ({self.date.strftime('%d/%m/%Y')})"


class Examen(models.Model):
    """Examen planifié."""
    TYPE_CHOICES = [
        ('controle', 'Contrôle'),
        ('devoir', 'Devoir'),
        ('composition', 'Composition'),
        ('examen_regional', 'Examen Régional'),
        ('examen_national', 'Examen National'),
    ]

    titre = models.CharField(max_length=200)
    matiere = models.CharField(max_length=100)
    classe = models.CharField(max_length=100)
    date = models.DateField()
    type_examen = models.CharField(max_length=20, choices=TYPE_CHOICES, default='controle')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'Examen'
        verbose_name_plural = 'Examens'

    def __str__(self):
        return f"{self.titre} — {self.classe} ({self.date.strftime('%d/%m/%Y')})"


class Paiement(models.Model):
    """Paiement d'un étudiant."""
    TYPE_CHOICES = [
        ('scolarite', 'Frais de scolarité'),
        ('inscription', "Frais d'inscription"),
        ('examen', "Frais d'examen"),
        ('autre', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('en_attente', 'En attente'),
        ('annule', 'Annulé'),
    ]

    etudiant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_paiement = models.CharField(max_length=20, choices=TYPE_CHOICES, default='scolarite')
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

    def __str__(self):
        return f"{self.etudiant} — {self.montant} MAD ({self.get_statut_display()})"


class ChatMessage(models.Model):
    """Message de chat entre professeurs et étudiants."""
    expediteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_recus')
    contenu = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['date_envoi']
        verbose_name = 'Message de chat'
        verbose_name_plural = 'Messages de chat'

    def __str__(self):
        preview = self.contenu[:30] if self.contenu else '[Image]'
        return f"{self.expediteur} → {self.destinataire}: {preview}"


class DocumentPartage(models.Model):
    """Document PDF partagé pour les cours et examens."""
    TYPE_DOC_CHOICES = [
        ('cours', 'Cours'),
        ('examen', 'Examen'),
    ]

    titre = models.CharField(max_length=200)
    type_document = models.CharField(max_length=20, choices=TYPE_DOC_CHOICES, default='cours')
    fichier = models.FileField(upload_to='documents_pdf/')
    
    # Liens avec les entités existantes (optionnel)
    cours = models.ForeignKey('Cours', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    examen = models.ForeignKey('Examen', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    # Contrôle d'accès
    classes_autorisees = models.ManyToManyField('Classe', blank=True, related_name='documents_autorises')
    etudiants_autorises = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='documents_autorises')
    professeurs_autorises = models.ManyToManyField('Professeur', blank=True, related_name='documents_autorises')
    
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Document Partagé'
        verbose_name_plural = 'Documents Partagés'

    def __str__(self):
        return self.titre
