from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    #email = forms.EmailField()
    userID=forms.CharField()
    class Meta:
        model = User
        fields = ['username','userID','password1', 'password2']
        
class trackingNumInputForm(forms.Form):
    trackingNumber=forms.CharField(max_length=100)



class UpdatePackagesInfoForms(forms.Form):
	name  =forms.CharField(max_length=100)
	trackingNum = forms.CharField(max_length=100)
	X = forms.CharField(max_length=100)
	Y = forms.CharField(max_length=100)


