from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings
import ldap
class UserAccount(AbstractUser) : 
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    
    def __str__(self):
        return self.email
    

    def save(self, *args, **kwargs) : 
        if self.first_name : 
            self.first_name = self.first_name.title()

        if self.first_name : 
            self.last_name = self.last_name.title()

        super().save(*args, **kwargs)

@receiver(pre_delete, sender=UserAccount)
def delete_ldap_user(sender, instance, **kwargs):
    """
    Deletes the corresponding user from the LDAP server before
    the user is deleted from the local Django database.
    """
    try:
        # 1. Establish a connection to the LDAP server
        con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

        # 2. Define the user's Distinguished Name (DN)
        base_dn = settings.AUTH_LDAP_USER_SEARCH.base_dn
        dn = f"uid={instance.username},{base_dn}"

        # 3. Delete the user from the LDAP directory
        con.delete_s(dn)
        con.unbind_s()
        print(f"Successfully deleted user '{instance.username}' from LDAP.")

    except ldap.NO_SUCH_OBJECT:
        # This is okay, the user might not exist in LDAP
        print(f"User '{instance.username}' not found in LDAP, skipping deletion.")
    except Exception as e:
        # We should log this error but not stop the Django deletion
        print(f"An error occurred while trying to delete user from LDAP: {e}")
