from django import forms

from .models import *
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.
from django.forms.formsets import BaseFormSet
    
class RenewKeyForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date (YYYY-MM-DD) between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        
        #Check date is not in past. 
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        #Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

class KeyInstanceForm(forms.ModelForm):
    class Meta:
        model = KeyInstance
        exclude = ('roomkey', 'id')

class KeyRequestForm(forms.ModelForm):
    class Meta:
        model = KeyRequest
        exclude = ('roomkey', 'requester', 'date_requested')

class MoveForm(forms.Form):
    move_person = forms.CharField(
                        max_length=40,
                        widget=forms.TextInput(attrs={
                            'placeholder': 'Person',
                            }),
                        required=True)
    move_to = forms.CharField(
                        max_length=100,
                        widget=forms.TextInput(attrs={
                            'placeholder': 'New Location'
                            }),
                        required=True)
    move_date = forms.DateField(
                        widget=forms.DateInput(),
                        required=True)
    move_conditions = forms.CharField(max_length=2000,
                        widget=forms.TextInput(attrs={
                            'placeholder': 'Enter any special requirements or reasons for move'
                            }),
                        required=False)
    # requested_by = forms.CharField(max_length=100)


class BaseMoveFormSet(BaseFormSet):

    def clean(self):
        if any(self.errors):
            return

        for form in self.forms:
            if form.cleaned_data:
                person = forms.cleaned_data['move_person']
                location = forms.cleaned_data['move_to']
                date = forms.cleaned_data['move_date']
