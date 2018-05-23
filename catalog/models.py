from django.db import models
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User
from datetime import date
from datetime import timedelta
import uuid # Required for unique book instances
from django.utils.deconstruct import deconstructible
# Create your models here.
@deconstructible
class RoomKey(models.Model):
    """
    Model representing rooms
    """
    room_name = models.CharField(max_length=100, help_text="Enter the name of the key.", verbose_name="Door #")
    room_des = models.CharField(max_length=200, help_text="Give a brief description of the key", verbose_name="Room description")
    key_symb = models.CharField(max_length=10, help_text="Enter the keyset symbol", verbose_name="Keyset Symbol", null=True, blank=True)
    bitting_num = models.PositiveIntegerField(help_text="Enter the bitting number (max length 10)", verbose_name="Bitting #", null=True, blank=True)

    OFFICE_LOCATION = (
        ('k', 'Kitchener'),
        ('h', 'Hamilton'),
    )
    
    office = models.CharField(max_length=1, choices=OFFICE_LOCATION, default='k', help_text='')

    def get_absolute_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('roomkey-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return '{0}'.format(self.room_name)


@deconstructible
class KeyInstance(models.Model):

    """
    Model representing key instances.
    """
    roomkey = models.ForeignKey('RoomKey',verbose_name="Room", on_delete=models.SET_NULL, null=True)

    LOAN_STATUS = (
        ('a', 'Available'),
        ('o', 'On loan'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, help_text='Key availability', verbose_name="Key status", blank=True)

    date_out = models.DateField(null=True, blank=True, verbose_name="Date Issued")
    due_back = models.DateField(null=True, blank=True, verbose_name="Date to be returned")
    date_returned = models.DateField(null=True, blank=True,verbose_name="Date that it has been returned")
    
    key_notes = models.CharField(max_length=2000, help_text='Key instance notes if applicable', null=True, blank=True)

    is_requested = models.BooleanField(blank=True, default=False,help_text="Is this key being requested ?", verbose_name="Is requested")

    REQUEST_STATUS = (
        ('p', 'Pending'),
        ('a', 'Approved'),
        ('d', 'Denied'),
    )


    request_status = models.CharField(max_length=1, choices=REQUEST_STATUS, default='p', verbose_name='Request status',
                                      blank=True)

    date_requested = models.DateField(null=True,blank=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular key")

    borrower = models.CharField(max_length=100, help_text="Enter the name of the borrower.",null=True,blank=True, verbose_name="Borrower",)

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set key as returned"),)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False
    
    def __str__(self):
        """
        String for representing the Model object
        """
        return '{1} ({0})'.format(self.id,self.roomkey.room_name)

    def get_absolute_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('keys',args={'pk':self.id})

class KeyRequest(models.Model):
    """
    Model that will hold the key requests
    """

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular request")

    # keyinstance = models.OneToOneField(
    #     KeyInstance,
    #     on_delete=models.CASCADE,
    #     primary_key=True,
    #     default=KeyInstance(roomkey=RoomKey(room_name='Grand River'),status='a')
    # )
    roomkey = models.ForeignKey('RoomKey',verbose_name="Room", on_delete=models.SET_NULL, null=True)

    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Requested by')
    
    # borrower is ther person who has the key
    borrower = models.CharField(max_length=100, help_text='Enter the full name of the person who will be responsible for the key')

    REQUEST_STATUS = (
        ('p', 'Pending'),
        ('a', 'Approved'),
        ('d', 'Denied'),
    )

    request_status = models.CharField(max_length=1, choices=REQUEST_STATUS, default='p', verbose_name='Request status', blank=True)

    date_requested = models.DateField(auto_now_add=True)
    date_due_back = models.DateField(default=(date.today() + timedelta(weeks=2)))
    date_completed = models.DateField(null=True, blank=True)
    
    request_comments =  models.TextField(max_length=2000, help_text='Enter a brief reason for the request')

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{2}-{0} ({1})'.format(self.roomkey.room_name, self.date_requested, self.requester)

    def get_absolute_url(self):

        return reverse('key-request-detail', args=[str(self.id)])

class MaintenanceRequest(models.Model):
    """
    Model that will hold the maintenance requests
    """
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Requested by')
    
    OFFICE_LOCATION = (
        ('k', 'Kitchener'),
        ('h', 'Hamilton'),
    )
    
    office = models.CharField(max_length=1, choices=OFFICE_LOCATION, default='k', help_text='')

    UG_LEVEL = (
        ('2', 'Low'),
        ('1', 'Medium'),
        ('0', 'High'),
    )

    urgency = models.CharField(max_length=1, choices=UG_LEVEL, default='2')

    REQUEST_STATUS = (
        ('s', 'Submitted'),
        ('w', 'Work in Progress'),
        ('c', 'Completed'),
    )

    status = models.CharField(max_length=1, choices=REQUEST_STATUS, blank=True, default='s', help_text='') 

    date_submitted = models.DateField(auto_now_add=True)
    date_completed = models.DateField(null=True, blank=True)
    request_comments =  models.TextField(max_length=2000, help_text='Enter a brief description of the request')

    def get_absolute_url(self):
        """
        Returns the url to access a detail record for this book.
        """
        return reverse('maintenancerequest-detail', args=[str(self.id)])

    def get_compcount(self):
        return MaintenanceRequest.objects.filter(status__exact='c').count()

    def get_pendcount(self):
        return MaintenanceRequest.objects.exclude(status__exact='c').count()

class MoveRequest(models.Model):
    """
    Model that will hold move requests
    """
    move_person = models.CharField(max_length=40)
    move_to = models.CharField(max_length=100)
    move_date = models.DateField(help_text='Enter the proposed date of move')
    move_conditions = models.CharField(max_length=2000, null=True, blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


# ===================================================================================================

