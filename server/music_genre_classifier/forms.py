from django import forms

class AudioFileForm(forms.Form):
    audio_file = forms.FileField()
