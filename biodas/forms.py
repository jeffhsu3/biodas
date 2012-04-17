from django import forms

class DASSourcesForm(forms.Form):
    capability = forms.CharField(max_length = 100, initiall = "",
                                 required = False)
    type = forms.CharField(max_length = 100, required = False)
    authority = forms.CharField(max_length = 100, required = False)
    version = forms.CharField(max_length = 100, required = False)
    organism = forms.CharField(max_length = 100, required = False)
    label = form.CharField(max_length = 100, required = False)

class TypeForm(forms.Form):
    segment = forms.Charfield(max_length = 100)
    type = forms.CharField(max_length = 100)
