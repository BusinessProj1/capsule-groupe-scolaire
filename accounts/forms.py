from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    """Formulaire de connexion pour admin et étudiant."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': "Nom d'utilisateur",
            'class': 'form-input',
            'id': 'login-username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe',
            'class': 'form-input',
            'id': 'login-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Nom d'utilisateur ou mot de passe incorrect.")
            if not user.is_active:
                raise forms.ValidationError("Ce compte est désactivé.")
            cleaned_data['user'] = user

        return cleaned_data
