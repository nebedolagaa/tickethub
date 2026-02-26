''' 
Bidratt til denne filen:
    - Kamilla Nizamova
'''
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

User = settings.AUTH_USER_MODEL

# Organizer profile model
class OrganizerProfile(models.Model):
     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organizer_profile')
     organization_name = models.CharField(max_length=255)
     contact_email = models.EmailField()
     phone_number = models.CharField(max_length=20, blank=True)
     organization_number = models.CharField(max_length=9, blank=True, null=True, help_text="Valgfritt. 9 sifre.")
     
     # Valgfritt: adresse, postnummer og by for arrangøren.
     #adresse ligger her for å skille mellom users-hjemmeadresse og organisasjonens adresse 
     organization_address = models.CharField(max_length=255, blank=True, null=True)
     organization_postcode = models.CharField(max_length=20, blank=True, null=True)
     organization_city = models.CharField(max_length=100, blank=True, null=True)

     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
         return self.organization_name


# Custom user manager
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email)
        
        user = self.model(
            email=self.normalize_email(email), #if you enter a capiotal letter in email it will convert it to lowercase
            first_name=first_name,
            last_name=last_name,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, first_name, last_name, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user
    

# Custom user model
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    #required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    #login with email not username like it is by default
    USERNAME_FIELD = 'email'

    #these fields will be asked when creating a superuser
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    

#modell for å lagre ekstra informasjon om brukeren som ikke er i Account modellen, for eksempel telefonnummer, adresse osv.
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address = models.CharField(blank=True, max_length=255)
    city = models.CharField(blank=True, max_length=100)
    postal_code = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
    

    def full_address(self):
        return f"{self.address}, {self.postal_code} {self.city}, {self.country}"