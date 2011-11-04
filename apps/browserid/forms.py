from django import forms

from django_browserid.forms import BrowserIDForm

class ModalBrowserIdForm(BrowserIDForm):
    mode = forms.CharField(widget=forms.HiddenInput)
