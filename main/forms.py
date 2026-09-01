from django import forms
from .models import Temoignage, ContactMessage, Professeur, Cours, Presence, Examen, Paiement, DocumentPartage
from main.models import Classe
from accounts.models import Utilisateur


class TemoignageForm(forms.ModelForm):
    """Formulaire pour soumettre un témoignage."""
    class Meta:
        model = Temoignage
        fields = ['nom', 'role', 'texte']
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Votre prénom / nom',
                'id': 'comment-name',
            }),
            'role': forms.TextInput(attrs={
                'placeholder': 'Ex: Élève en 2ème Bac SM',
                'id': 'comment-role',
            }),
            'texte': forms.Textarea(attrs={
                'placeholder': 'Partagez votre expérience...',
                'rows': 3,
                'id': 'comment-text',
            }),
        }


class ContactForm(forms.ModelForm):
    """Formulaire de réservation / contact."""
    class Meta:
        model = ContactMessage
        fields = ['nom', 'niveau', 'format_cours', 'details']
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Nom Complet',
                'class': 'form-control',
            }),
            'niveau': forms.Select(
                choices=[
                    ('', 'Sélectionnez un niveau'),
                    ('Primaire (1AP - 6AP)', 'Primaire (1AP - 6AP)'),
                    ('Collège (1AC - 3AC)', 'Collège (1AC - 3AC)'),
                    ('Lycée - Tronc Commun', 'Lycée - Tronc Commun'),
                    ('Lycée - 1ère Bac (SM / SE)', 'Lycée - 1ère Bac (SM / SE)'),
                    ('Lycée - 2ème Bac (SM / SE)', 'Lycée - 2ème Bac (SM / SE)'),
                ],
                attrs={'class': 'form-control'}
            ),
            'format_cours': forms.RadioSelect(choices=[
                ('domicile', 'À domicile'),
                ('enseignant', "Chez l'enseignant"),
                ('en_ligne', 'En ligne'),
            ]),
            'details': forms.Textarea(attrs={
                'placeholder': 'Précisez le niveau actuel, les objectifs visés, la ville et vos disponibilités...',
                'rows': 4,
                'class': 'form-control',
            }),
        }


# ═══════════════════════════════════════════
# FORMULAIRES DASHBOARD ADMIN
# ═══════════════════════════════════════════

class EleveForm(forms.ModelForm):
    """Formulaire pour ajouter un élève."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
        label='Mot de passe'
    )

    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'username', 'email', 'niveau', 'classe', 'telephone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'username': forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email (optionnel)'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Téléphone (optionnel)'}),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'username': "Nom d'utilisateur",
            'email': 'Email',
            'niveau': 'Niveau scolaire (optionnel)',
            'classe': 'Classe',
            'telephone': 'Téléphone',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from main.models import Classe
        self.fields['classe'].queryset = Classe.objects.all()
        self.fields['classe'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'etudiant'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ProfesseurForm(forms.ModelForm):
    """Formulaire pour ajouter un professeur."""
    class Meta:
        model = Professeur
        fields = ['prenom', 'nom', 'matiere', 'telephone', 'email']
        widgets = {
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Téléphone'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }


class ClasseForm(forms.ModelForm):
    """Formulaire pour gérer les classes."""
    class Meta:
        from main.models import Classe
        model = Classe
        fields = ['nom', 'niveau']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Ex: 3ème Année - Informatique et Réseau (3-IIR)'}),
        }


class CoursForm(forms.ModelForm):
    """Formulaire pour ajouter un cours."""
    MATIERE_CHOICES = [
        ('Mathématiques', 'Mathématiques'),
        ('Physique-Chimie', 'Physique-Chimie'),
        ('SVT', 'SVT'),
        ('Français', 'Français'),
        ('Anglais', 'Anglais'),
        ('Arabe', 'Arabe'),
        ('Informatique', 'Informatique'),
        ('Éducation Islamique', 'Éducation Islamique'),
        ('Histoire-Géographie', 'Histoire-Géographie'),
        ('Philosophie', 'Philosophie'),
        ('Éducation Physique', 'Éducation Physique'),
    ]
    titre = forms.ChoiceField(choices=MATIERE_CHOICES, label='Matière')

    class Meta:
        model = Cours
        fields = ['titre', 'professeur', 'classe', 'jour', 'date_exacte', 'creneau', 'salle', 'couleur']
        widgets = {
            'salle': forms.TextInput(attrs={'placeholder': 'Ex: Salle 1'}),
            'couleur': forms.Select(),
            'date_exacte': forms.DateInput(attrs={'type': 'date'}),
        }


class PresenceForm(forms.ModelForm):
    """Formulaire pour marquer une présence."""
    class Meta:
        model = Presence
        fields = ['etudiant', 'cours', 'date', 'statut']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['etudiant'].queryset = Utilisateur.objects.filter(role='etudiant')


class ExamenForm(forms.ModelForm):
    """Formulaire pour planifier un examen."""
    class Meta:
        model = Examen
        fields = ['titre', 'matiere', 'classe', 'date', 'type_examen']
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Ex: Contrôle Maths'}),
            'matiere': forms.TextInput(attrs={'placeholder': 'Ex: Mathématiques'}),
            'classe': forms.TextInput(attrs={'placeholder': 'Ex: 2BAC SM'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class PaiementForm(forms.ModelForm):
    """Formulaire pour enregistrer un paiement."""
    class Meta:
        model = Paiement
        fields = ['etudiant', 'montant', 'type_paiement', 'statut', 'description']
        widgets = {
            'montant': forms.NumberInput(attrs={'placeholder': 'Montant en MAD', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description (optionnel)', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['etudiant'].queryset = Utilisateur.objects.filter(role='etudiant')


class DocumentCoursForm(forms.ModelForm):
    """Formulaire pour partager un document PDF de cours."""
    class Meta:
        model = DocumentPartage
        fields = ['titre', 'fichier', 'cours', 'classes_autorisees', 'etudiants_autorises', 'professeurs_autorises']
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Titre du document'}),
            'fichier': forms.FileInput(attrs={'accept': '.pdf'}),
            'classes_autorisees': forms.SelectMultiple(attrs={'class': 'multi-select'}),
            'etudiants_autorises': forms.SelectMultiple(attrs={'class': 'multi-select'}),
            'professeurs_autorises': forms.SelectMultiple(attrs={'class': 'multi-select'}),
        }
        labels = {
            'fichier': 'Fichier PDF',
            'cours': 'Lié au cours (optionnel)',
            'classes_autorisees': 'Partager avec classes (optionnel)',
            'etudiants_autorises': 'Partager avec étudiants (optionnel)',
            'professeurs_autorises': 'Partager avec professeurs (optionnel)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['etudiants_autorises'].queryset = Utilisateur.objects.filter(role='etudiant')


class DocumentExamenForm(forms.ModelForm):
    """Formulaire pour partager un document PDF d'examen."""
    class Meta:
        model = DocumentPartage
        fields = ['titre', 'fichier', 'examen', 'classes_autorisees', 'etudiants_autorises', 'professeurs_autorises']
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Titre du document'}),
            'fichier': forms.FileInput(attrs={'accept': '.pdf'}),
            'classes_autorisees': forms.SelectMultiple(attrs={'class': 'multi-select'}),
            'etudiants_autorises': forms.SelectMultiple(attrs={'class': 'multi-select'}),
            'professeurs_autorises': forms.SelectMultiple(attrs={'class': 'multi-select'}),
        }
        labels = {
            'fichier': 'Fichier PDF',
            'examen': 'Lié à l\'examen (optionnel)',
            'classes_autorisees': 'Partager avec classes (optionnel)',
            'etudiants_autorises': 'Partager avec étudiants (optionnel)',
            'professeurs_autorises': 'Partager avec professeurs (optionnel)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['etudiants_autorises'].queryset = Utilisateur.objects.filter(role='etudiant')
