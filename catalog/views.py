from django.shortcuts import render, redirect
from .models import *
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404,get_list_or_404
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from .forms import *
from django.shortcuts import render_to_response
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.db.models import Count, Case, When, CharField
from django.views.generic.edit import ProcessFormView
from django.core.mail import send_mail
from django.template import loader
from django.views.generic.edit import FormView





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

# The views for a list of rooms

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


class LoanedKeysByUserListView(LoginRequiredMixin,generic.ListView):
    model = KeyInstance
    template_name = 'catalog/roomkey_list_borrowed_user.html'


    def get_queryset(self):
        name = self.request.user.first_name + ' ' + self.request.user.last_name
        return KeyInstance.objects.filter(borrower=name).filter(status__exact='o').order_by('due_back')

class LoanedKeysAllListView(PermissionRequiredMixin,generic.ListView):
    
    model = KeyInstance
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/roomkey-all-borrowed.html'
        
    def get_queryset(self):
        return KeyInstance.objects.filter(status__exact='o').order_by('due_back')


class AllAvailableKeysView(generic.ListView):
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

    key_inst = get_object_or_404(KeyInstance, pk=pk)
    names = get_list_or_404(User)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        name = request.POST['name']

        key_inst.is_requested = True
        key_inst.status = 'r'
        key_inst.date_requested = datetime.date.today()
        key_inst.borrower = name
        key_inst.borrower_email = request.user.email
        key_inst.save()

        return HttpResponseRedirect(reverse('all-available-keys') )


    # If this is a GET (or any other method) create the default form.
    else:
        pass


    return render(request,'catalog/keyinstance_request_update.html',{'keyinst':key_inst, 'names':names})


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
            key_notes = form.cleaned_data['notes']
            email_subject = 'Key Request Response'
            sender_email = 'service@walterfedy.com'
            receiver_email = key_inst.borrower_email

            if request_status == 'a':

                key_inst.due_back = due_date
                key_inst.status = 'o'
                key_inst.date_out = datetime.date.today()
                key_inst.request_status = 'a'
                key_inst.key_notes = key_notes
                key_inst.save()

                body_message = 'Greetings ' + key_inst.borrower + '.Your key request for ' + key_inst.roomkey.room_name + ' has been approved. Here are the keynotes: ' + key_notes
                html_message = loader.render_to_string(
                    'catalog/email_template.html',
                    {'body_message': body_message,
                     'user': key_inst.borrower},
                )
                send_mail(
                    email_subject,
                    body_message,
                    sender_email,
                    [receiver_email],
                    fail_silently=False,
                    html_message=html_message
                )

            else:
                key_inst.status = 'a'
                key_inst.request_status = 'd'
                key_inst.key_notes = key_notes
                key_inst.save()

                body_message = 'Greetings ' + key_inst.borrower + '.Unfortunately your key request for ' + key_inst.roomkey.room_name + ' has been denied. Here are the keynotes: ' + key_notes
                html_message = loader.render_to_string(
                    'catalog/email_template.html',
                    {'body_message' : body_message,
                     'user': key_inst.borrower},
                )


                send_mail(
                    email_subject,
                    body_message,
                    sender_email,
                    [receiver_email],
                    fail_silently=False,
                    html_message=html_message
                )



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
class MaintenanceRequestCreate(FormView):
    model = MaintenanceRequest
    template_name = 'catalog/maintenancerequest_form.html'
    form_class = MaintenanceForm
    names = get_list_or_404(User)

    def get_success_url(self):
        return reverse('maintenance-home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['names'] = self.names
        return context

    def form_valid(self, form):
        maintenance_request = MaintenanceRequest.objects.create()
        user_obj = get_object_or_404(User, username = self.request.POST['name'])
        maintenance_request.requester = user_obj
        maintenance_request.date_requested = datetime.date.today()
        maintenance_request.urgency = form.cleaned_data['urgency']
        maintenance_request.request_comments = form.cleaned_data['request_comments']
        maintenance_request.office = form.cleaned_data['office']
        maintenance_request.save()
        return super().form_valid(form)


class MaintenanceRequestUpdate(UpdateView):
    model = MaintenanceRequest
    fields = ['status', 'date_completed', 'request_comments']
    template_name = 'catalog/maintenancerequest_update.html'
    initial = {'date_completed': datetime.date.today()}




# =========================================MOVE REQUESTS=========================================================
class MoveRequestListView(generic.ListView):
    model = MoveRequest
    template_name = 'catalog/move-home.html'


def move_request(request):

    MoveFormSet = formset_factory(MoveForm, formset=BaseMoveFormSet)

    if request.method == 'POST':
        move_formset = BaseMoveFormSet(request.POST)

