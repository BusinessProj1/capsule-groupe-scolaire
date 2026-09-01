from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from datetime import date
from django.utils import timezone
from django.utils.timesince import timesince

from .models import Utilisateur
from main.models import (
    Temoignage, ContactMessage, Professeur, Cours,
    Presence, Examen, Paiement, CreneauHoraire,
)
from main.forms import (
    EleveForm, ProfesseurForm, CoursForm, PresenceForm,
    ExamenForm, PaiementForm, DocumentCoursForm, DocumentExamenForm,
)
from main.models import DocumentPartage


def login_view(request):
    """Page de connexion unifiée."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Nom d'utilisateur ou mot de passe incorrect."
    from .forms import LoginForm
    form = LoginForm()
    if error:
        form.add_error(None, error)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Déconnexion."""
    logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    """Redirige vers le bon dashboard selon le rôle."""
    if request.user.is_admin_user or request.user.is_superuser:
        return redirect('dashboard_admin')
    return redirect('dashboard_etudiant')


# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════

def _check_admin(request):
    if not (request.user.is_admin_user or request.user.is_superuser):
        return redirect('dashboard_etudiant')
    return None


def _get_notifications():
    """Génère les notifications à partir des données récentes."""
    notifs = []
    from datetime import timedelta

    # Derniers messages reçus
    recent_msgs = ContactMessage.objects.filter(lu=False).order_by('-date_creation')[:3]
    for msg in recent_msgs:
        msg_date = msg.date_creation if msg.date_creation else timezone.now()
        if msg_date.tzinfo is None:
            from django.utils.timezone import make_aware
            msg_date = make_aware(msg_date)
        notifs.append({
            'text': f'Nouveau message de {msg.nom}',
            'time': timesince(msg_date, timezone.now()) + ' ago' if msg_date else '',
            'bg': 'rgba(0,122,255,0.08)', 'color': '#007AFF',
            'icon': '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
            'type': 'message',
            'id': msg.id,
        })

    # Nouveaux élèves (dernières 24h)
    recent_students = Utilisateur.objects.filter(role='etudiant', date_joined__gte=timezone.now() - timedelta(hours=24)).order_by('-date_joined')[:3]
    for student in recent_students:
        student_date = student.date_joined if student.date_joined else timezone.now()
        if student_date.tzinfo is None:
            from django.utils.timezone import make_aware
            student_date = make_aware(student_date)
        notifs.append({
            'text': f'Nouvel élève: {student.get_full_name or student.username}',
            'time': timesince(student_date, timezone.now()) + ' ago' if student_date else '',
            'bg': 'rgba(52,199,89,0.08)', 'color': '#34C759',
            'icon': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>',
        })

    # Nouveaux professeurs (dernières 24h)
    recent_profs = Professeur.objects.filter(date_creation__gte=timezone.now() - timedelta(hours=24)).order_by('-date_creation')[:2]
    for prof in recent_profs:
        prof_date = prof.date_creation if prof.date_creation else timezone.now()
        if prof_date.tzinfo is None:
            from django.utils.timezone import make_aware
            prof_date = make_aware(prof_date)
        notifs.append({
            'text': f'Nouveau professeur: {prof.prenom} {prof.nom}',
            'time': timesince(prof_date, timezone.now()) + ' ago' if prof_date else '',
            'bg': 'rgba(0,122,255,0.08)', 'color': '#007AFF',
            'icon': '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        })

    # Nouveaux cours (dernières 24h)
    recent_cours = Cours.objects.filter(date_creation__gte=timezone.now() - timedelta(hours=24)).order_by('-date_creation')[:2]
    for cours in recent_cours:
        cours_date = cours.date_creation if cours.date_creation else timezone.now()
        if cours_date.tzinfo is None:
            from django.utils.timezone import make_aware
            cours_date = make_aware(cours_date)
        notifs.append({
            'text': f'Nouveau cours: {cours.titre}',
            'time': timesince(cours_date, timezone.now()) + ' ago' if cours_date else '',
            'bg': 'rgba(212,175,55,0.08)', 'color': '#D4AF37',
            'icon': '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
        })

    # Nouveaux examens planifiés (dernières 24h)
    recent_examens = Examen.objects.filter(date_creation__gte=timezone.now() - timedelta(hours=24)).order_by('-date_creation')[:2]
    for examen in recent_examens:
        examen_date = examen.date_creation if examen.date_creation else timezone.now()
        if examen_date.tzinfo is None:
            from django.utils.timezone import make_aware
            examen_date = make_aware(examen_date)
        notifs.append({
            'text': f'Nouvel examen: {examen.titre}',
            'time': timesince(examen_date, timezone.now()) + ' ago' if examen_date else '',
            'bg': 'rgba(212,175,55,0.08)', 'color': '#D4AF37',
            'icon': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
        })

    # Nouveaux paiements (dernières 24h)
    recent_paiements = Paiement.objects.filter(date__gte=timezone.now() - timedelta(hours=24)).order_by('-date')[:2]
    for paiement in recent_paiements:
        paiement_date = paiement.date if paiement.date else timezone.now()
        if type(paiement_date) is date:
            from datetime import datetime
            paiement_date = datetime.combine(paiement_date, datetime.min.time())
        if getattr(paiement_date, 'tzinfo', None) is None:
            from django.utils.timezone import make_aware
            paiement_date = make_aware(paiement_date)
        notifs.append({
            'text': f'Nouveau paiement: {paiement.montant} MAD',
            'time': timesince(paiement_date, timezone.now()) + ' ago' if paiement_date else '',
            'bg': 'rgba(52,199,89,0.08)', 'color': '#34C759',
            'icon': '<path d="M12 1v22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
        })

    # Examens à venir (dans les 7 prochains jours)
    upcoming = Examen.objects.filter(date__gte=date.today(), date__lte=date.today() + timedelta(days=7))
    for ex in upcoming[:2]:
        notifs.append({
            'text': f'Examen: {ex.titre} le {ex.date.strftime("%d/%m")}',
            'time': f'Dans {(ex.date - date.today()).days} jour(s)',
            'bg': 'rgba(212,175,55,0.08)', 'color': '#D4AF37',
            'icon': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
        })

    return notifs


def _base_context(active_page):
    """Contexte partagé pour toutes les pages dashboard."""
    notifs = _get_notifications()
    return {
        'active_page': active_page,
        'notifications': notifs,
        'notifications_count': len(notifs),
    }


# ═══════════════════════════════════════════
# DASHBOARD ADMIN
# ═══════════════════════════════════════════

@login_required
def dashboard_admin_view(request):
    """Tableau de bord administrateur."""
    if not (request.user.is_admin_user or request.user.is_superuser):
        return redirect('dashboard_etudiant')

    etudiants = Utilisateur.objects.filter(role='etudiant')
    temoignages = Temoignage.objects.all()[:10]
    messages_list = ContactMessage.objects.all()[:10]
    messages_non_lus = ContactMessage.objects.filter(lu=False).count()

    niveaux_primaire = ['1AP', '2AP', '3AP', '4AP', '5AP', '6AP']
    niveaux_college = ['1AC', '2AC', '3AC']
    etudiants_primaire = etudiants.filter(niveau__in=niveaux_primaire).count()
    etudiants_college = etudiants.filter(niveau__in=niveaux_college).count()
    etudiants_lycee = etudiants.exclude(
        Q(niveau__in=niveaux_primaire) | Q(niveau__in=niveaux_college) | Q(niveau__isnull=True) | Q(niveau='')
    ).count()

    context = {
        **_base_context('dashboard'),
        'etudiants': etudiants,
        'temoignages': temoignages,
        'messages': messages_list,
        'messages_non_lus': messages_non_lus,
        'total_etudiants': etudiants.count(),
        'total_temoignages': Temoignage.objects.count(),
        'total_messages': ContactMessage.objects.count(),
        'etudiants_primaire': etudiants_primaire,
        'etudiants_college': etudiants_college,
        'etudiants_lycee': etudiants_lycee,
    }
    return render(request, 'accounts/dashboard_admin.html', context)


# ═══════════════════════════════════════════
# PAGES SIDEBAR
# ═══════════════════════════════════════════

@login_required
def dashboard_eleves_view(request):
    redir = _check_admin(request)
    if redir: return redir

    form = EleveForm()
    show_modal = False
    success_message = None

    if request.method == 'POST':
        form = EleveForm(request.POST)
        if form.is_valid():
            etudiant = form.save()
            
            # Auto-créer un paiement en attente
            Paiement.objects.create(
                etudiant=etudiant,
                montant=0,
                type_paiement='inscription',
                statut='en_attente',
                description='Frais d\'inscription — à définir'
            )
            
            success_message = 'Élève ajouté avec succès !'
            form = EleveForm()
        else:
            show_modal = True

    etudiants = Utilisateur.objects.filter(role='etudiant')
    niveaux_primaire = ['1AP', '2AP', '3AP', '4AP', '5AP', '6AP']
    niveaux_college = ['1AC', '2AC', '3AC']

    context = {
        **_base_context('eleves'),
        'form': form, 'show_modal': show_modal, 'success_message': success_message,
        'eleves': etudiants,
        'total': etudiants.count(),
        'primaire': etudiants.filter(niveau__in=niveaux_primaire).count(),
        'college': etudiants.filter(niveau__in=niveaux_college).count(),
        'lycee': etudiants.exclude(
            Q(niveau__in=niveaux_primaire) | Q(niveau__in=niveaux_college) | Q(niveau__isnull=True) | Q(niveau='')
        ).count(),
    }
    return render(request, 'accounts/pages/eleves.html', context)


@login_required
def dashboard_classes_view(request):
    redir = _check_admin(request)
    if redir: return redir

    from main.models import Classe
    from main.forms import ClasseForm

    form = ClasseForm()
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            classe_id = request.POST.get('delete_id')
            Classe.objects.filter(id=classe_id).delete()
            return redirect('dashboard_classes')
        else:
            form = ClasseForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('dashboard_classes')

    classes = Classe.objects.all()
    niveaux_primaire = ['1AP', '2AP', '3AP', '4AP', '5AP', '6AP']
    niveaux_college = ['1AC', '2AC', '3AC']

    context = {
        **_base_context('classes'),
        'classes': classes,
        'form': form,
        'show_modal': bool(form.errors),
        'total': classes.count(),
        'primaire': classes.filter(niveau__in=niveaux_primaire).count(),
        'college': classes.filter(niveau__in=niveaux_college).count(),
        'lycee': classes.exclude(
            Q(niveau__in=niveaux_primaire) | Q(niveau__in=niveaux_college) | Q(niveau__isnull=True) | Q(niveau='')
        ).count(),
    }
    return render(request, 'accounts/pages/classes.html', context)


@login_required
def edit_classe_view(request, classe_id):
    """Modifier une classe."""
    redir = _check_admin(request)
    if redir: return redir

    from main.models import Classe
    from main.forms import ClasseForm

    classe = get_object_or_404(Classe, id=classe_id)
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            return redirect('dashboard_classes')
    else:
        form = ClasseForm(instance=classe)

    context = {
        **_base_context('classes'),
        'form': form,
        'classe': classe,
    }
    return render(request, 'accounts/pages/edit_classe.html', context)


@login_required
def emploi_temps_view(request):
    """Emploi du temps."""
    from main.models import Cours, Classe
    from main.forms import CoursForm

    # Check role
    is_admin = request.user.is_admin_user or request.user.is_superuser
    
    classes = Classe.objects.all()
    selected_classe = None
    form = CoursForm()

    if is_admin:
        classe_id = request.GET.get('classe')
        if classe_id:
            selected_classe = Classe.objects.filter(id=classe_id).first()
        elif classes.exists():
            selected_classe = classes.first()
    else:
        # Pour l'étudiant
        selected_classe = request.user.classe

    if request.method == 'POST' and is_admin:
        delete_id = request.POST.get('delete_cours_id')
        edit_id = request.POST.get('edit_cours_id')
        if delete_id:
            try:
                Cours.objects.get(id=delete_id).delete()
                return redirect(f"{request.path}?classe={request.POST.get('classe')}")
            except Cours.DoesNotExist:
                pass
        elif edit_id:
            try:
                cours_obj = Cours.objects.get(id=edit_id)
                cours_obj.titre = request.POST.get('titre', cours_obj.titre)
                prof_id = request.POST.get('professeur')
                if prof_id:
                    cours_obj.professeur = Professeur.objects.filter(id=prof_id).first()
                else:
                    cours_obj.professeur = None
                cours_obj.salle = request.POST.get('salle', cours_obj.salle)
                cours_obj.couleur = request.POST.get('couleur', cours_obj.couleur)
                cours_obj.save()
                return redirect(f"{request.path}?classe={request.POST.get('classe')}")
            except Cours.DoesNotExist:
                pass
        else:
            form = CoursForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect(f"{request.path}?classe={request.POST.get('classe')}")
    cours = Cours.objects.filter(classe=selected_classe) if selected_classe else []
    
    # Organiser les cours par jour et créneau pour la vue
    creneaux = CreneauHoraire.objects.all()
    if not creneaux.exists():
        # Fallback if no creneaux in DB yet
        jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
        emploi = []
    else:
        jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
        emploi = []
        for creneau in creneaux:
            row = {'val': creneau.val, 'label': creneau.label, 'jours': []}
            for j in jours:
                # find courses for this slot and day
                cours_liste = [c for c in cours if c.creneau == creneau.val and c.jour == j]
                row['jours'].append({'nom': j, 'cours': cours_liste})
            emploi.append(row)

    # Préparer les matières et professeurs pour les modals
    professeurs = Professeur.objects.all()
    matieres = CoursForm.MATIERE_CHOICES
    couleurs = Cours.COULEUR_CHOICES

    context = {
        **_base_context('emploi_temps'),
        'emploi': emploi,
        'classes': classes,
        'selected_classe': selected_classe,
        'form': form,
        'is_admin': is_admin,
        'professeurs_list': professeurs,
        'matieres': matieres,
        'couleurs': couleurs,
    }
    template = 'accounts/pages/emploi_temps.html' if is_admin else 'accounts/pages/emploi_temps_etudiant.html'
    return render(request, template, context)


@login_required
def edit_etudiant_view(request, etudiant_id):
    """Vue pour modifier les informations d'un étudiant."""
    redir = _check_admin(request)
    if redir: return redir

    etudiant = get_object_or_404(Utilisateur, id=etudiant_id, role='etudiant')
    
    from main.models import Classe

    if request.method == 'POST':
        etudiant.first_name = request.POST.get('first_name', etudiant.first_name)
        etudiant.last_name = request.POST.get('last_name', etudiant.last_name)
        etudiant.email = request.POST.get('email', etudiant.email)
        etudiant.telephone = request.POST.get('telephone', etudiant.telephone)
        etudiant.niveau = request.POST.get('niveau', etudiant.niveau)
        
        classe_id = request.POST.get('classe')
        if classe_id:
            etudiant.classe = Classe.objects.filter(id=classe_id).first()
        else:
            etudiant.classe = None
        
        if request.FILES.get('photo'):
            etudiant.photo = request.FILES['photo']
        
        etudiant.save()
        return redirect('dashboard_eleves')
    
    classes_list = Classe.objects.all()
    context = {
        **_base_context('eleves'),
        'etudiant': etudiant,
        'classes_list': classes_list,
        'active_page': 'eleves',
    }
    return render(request, 'accounts/pages/edit_etudiant.html', context)


@login_required
def toggle_etudiant_active_view(request, etudiant_id):
    """Vue pour activer/désactiver un compte étudiant."""
    redir = _check_admin(request)
    if redir: return redir

    etudiant = get_object_or_404(Utilisateur, id=etudiant_id, role='etudiant')
    etudiant.is_active = not etudiant.is_active
    etudiant.save()
    
    return redirect('dashboard_eleves')


@login_required
def toggle_professeur_active_view(request, professeur_id):
    """Vue pour activer/désactiver un compte professeur."""
    redir = _check_admin(request)
    if redir: return redir

    prof = get_object_or_404(Professeur, id=professeur_id)
    prof.is_active = not prof.is_active
    prof.save()
    
    return redirect('dashboard_professeurs')


@login_required
def dashboard_professeurs_view(request):
    redir = _check_admin(request)
    if redir: return redir

    form = ProfesseurForm()
    show_modal = False
    success_message = None

    if request.method == 'POST':
        delete_id = request.POST.get('delete_id')
        if delete_id:
            try:
                Professeur.objects.get(id=delete_id).delete()
                success_message = 'Professeur supprimé avec succès !'
            except Professeur.DoesNotExist:
                pass
        else:
            form = ProfesseurForm(request.POST)
            if form.is_valid():
                form.save()
                success_message = 'Professeur ajouté avec succès !'
                form = ProfesseurForm()
            else:
                show_modal = True

    professeurs = Professeur.objects.all()
    niveaux_primaire = ['1AP', '2AP', '3AP', '4AP', '5AP', '6AP']
    niveaux_college = ['1AC', '2AC', '3AC']

    context = {
        **_base_context('professeurs'),
        'form': form, 'show_modal': show_modal, 'success_message': success_message,
        'professeurs': professeurs,
        'total': professeurs.count(),
        'primaire': Professeur.objects.filter(cours__classe__niveau__in=niveaux_primaire).distinct().count(),
        'college': Professeur.objects.filter(cours__classe__niveau__in=niveaux_college).distinct().count(),
        'lycee': Professeur.objects.exclude(
            Q(cours__classe__niveau__in=niveaux_primaire) | Q(cours__classe__niveau__in=niveaux_college) | Q(cours__classe__niveau__isnull=True) | Q(cours__classe__niveau='')
        ).filter(cours__isnull=False).distinct().count(),
    }
    return render(request, 'accounts/pages/professeurs.html', context)


@login_required
def edit_professeur_view(request, professeur_id):
    """Vue pour modifier un professeur."""
    redir = _check_admin(request)
    if redir: return redir

    professeur = get_object_or_404(Professeur, id=professeur_id)
    
    if request.method == 'POST':
        form = ProfesseurForm(request.POST, instance=professeur)
        if form.is_valid():
            form.save()
            return redirect('dashboard_professeurs')
    else:
        form = ProfesseurForm(instance=professeur)
        
    context = {
        **_base_context('professeurs'),
        'professeur': professeur,
        'form': form,
    }
    return render(request, 'accounts/pages/edit_professeur.html', context)


@login_required
def dashboard_cours_view(request):
    redir = _check_admin(request)
    if redir: return redir

    form = CoursForm()
    doc_form = DocumentCoursForm()
    show_modal = False
    show_doc_modal = False
    success_message = None

    if request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'upload_pdf':
            doc_form = DocumentCoursForm(request.POST, request.FILES)
            if doc_form.is_valid():
                doc = doc_form.save(commit=False)
                doc.type_document = 'cours'
                doc.save()
                doc_form.save_m2m()
                success_message = 'Document partagé avec succès !'
                doc_form = DocumentCoursForm()
            else:
                show_doc_modal = True
        else:
            form = CoursForm(request.POST)
            if form.is_valid():
                form.save()
                success_message = 'Cours ajouté avec succès !'
                form = CoursForm()
            else:
                show_modal = True

    cours_list = Cours.objects.select_related('professeur', 'classe').all()
    documents_list = DocumentPartage.objects.filter(type_document='cours')
    niveaux_primaire = ['1AP', '2AP', '3AP', '4AP', '5AP', '6AP']
    niveaux_college = ['1AC', '2AC', '3AC']

    context = {
        **_base_context('cours'),
        'form': form, 'doc_form': doc_form, 'show_modal': show_modal, 'show_doc_modal': show_doc_modal, 'success_message': success_message,
        'cours_list': cours_list,
        'documents_list': documents_list,
        'matieres': [m[0] for m in CoursForm.MATIERE_CHOICES],
        'total': cours_list.count(),
        'primaire': cours_list.filter(classe__niveau__in=niveaux_primaire).count(),
        'college': cours_list.filter(classe__niveau__in=niveaux_college).count(),
        'lycee': cours_list.exclude(
            Q(classe__niveau__in=niveaux_primaire) | Q(classe__niveau__in=niveaux_college) | Q(classe__niveau__isnull=True) | Q(classe__niveau='')
        ).count(),
    }
    return render(request, 'accounts/pages/cours.html', context)


@login_required
def edit_cours_view(request, cours_id):
    """Vue pour modifier un cours existant."""
    redir = _check_admin(request)
    if redir: return redir

    cours = get_object_or_404(Cours, id=cours_id)
    
    if request.method == 'POST':
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            form.save()
            return redirect('dashboard_cours')
    else:
        form = CoursForm(instance=cours)
        
    context = {
        **_base_context('cours'),
        'form': form,
        'cours': cours,
    }
    return render(request, 'accounts/pages/edit_cours.html', context)


@login_required
def delete_cours_view(request, cours_id):
    """Vue pour supprimer un cours."""
    redir = _check_admin(request)
    if redir: return redir

    cours = get_object_or_404(Cours, id=cours_id)
    cours.delete()
    return redirect('dashboard_cours')


@login_required
def dashboard_presences_view(request):
    redir = _check_admin(request)
    if redir: return redir

    from main.models import Classe
    from datetime import date

    # Récupérer les paramètres
    selected_cours_id = request.GET.get('cours')
    selected_date = request.GET.get('date', date.today().isoformat())
    
    # Récupérer tous les cours
    cours_list = Cours.objects.select_related('classe', 'professeur').all()
    
    selected_cours = None
    etudiants = []
    presences_existantes = {}
    
    if selected_cours_id:
        selected_cours = Cours.objects.filter(id=selected_cours_id).first()
        if selected_cours and selected_cours.classe:
            etudiants = Utilisateur.objects.filter(role='etudiant', classe=selected_cours.classe)
            # Récupérer les présences existantes pour ce cours et cette date
            presences = Presence.objects.filter(
                cours=selected_cours,
                date=selected_date
            ).select_related('etudiant')
            presences_existantes = {p.etudiant_id: p.statut for p in presences}
            # Créer une liste d'étudiants avec leur statut
            etudiants_avec_statut = []
            for etudiant in etudiants:
                etudiants_avec_statut.append({
                    'etudiant': etudiant,
                    'statut': presences_existantes.get(etudiant.id, 'present')
                })
        else:
            etudiants_avec_statut = []

    # Traitement du formulaire POST
    if request.method == 'POST':
        cours_id = request.POST.get('cours')
        date_p = request.POST.get('date')
        
        if cours_id and date_p:
            cours_obj = Cours.objects.filter(id=cours_id).first()
            if cours_obj and cours_obj.classe:
                etudiants_list = Utilisateur.objects.filter(role='etudiant', classe=cours_obj.classe)
                
                # Supprimer les anciennes présences pour ce cours et cette date
                Presence.objects.filter(cours=cours_obj, date=date_p).delete()
                
                # Créer les nouvelles présences
                for etudiant in etudiants_list:
                    statut = request.POST.get(f'presence_{etudiant.id}', 'present')
                    Presence.objects.create(
                        etudiant=etudiant,
                        cours=cours_obj,
                        date=date_p,
                        statut=statut
                    )
                
                return redirect(f'/dashboard/presences/?cours={cours_id}&date={date_p}')

    # Calculer les statistiques pour le cours sélectionné
    stats_total = 0
    stats_presents = 0
    stats_absents = 0
    stats_retards = 0
    
    if selected_cours and selected_cours.classe:
        stats_total = Utilisateur.objects.filter(role='etudiant', classe=selected_cours.classe).count()
        if selected_date:
            presences_du_jour = Presence.objects.filter(cours=selected_cours, date=selected_date)
            stats_presents = presences_du_jour.filter(statut='present').count()
            stats_absents = presences_du_jour.filter(statut='absent').count()
            stats_retards = presences_du_jour.filter(statut='retard').count()

    context = {
        **_base_context('presences'),
        'cours_list': cours_list,
        'selected_cours': selected_cours,
        'selected_date': selected_date,
        'etudiants_avec_statut': etudiants_avec_statut if selected_cours_id else [],
        'today': date.today().isoformat(),
        'stats_total': stats_total,
        'stats_presents': stats_presents,
        'stats_absents': stats_absents,
        'stats_retards': stats_retards,
    }
    return render(request, 'accounts/pages/presences.html', context)


@login_required
def dashboard_examens_view(request):
    redir = _check_admin(request)
    if redir: return redir

    form = ExamenForm()
    doc_form = DocumentExamenForm()
    show_modal = False
    show_doc_modal = False
    success_message = None

    if request.method == 'POST':
        if 'action' in request.POST and request.POST['action'] == 'upload_pdf':
            doc_form = DocumentExamenForm(request.POST, request.FILES)
            if doc_form.is_valid():
                doc = doc_form.save(commit=False)
                doc.type_document = 'examen'
                doc.save()
                doc_form.save_m2m()
                success_message = 'Document d\'examen partagé avec succès !'
                doc_form = DocumentExamenForm()
            else:
                show_doc_modal = True
        else:
            form = ExamenForm(request.POST)
            if form.is_valid():
                form.save()
                success_message = 'Examen planifié avec succès !'
                form = ExamenForm()
            else:
                show_modal = True

    examens = Examen.objects.all()
    documents_list = DocumentPartage.objects.filter(type_document='examen')
    today = date.today()
    context = {
        **_base_context('examens'),
        'form': form, 'doc_form': doc_form, 'show_modal': show_modal, 'show_doc_modal': show_doc_modal, 'success_message': success_message,
        'examens': examens,
        'documents_list': documents_list,
        'total': examens.count(),
        'a_venir': examens.filter(date__gte=today).count(),
        'passes': examens.filter(date__lt=today).count(),
    }
    return render(request, 'accounts/pages/examens.html', context)


@login_required
def dashboard_paiements_view(request):
    redir = _check_admin(request)
    if redir: return redir

    form = PaiementForm()
    show_modal = False
    success_message = None

    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            form.save()
            success_message = 'Paiement enregistré avec succès !'
            form = PaiementForm()
        else:
            show_modal = True

    paiements = Paiement.objects.select_related('etudiant').all()
    montant_total = paiements.filter(statut='paye').aggregate(total=Sum('montant'))['total'] or 0
    context = {
        **_base_context('paiements'),
        'form': form, 'show_modal': show_modal, 'success_message': success_message,
        'paiements': paiements,
        'total': paiements.count(),
        'payes': paiements.filter(statut='paye').count(),
        'en_attente': paiements.filter(statut='en_attente').count(),
        'montant_total': montant_total,
    }
    return render(request, 'accounts/pages/paiements.html', context)


@login_required
def dashboard_messages_view(request):
    redir = _check_admin(request)
    if redir: return redir

    messages_list = ContactMessage.objects.all()
    non_lus_count = messages_list.filter(lu=False).count()
    context = {
        **_base_context('messages'),
        'messages_list': messages_list,
        'total': messages_list.count(),
        'non_lus': non_lus_count,
        'lus': messages_list.filter(lu=True).count(),
        'non_lus_count': non_lus_count,
    }
    return render(request, 'accounts/pages/messages.html', context)


@login_required
def toggle_message_status(request, message_id):
    """Marquer un message comme lu/non lu."""
    redir = _check_admin(request)
    if redir: return redir

    try:
        message = ContactMessage.objects.get(id=message_id)
        message.lu = not message.lu
        message.save()
    except ContactMessage.DoesNotExist:
        from django.contrib import messages
        messages.warning(request, 'Ce message n\'existe plus.')
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('dashboard_messages')


@login_required
def message_detail_view(request, message_id):
    """Afficher les détails d'un message dans un modal."""
    redir = _check_admin(request)
    if redir: return redir

    try:
        message = ContactMessage.objects.get(id=message_id)
        if not message.lu:
            message.lu = True
            message.save()

        messages_list = ContactMessage.objects.all()
        non_lus_count = messages_list.filter(lu=False).count()
        context = {
            **_base_context('messages'),
            'messages_list': messages_list,
            'total': messages_list.count(),
            'non_lus': non_lus_count,
            'lus': messages_list.filter(lu=True).count(),
            'non_lus_count': non_lus_count,
            'message': message,
            'show_detail_modal': True,
        }
        return render(request, 'accounts/pages/messages.html', context)
    except ContactMessage.DoesNotExist:
        from django.contrib import messages
        messages.warning(request, 'Ce message n\'existe plus.')
        return redirect('dashboard_messages')


@login_required
def message_edit_view(request, message_id):
    """Modifier un message."""
    redir = _check_admin(request)
    if redir: return redir

    from main.forms import ContactForm
    try:
        message = ContactMessage.objects.get(id=message_id)
        messages_list = ContactMessage.objects.all()
        non_lus_count = messages_list.filter(lu=False).count()

        if request.method == 'POST':
            form = ContactForm(request.POST, instance=message)
            if form.is_valid():
                form.save()
                return redirect('dashboard_messages')
        else:
            form = ContactForm(instance=message)

        context = {
            **_base_context('messages'),
            'messages_list': messages_list,
            'total': messages_list.count(),
            'non_lus': non_lus_count,
            'lus': messages_list.filter(lu=True).count(),
            'non_lus_count': non_lus_count,
            'form': form,
            'message': message,
            'show_edit_modal': True,
        }
        return render(request, 'accounts/pages/messages.html', context)
    except ContactMessage.DoesNotExist:
        from django.contrib import messages
        messages.warning(request, 'Ce message n\'existe plus.')
        return redirect('dashboard_messages')


@login_required
def message_delete_view(request, message_id):
    """Supprimer un message."""
    redir = _check_admin(request)
    if redir: return redir

    try:
        message = ContactMessage.objects.get(id=message_id)
        message.delete()
    except ContactMessage.DoesNotExist:
        from django.contrib import messages
        messages.warning(request, 'Ce message n\'existe plus.')
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('dashboard_messages')


@login_required
def dashboard_rapports_view(request):
    redir = _check_admin(request)
    if redir: return redir

    etudiants = Utilisateur.objects.filter(role='etudiant')
    niveaux_primaire = ['1AP', '2AP', '3AP', '4AP', '5AP', '6AP']
    niveaux_college = ['1AC', '2AC', '3AC']

    paiements = Paiement.objects.all()
    revenus = paiements.filter(statut='paye').aggregate(total=Sum('montant'))['total'] or 0

    context = {
        **_base_context('rapports'),
        'total_eleves': etudiants.count(),
        'total_profs': Professeur.objects.count(),
        'total_cours': Cours.objects.count(),
        'revenus_total': revenus,
        # Répartition élèves
        'primaire': etudiants.filter(niveau__in=niveaux_primaire).count(),
        'college': etudiants.filter(niveau__in=niveaux_college).count(),
        'lycee': etudiants.exclude(
            Q(niveau__in=niveaux_primaire) | Q(niveau__in=niveaux_college) | Q(niveau__isnull=True) | Q(niveau='')
        ).count(),
        # Paiements
        'paiements_total': paiements.count(),
        'payes': paiements.filter(statut='paye').count(),
        'en_attente': paiements.filter(statut='en_attente').count(),
        'annules': paiements.filter(statut='annule').count(),
        # Paiements par type
        'scolarite_payes': paiements.filter(type_paiement='scolarite', statut='paye').count(),
        'scolarite_attente': paiements.filter(type_paiement='scolarite', statut='en_attente').count(),
        'scolarite_montant': paiements.filter(type_paiement='scolarite', statut='paye').aggregate(t=Sum('montant'))['t'] or 0,
        'inscription_payes': paiements.filter(type_paiement='inscription', statut='paye').count(),
        'inscription_attente': paiements.filter(type_paiement='inscription', statut='en_attente').count(),
        'inscription_montant': paiements.filter(type_paiement='inscription', statut='paye').aggregate(t=Sum('montant'))['t'] or 0,
        'examen_payes': paiements.filter(type_paiement='examen', statut='paye').count(),
        'examen_attente': paiements.filter(type_paiement='examen', statut='en_attente').count(),
        'examen_montant': paiements.filter(type_paiement='examen', statut='paye').aggregate(t=Sum('montant'))['t'] or 0,
        # Présences
        'presences_total': Presence.objects.count(),
        'presents': Presence.objects.filter(statut='present').count(),
        'absents': Presence.objects.filter(statut='absent').count(),
        'retards': Presence.objects.filter(statut='retard').count(),
        # Examens par type
        'examens_total': Examen.objects.count(),
        'type_controle': Examen.objects.filter(type_examen='controle').count(),
        'type_devoir': Examen.objects.filter(type_examen='devoir').count(),
        'type_composition': Examen.objects.filter(type_examen='composition').count(),
        'type_regional': Examen.objects.filter(type_examen='examen_regional').count(),
        'type_national': Examen.objects.filter(type_examen='examen_national').count(),
    }
    return render(request, 'accounts/pages/rapports.html', context)


# ═══════════════════════════════════════════
# DASHBOARD ÉTUDIANT
# ═══════════════════════════════════════════

@login_required
def dashboard_etudiant_view(request):
    """Vue du dashboard pour l'étudiant."""
    if request.user.role != 'etudiant':
        return redirect('dashboard')
    
    # Documents où l'étudiant est explicitement autorisé ou sa classe est autorisée
    from main.models import DocumentPartage
    from django.db.models import Q
    
    user = request.user
    mes_documents = DocumentPartage.objects.filter(
        Q(etudiants_autorises=user) | Q(classes_autorisees=user.classe)
    ).distinct().order_by('-date_creation')
    
    context = {
        'active_page': 'dashboard',
        'mes_documents': mes_documents,
    }
    return render(request, 'accounts/dashboard_etudiant.html', context)


@login_required
def etudiant_profile_view(request):
    """Vue du profil pour l'étudiant."""
    if request.user.role != 'etudiant':
        return redirect('dashboard')
    
    context = {
        'active_page': 'profile',
        'user': request.user,
    }
    return render(request, 'accounts/dashboard_etudiant.html', context)


@login_required
def etudiant_cours_view(request):
    """Vue des cours pour l'étudiant."""
    if request.user.role != 'etudiant':
        return redirect('dashboard')
    
    from main.models import Cours
    
    context = {
        'active_page': 'cours',
        'user': request.user,
        'cours': [],
    }
    return render(request, 'accounts/etudiant_cours.html', context)


@login_required
def etudiant_examens_view(request):
    """Vue des examens pour l'étudiant."""
    if request.user.role != 'etudiant':
        return redirect('dashboard')
    
    from main.models import Examen
    
    context = {
        'active_page': 'examens',
        'user': request.user,
        'examens': [],
    }
    return render(request, 'accounts/etudiant_examens.html', context)


@login_required
def etudiant_presence_view(request):
    """Vue de la présence pour l'étudiant."""
    if request.user.role != 'etudiant':
        return redirect('dashboard')
    
    from main.models import Presence
    
    presences = Presence.objects.filter(etudiant=request.user).select_related('cours').order_by('-date')
    
    total = presences.count()
    nb_present = presences.filter(statut='present').count()
    nb_absent = presences.filter(statut='absent').count()
    nb_retard = presences.filter(statut='retard').count()
    taux = round((nb_present / total) * 100) if total > 0 else 0
    
    context = {
        'active_page': 'presence',
        'user': request.user,
        'presences': presences,
        'nb_present': nb_present,
        'nb_absent': nb_absent,
        'nb_retard': nb_retard,
        'taux': taux,
    }
    return render(request, 'accounts/etudiant_presence.html', context)


@login_required
def chat_view(request):
    """Vue du chat pour l'admin (professeur)."""
    redir = _check_admin(request)
    if redir: return redir

    from main.models import ChatMessage

    # Montrer tous les étudiants pour l'admin
    etudiants = Utilisateur.objects.filter(role='etudiant')
    conversations = []
    
    try:
        for etudiant in etudiants:
            messages = ChatMessage.objects.filter(
                Q(expediteur=request.user, destinataire=etudiant) |
                Q(expediteur=etudiant, destinataire=request.user)
            ).order_by('date_envoi')
            
            conversations.append({
                'user': etudiant,
                'last_message': messages.last() if messages.exists() else None,
                'unread': messages.filter(destinataire=request.user, lu=False).count()
            })
    except Exception:
        # Si la table n'existe pas encore, retourner des conversations vides
        conversations = []

    context = {
        **_base_context('chat'),
        'conversations': conversations,
    }
    return render(request, 'accounts/pages/chat.html', context)


@login_required
def chat_etudiant_view(request):
    """Vue du chat pour l'étudiant."""
    if request.user.role != 'etudiant':
        return redirect('dashboard')

    from main.models import ChatMessage

    # Récupérer tous les admins / profs (les users avec le role admin ou superuser)
    admins = Utilisateur.objects.filter(
        Q(role='admin') | Q(is_superuser=True)
    )
    conversations = []
    
    try:
        for admin_user in admins:
            messages = ChatMessage.objects.filter(
                Q(expediteur=request.user, destinataire=admin_user) |
                Q(expediteur=admin_user, destinataire=request.user)
            ).order_by('date_envoi')
            
            conversations.append({
                'user': admin_user,
                'last_message': messages.last() if messages.exists() else None,
                'unread': messages.filter(destinataire=request.user, lu=False).count()
            })
    except Exception:
        # Si la table n'existe pas encore, retourner des conversations vides
        conversations = []

    context = {
        'active_page': 'chat',
        'conversations': conversations,
        'user': request.user,
    }
    return render(request, 'accounts/chat_etudiant.html', context)


@login_required
def chat_messages_view(request, user_id):
    """API pour récupérer les messages d'une conversation."""
    from main.models import ChatMessage

    try:
        other_user = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    messages = ChatMessage.objects.filter(
        expediteur=request.user, destinataire=other_user
    ) | ChatMessage.objects.filter(
        expediteur=other_user, destinataire=request.user
    ).order_by('date_envoi')

    # Marquer comme lus les messages reçus
    messages.filter(destinataire=request.user, lu=False).update(lu=True)

    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'expediteur': msg.expediteur.id,
            'destinataire': msg.destinataire.id,
            'contenu': msg.contenu,
            'image_url': msg.image.url if msg.image else None,
            'date_envoi': msg.date_envoi.strftime('%H:%M'),
            'lu': msg.lu,
            'is_mine': msg.expediteur == request.user,
        })

    return JsonResponse({'messages': messages_data})


@login_required
def chat_send_view(request):
    """API pour envoyer un message avec optionnellement une image."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    from main.models import ChatMessage
    import json

    try:
        # Support pour formData (si image) ou JSON
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
            destinataire_id = data.get('destinataire_id')
            contenu = data.get('contenu', '')
            image = None
        else:
            destinataire_id = request.POST.get('destinataire_id')
            contenu = request.POST.get('contenu', '')
            image = request.FILES.get('image')

        if not destinataire_id:
            return JsonResponse({'error': 'Destinataire manquant'}, status=400)

        if not contenu and not image:
            return JsonResponse({'error': 'Contenu ou image requis'}, status=400)

        destinataire = Utilisateur.objects.get(id=destinataire_id)
        message = ChatMessage.objects.create(
            expediteur=request.user,
            destinataire=destinataire,
            contenu=contenu,
            image=image
        )

        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'expediteur': message.expediteur.id,
                'destinataire': message.destinataire.id,
                'contenu': message.contenu,
                'image_url': message.image.url if message.image else None,
                'date_envoi': message.date_envoi.strftime('%H:%M'),
                'lu': message.lu,
                'is_mine': True,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def update_paiement_statut_view(request, paiement_id):
    """Mettre à jour rapidement le statut d'un paiement."""
    redir = _check_admin(request)
    if redir: return redir

    if request.method == 'POST':
        statut = request.POST.get('statut')
        if statut in dict(Paiement.STATUT_CHOICES):
            paiement = get_object_or_404(Paiement, id=paiement_id)
            paiement.statut = statut
            paiement.save()
    return redirect('dashboard_paiements')

@login_required
def delete_paiement_view(request, paiement_id):
    """Supprimer un paiement."""
    redir = _check_admin(request)
    if redir: return redir

    if request.method == 'POST':
        paiement = get_object_or_404(Paiement, id=paiement_id)
        paiement.delete()
    return redirect('dashboard_paiements')
