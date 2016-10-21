from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Table(models.Model):
    user = models.ForeignKey(User)
    
    database = models.CharField(
        max_length=300,
        blank=False,
        null=False
    )

    table = models.CharField(
        max_length=300,
        blank=False,
        null=False        
    )
    
    upload_time = models.DateTimeField(auto_now_add=True)

    upload_log = models.TextField(
        blank=True
    )
    
    source = models.CharField(
        max_length=300,
        blank=False,
        null=False
    )
    
    next_update = models.DateField(
        blank=True,
        null=True
    )
    
    
class Column(models.Model):
    INFORMATION_TYPE_CHOICES = (
        ("full_name","Full Name"),
        ("last_name","Last Name"),
        ("first name","First Name"),
        ("middle_name","Middle Name"),
        ("other_name","Other Name"),
        ("full_add","Full Address"),
        ("street_add","Street"),
        ("city_add","City"),
        ("county_add","County"),
        ("state_add","State"),
        ("zip_add","ZIP"),
        ("other_add","Other Address"),
        ("organization_name","Organization Name"),
        ("corp_or_person_name","Corporate or Person Name")
    ) 

    MYSQL_TYPE_CHOICES = (
        ("varchar","VARCHAR"),
        ("char","CHAR"),
        ("text","TEXT"),
        ("longtext","LONGTEXT"),
        ("decimal","DECIMAL"),
        ("double","DOUBLE"),
        ("int","INT"),
        ("date","DATE"),
        ("datetime","DATETIME"),
        ("timestamp","TIMESTAMP"),
        ("json","JSON"),
        ("binary","BINARY")
    )
    
    table = models.ForeignKey(Table)
    
    column = models.CharField(
        max_length=300,
        blank=False,
        null=False
    )
    
    mysql_type = models.CharField(
        choices=MYSQL_TYPE_CHOICES,
        max_length=300,
        blank=False,
        null=False
    )
    
    column_size = models.CharField(
        max_length=10,
        null=True
    )
    
    information_type = models.CharField(
        choices=INFORMATION_TYPE_CHOICES,
        max_length=30,
        blank=True,
        null=True
    )
    
class Contact(models.Model):
    table = models.ForeignKey(Table)
    
    name = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    
    email = models.EmailField(
        max_length=300,
        blank=True,
        null=True
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    CONTACT_TYPE_CHOICES = (
        ("pio","Press Officer"),
        ("tech","Technical Contact"),
        ("leg","Legal Contact"),
        ("other","Other")
    )
    
    contact_type = models.CharField(
        choices=CONTACT_TYPE_CHOICES,
        max_length=50,
        blank=False,
        null=False
    )
