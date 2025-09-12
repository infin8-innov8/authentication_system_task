from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class UserAccount(AbstractUser) : 
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    class Meta : 
        db_table = "User Accounts"  
        verbose_name = "User Account"
        verbose_name_plural = "User Account"

    def save(self, *args, **kwargs) : 
        if self.first_name : 
            self.first_name = self.first_name.upper()

        if self.first_name : 
            self.last_name = self.last_name.upper()

        super().save(*args, **kwargs)
