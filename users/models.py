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
     phone = models.CharField(max_length=20, blank=True)
     organization_number = models.CharField(max_length=9, blank=True, null=True, help_text="Valgfritt. 9 sifre.")

     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
         return self.organization_name


# Custom user manager
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have a username')
        
        user = self.model(
            email=self.normalize_email(email), #if you enter a capiotal letter in email it will convert it to lowercase
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
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
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)

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
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True