from django import forms
from .models import Video


class VideoForm(forms.ModelForm):
    format_choices = (
        ('mp4', 'MP4'),
        ('mp3', 'MP3'),
    )

    format = forms.ChoiceField(choices=format_choices, initial='mp4', widget=forms.RadioSelect)

    download_path = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.HiddenInput()  # Hide the input field for the download path
    )

    class Meta:
        model = Video
        fields = ('url', 'format')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите URL видео с YouTube'
        })

    def clean_url(self):
        url = self.cleaned_data['url'].strip()
        return url
