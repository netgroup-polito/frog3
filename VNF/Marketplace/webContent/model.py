from django import forms

class UploadForm(forms.Form):
    
    CHOICES = (('0', 'Inactive'), ('1', 'Active'))
    
    appname = forms.CharField(label='App name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    status = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
    manifest_id = forms.CharField(label='Manifest ID', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    storage_id = forms.CharField(label='Storage ID', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    plugin_id = forms.CharField(label='Plugin ID', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    disk_format = forms.CharField(label='Disk format', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    container_format = forms.CharField(label='Container format', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    file_image = forms.FileField(required=True)