from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UpdateProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False)
    image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if user:
            self.fields['phone'].initial = user.profile.phone
            self.fields['image'].initial = user.profile.image

    def save(self, commit=True):
        user = super().save(commit)

        profile = user.profile
        profile.phone = self.cleaned_data.get('phone')
        
        if self.cleaned_data.get('image'):
            profile.image = self.cleaned_data.get('image')

        if commit:
            profile.save()

        return user