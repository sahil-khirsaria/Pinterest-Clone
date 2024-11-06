from django import forms

from pinterest.models import Pin, PinComment


class PinCreateModelForm(forms.ModelForm):
    class Meta:
        model = Pin
        fields = ('title', 'pin_file', 'about', 'alter_text', 'destination_link', 'category', 'is_private')

    def __init__(self, *args, **kwargs):
        super(PinCreateModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PinCommentModelForm(forms.ModelForm):
    class Meta:
        model = PinComment
        fields = ('pin', 'comment', 'parent_comment')

    def __init__(self, *args, **kwargs):
        super(PinCommentModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
