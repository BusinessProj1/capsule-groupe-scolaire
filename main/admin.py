from django.contrib import admin
from .models import Temoignage, ContactMessage, Professeur, Cours, Presence, Examen, Paiement, CreneauHoraire

@admin.register(CreneauHoraire)
class CreneauHoraireAdmin(admin.ModelAdmin):
    list_display = ('heure_debut', 'heure_fin', 'ordre')
    list_editable = ('ordre',)
    ordering = ('ordre', 'heure_debut')

@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'role', 'date_creation')
    list_filter = ('date_creation',)
    search_fields = ('nom', 'texte')
    readonly_fields = ('date_creation',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'niveau', 'format_cours', 'date_creation', 'lu')
    list_filter = ('format_cours', 'lu', 'date_creation')
    search_fields = ('nom', 'niveau', 'details')
    readonly_fields = ('date_creation',)
    list_editable = ('lu',)


@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'matiere', 'telephone', 'email')
    list_filter = ('matiere',)
    search_fields = ('nom', 'prenom', 'email')


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('titre', 'professeur', 'niveau', 'jour', 'heure_debut', 'heure_fin', 'salle')
    list_filter = ('jour', 'niveau')
    search_fields = ('titre', 'niveau')


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'cours', 'date', 'statut')
    list_filter = ('statut', 'date', 'cours')
    search_fields = ('etudiant__username', 'etudiant__first_name')


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('titre', 'matiere', 'classe', 'date', 'type_examen')
    list_filter = ('type_examen', 'date')
    search_fields = ('titre', 'matiere', 'classe')


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'montant', 'type_paiement', 'statut', 'date')
    list_filter = ('statut', 'type_paiement', 'date')
    search_fields = ('etudiant__username', 'etudiant__first_name')
    list_editable = ('statut',)
