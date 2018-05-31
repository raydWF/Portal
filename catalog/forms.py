from django import forms
from django.forms import ModelForm
from .models import *
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.
from django.forms.formsets import BaseFormSet

#====================================================================== Key Forms ===================================================================
    
class RenewKeyForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date (YYYY-MM-DD) between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        
        #Check date is not in past. 
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        #Check date is in range admin allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data



class UpdateKeyRequestForm(forms.Form):

    APPROVE_CHOICES = [
        ('d', 'Deny this key request'),
        ('a', 'Approve this key request')

    ]

    request_status = forms.CharField(label='Please select to accept or deny this request.',widget=forms.Select(choices=APPROVE_CHOICES))

    due_date = forms.DateField(label='Due Date(If the request is approved)',
                               help_text='Enter a date (YYYY-MM-DD) between now and 4 weeks (default 3). ')

    notes = forms.CharField(label='Enter a brief note if you wish',widget=forms.Textarea)



    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']

         #Check date is not in past.
        if due_date < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        if due_date > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))


        return due_date


class KeyMarkReturnForm(forms.Form):

    mark_returned = forms.BooleanField()


    def validate_return(self):
        status = self.cleaned_data['mark_returned']

        if status != True:
            raise ValidationError(_('Please Check Box If You Would Like To Mark Returned. '))
        else:
            pass


class KeyInstanceForm(forms.ModelForm):
    class Meta:
        model = KeyInstance
        exclude = ('key_notes',)


class KeyRequestForm(forms.ModelForm):
    class Meta:
        model = KeyRequest
        exclude = ('roomkey', 'requester', 'date_requested')

class UpdateKeyForm(forms.Form):
    class Meta:
        model = KeyInstance

    borrower = forms.CharField(max_length=100,help_text="Enter the name of the borrower.")




    def clean_renewal_date(self):


        data = self.cleaned_data['borrower']

        # Check date is not in past.
        if data:
            return data

#====================================================================== Move Forms ===================================================================
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

