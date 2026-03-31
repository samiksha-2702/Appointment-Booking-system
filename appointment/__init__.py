from profile import Profile


def __init__(self, *args, **kwargs):
    user = kwargs.get('instance')
    super().__init__(*args, **kwargs)

    if user:
        profile, created = Profile.objects.get_or_create(user=user)

        self.fields['phone'].initial = profile.phone
        self.fields['image'].initial = profile.image