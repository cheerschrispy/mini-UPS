from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class package(models.Model):
	name  = models.CharField(max_length=100)
	trackingNum = models.CharField(max_length=100)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	X = models.CharField(max_length=100)
	Y = models.CharField(max_length=100)
	status= models.IntegerField(default=0, verbose_name='Delivery Status (in warehouse, delivering, delivered)')

	def __str__(self):
		return self.name
	#no need to have a return reverse url