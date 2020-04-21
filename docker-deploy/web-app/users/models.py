from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class package(models.Model):
	name  = models.CharField(max_length=100)
	trackingnum = models.CharField(max_length=100)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	x = models.CharField(max_length=100)
	y = models.CharField(max_length=100)
	status= models.IntegerField(default=0, verbose_name='Delivery Status (in warehouse, delivering, delivered)')

	def __str__(self):
		return self.namey
	#no need to have a return reverse url

class truck(models.Model):
	status = models.CharField(max_length=100)


