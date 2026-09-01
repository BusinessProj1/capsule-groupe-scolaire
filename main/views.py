from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Temoignage
from .forms import TemoignageForm, ContactForm


def index_view(request):
    return render(request, 'main/index.html')


def methode_view(request):
    return render(request, 'main/methode.html')


def cours_view(request):
    return render(request, 'main/cours.html')


def tarifs_view(request):
    return render(request, 'main/tarifs.html')


def temoignages_view(request):
    """Vue des témoignages avec formulaire de soumission."""
    if request.method == 'POST':
        form = TemoignageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre témoignage a été ajouté avec succès !')
            return redirect('temoignages')
    else:
        form = TemoignageForm()

    temoignages = Temoignage.objects.all()
    return render(request, 'main/temoignages.html', {
        'form': form,
        'temoignages': temoignages,
    })


def ressources_view(request):
    return render(request, 'main/ressources.html')


def apropos_view(request):
    return render(request, 'main/apropos.html')


def contact_view(request):
    """Vue du formulaire de contact/réservation."""
    if request.method == 'POST':
        print(f"DEBUG: POST request received - {request.POST}")
        form = ContactForm(request.POST)
        print(f"DEBUG: Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG: Form errors: {form.errors}")
        if form.is_valid():
            saved = form.save()
            print(f"DEBUG: Message saved with ID: {saved.id}, lu={saved.lu}")
            messages.success(request, 'Votre demande de réservation a été enregistrée !')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'main/contact.html', {'form': form})


def lecon_type_view(request):
    return render(request, 'main/lecon_type.html')
