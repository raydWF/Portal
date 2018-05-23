from django.shortcuts import render, redirect
from .models import *
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from .forms import *
from django.shortcuts import render_to_response
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.db.models import Count, Case, When, CharField
from django.views.generic.edit import ProcessFormView




# Create your views here.

@login_required
def index(request):
	"""
	View function for home page of site.
	"""
	
	# Render the HTML template index.html with the data in the context variable
	return render(
		request,
		'index.html',
	)
def construction(request):
 
    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'under_construction.html',
    )


def KeyAgreement(request):

    return render(
        request,
        'catalog/roomkey_agreement.html',
    )
# ===================================== KEYS ====================================================

class KeyListView(generic.ListView):
    model = RoomKey
    fields = '__all__'
    template_name = 'catalog/roomkey_list.html'

    def get_queryset(self):
        return RoomKey.objects.annotate(
            available_keys_count=Count(Case(
                When(keyinstance__status='a', then=1),
                output_field=CharField(),
            )))

class AllKeysStatus(generic.ListView):
    model = KeyInstance
    fields = '__all__'
    template_name = 'catalog/keyinstance_all.html'



    
class KeyDetailView(generic.DetailView):
    model = RoomKey

    """
	Shows the number of available keys. Accessable 
	through the available_key_count	variable
	"""
    def get_queryset(self):
        return RoomKey.objects.annotate(
            available_keys_count=Count(Case(
                When(keyinstance__status='a', then=1),
                output_field=CharField(),
            )))

# view for making a key request
class KeyRequestCreate(CreateView):
    model = KeyRequest
    fields = ['roomkey', 'requester', 'borrower', 'request_comments']
    template_name = 'catalog/roomkey_request_form.html'

class KeyAgreement111(CreateView):
    model = KeyRequest
    fields = ['roomkey', 'requester', 'borrower', 'request_comments']
    template_name = 'catalog/roomkey_agreement.html'

class LoanedKeysByUserListView(LoginRequiredMixin,generic.ListView):
    model = KeyInstance
    template_name = 'catalog/roomkey_list_borrowed_user.html'

    def get_queryset(self):
        return KeyInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedKeysAllListView(PermissionRequiredMixin,generic.ListView):
    
    model = KeyInstance
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/roomkey-all-borrowed.html'
        
    def get_queryset(self):
        return KeyInstance.objects.filter(status__exact='o').order_by('due_back')


class AllAvailableKeysView(PermissionRequiredMixin, generic.ListView):
    model = KeyInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/roomkey-all-available.html'

    def get_queryset(self):
        return KeyInstance.objects.filter(status__exact='a')


class KeyRequestListView(PermissionRequiredMixin, generic.ListView):
    model = KeyInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/roomkey_requests_all.html'

    def get_queryset(self):
        return  KeyInstance.objects.filter(status__exact='r')

class KeyRequestUpdate(UpdateView):
    model = KeyRequest
    inline_model = KeyInstance
    fields = ['request_status', 'request_comments']
    # initial = {'due_back': datetime.date.today()}
    template_name = 'catalog/roomkey_request_form.html'
    success_url = '/catalog/keys'


class KeyRequestDetailView(generic.DetailView):
    model = KeyInstance
    template_name = "catalog/roomkey_request_detail.html"



    def RequestDetail(request):
        num_keyinstances_available = KeyInstance.objects.filter(status__exact='a').count()

        return render(
            request,
            'key-request-detail',
            context = {'num_key_available':num_keyinstances_available},
        )


        
@permission_required('catalog.can_mark_returned')
def renew_key_user(request, pk):
    """
    View function for renewing a specific keyInstance by admin
    """
    key_inst=get_object_or_404(KeyInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewKeyForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            key_inst.due_back = form.cleaned_data['renewal_date']
            key_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed-keys') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewKeyForm(initial={'renewal_date': proposed_renewal_date})

    return render(request, 'catalog/roomkey_renew_user.html', {'form': form, 'keyinst':key_inst})


def submit_key_request(request, pk):
    """
    View function for renewing a specific keyInstance by admin
    """
    key_inst=get_object_or_404(KeyInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = UpdateKeyForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            key_inst.is_requested = True
            key_inst.status = 'r'
            key_inst.date_requested = datetime.date.today()
            key_inst.borrower = form.cleaned_data['borrower']
            key_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-available-keys') )

    # If this is a GET (or any other method) create the default form.
    else:

        form = UpdateKeyForm(initial={'borrower': 'N/A'})

    return render(request, 'catalog/keyinstance_request_update.html', {'form': form, 'keyinst':key_inst})


@permission_required('catalog.can_mark_returned')
def update_key_request(request, pk):
    """
    View function for renewing a specific keyInstance by admin
    """
    key_inst=get_object_or_404(KeyInstance, pk=pk)


    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = UpdateKeyRequestForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            request_status = form.cleaned_data['request_status']
            due_date = form.cleaned_data['due_date']
            if request_status == 'a':
                key_inst.due_back = due_date
                key_inst.status = 'o'
                key_inst.date_out = datetime.date.today()
                key_inst.save()
            else:
                key_inst.status = 'a'
                key_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-available-keys'))
    else:
        default_due_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = UpdateKeyRequestForm(initial={'due_date': default_due_date})

    #If this is a GET (or any other method) create the default form.

    return render(request, 'catalog/roomkey_request_update.html', {'form': form, 'keyinst': key_inst})


@permission_required('catalog.can_mark_returned')
def return_key_user(request,pk):
    key_inst = get_object_or_404(KeyInstance, pk=pk)

    if request.method == 'POST' :

        form = KeyMarkReturnForm(request.POST)

        if form.is_valid():
            key_inst.status = 'a'
            key_inst.date_returned = datetime.date.today()
            key_inst.save()

            return HttpResponseRedirect(reverse('all-borrowed-keys'))
    else:
        form = KeyMarkReturnForm(initial={'mark_returned':False})

    return render(request, 'catalog/roomkey_mark_return.html', {'form': form, 'keyinst':key_inst})







# =================================== MAINTENANCE REQUESTS=============================================================
# view for maintenance home page
class MaintenanceListView(generic.ListView):
    model = MaintenanceRequest
    template_name = 'catalog/maintenance-home.html'

# view for pending maintenance requests
class MaintenanceRequestListView(LoginRequiredMixin,generic.ListView):
    model = MaintenanceRequest
    template_name = 'catalog/maintenancerequest_list.html'

    def get_queryset(self):
        return MaintenanceRequest.objects.order_by('urgency', 'status')

# view for completed maintenance requests
class CompletedMaintenanceListView(LoginRequiredMixin,generic.ListView):
    login_url = '/login/'
    redirect_field_name = index
    model = MaintenanceRequest
    template_name = 'catalog/maintenance_list_completed.html'

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(status__exact='c').order_by('-date_completed')

# view for individual maintenance request details
class MaintenanceRequestDetailView(generic.DetailView):
    model = MaintenanceRequest

# view for creating maintenacne request
class MaintenanceRequestCreate(CreateView):
    model = MaintenanceRequest
    fields = ['requester', 'office', 'urgency', 'status', 'request_comments']

class MaintenanceRequestUpdate(UpdateView):
    model = MaintenanceRequest
    fields = ['status', 'date_completed', 'request_comments']
    initial = {'date_completed': datetime.date.today()}




# =========================================MOVE REQUESTS=========================================================
class MoveRequestListView(generic.ListView):
    model = MoveRequest
    template_name = 'catalog/move-home.html'


def move_request(request):

    MoveFormSet = formset_factory(MoveForm, formset=BaseMoveFormSet)

    if request.method == 'POST':
        move_formset = BaseMoveFormSet(request.POST)

