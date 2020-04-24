from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
#这里用了继承的form，为了添加新的field
from .forms import UserRegisterForm,trackingNumInputForm,UpdatePackagesInfoForms
from .models import package
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView,DetailView,CreateView,UpdateView,DeleteView)
from django.core.mail import send_mail


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            #userID=form.cleaned_data.get('userID')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    #_driver=RequestofDriver.objects.filter(driver = request.user)
    context={'user':request.user}
    return render(request, 'users/profile.html',context)



def trackPackage(request):
    #if request.users
    if request.method == 'POST':
        p_form = trackingNumInputForm(request.POST)
        if p_form.is_valid():
            trackingNum = p_form.cleaned_data.get("trackingNumber")
            print(trackingNum)
            current = package.objects.filter(trackingnum = trackingNum )
            context = {
        'unposts': current
}      
        return render(request, 'users/trackingList.html',context)
    else:
    #u_form = UserUpdateForm(instance=request.user)
        p_form = trackingNumInputForm()
        context = {
        'form': p_form
}      
    return render(request, 'users/trackingInput.html',context)


@login_required
def viewOwnOrder(request):
    context = {
        'posts': package.objects.filter(Q(owner=request.user.username),Q(status="created")|Q(status="packing")|Q(status="truck enroute to wharehouse")) ,
        'unposts': package.objects.filter(Q(owner=request.user.username),Q(status="out for deliver")|Q(status="delivered"))
    }
    return render(request, 'users/allPackages.html', context)


@login_required
def updateInfo (request, package_id):
    if request.method == 'POST':
        p_form = UpdatePackagesInfoForms(request.POST)
        #print (p_form.fields.des)
        if p_form.is_valid():
            print(package_id)
            current = package.objects.get(id = package_id )
             
            #_name = p_form.cleaned_data.get("name")
            
            #_trackingNum = p_form.cleaned_data.get("trackingNum")
            #_status= p_form.cleaned_data.get("des")
            _X = p_form.cleaned_data.get("new_X")
            _Y = p_form.cleaned_data.get("new_Y")

            #current.name = _name
            #current.trackingNum = _trackingNum
            current.x = _X
            current.y = _Y
            current.save()
            messages.success(request, f'Your account has been updated!')
            
            send_mail(
            'Package Information Updated',
            'You have updated your destination successfully',
            'UPS Services',
            [request.user.email],
            fail_silently=False,

    )
            return redirect('viewOwnOrder')
    else:
        p_form = UpdatePackagesInfoForms()

    context = {
        'form': p_form
}

    return render(request, 'users/updatePackages.html', context)
    








class packageCreateView(LoginRequiredMixin, CreateView):
    model = package
    fields = ['name', 'trackingNum','X','Y']

    def form_valid(self, form):
        print(form.instance.id)
        form.instance.owner= self.request.user
        
        return super().form_valid(form)





