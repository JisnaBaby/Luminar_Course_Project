from django import forms
from .models import QuizParticipant,UserProfile

class QuizRegistrationForm(forms.ModelForm):
    class Meta:
        model = QuizParticipant
        fields = ['name', 'email', 'mobile']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'place', 'gender']
