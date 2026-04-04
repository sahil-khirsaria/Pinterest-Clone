from django import forms

from pinterest.models import Pin, Comment


class PinCreateModelForm(forms.ModelForm):
    class Meta:
        model = Pin
        fields = ('title', 'pin_file', 'about', 'alter_text', 'destination_link', 'category', 'is_private')

    def __init__(self, *args, **kwargs):
        super(PinCreateModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PinUpdateModelForm(forms.ModelForm):
    class Meta:
        model = Pin
        fields = ('title', 'pin_file', 'about', 'alter_text', 'destination_link', 'category', 'is_private')

    def __init__(self, *args, **kwargs):
        super(PinUpdateModelForm, self).__init__(*args, **kwargs)
        self.fields['pin_file'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add a comment...'
        })
