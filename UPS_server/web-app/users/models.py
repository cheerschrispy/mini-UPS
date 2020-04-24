from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class package(models.Model):
	#name = models.CharField(max_length=100)
	trackingnum = models.IntegerField()
	#ownername=models.CharField(max_length=100)
	owner = models.CharField(max_length=100,verbose_name="owner name",blank=True)
	truckid = models.IntegerField(verbose_name="once carried by which truck")
	detail = models.CharField(max_length=300)
	x = models.IntegerField()
	y = models.IntegerField()
	status = models.CharField(max_length=300)
	#created,truck enroute to wharehouse,packing,out for deliver

	def __str__(self):
		return self.owner
	#no need to have a return reverse url

class truck(models.Model):
	status = models.CharField(max_length=100)
	whid=models.IntegerField(blank=True)
	



