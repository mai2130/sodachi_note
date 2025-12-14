from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction
from .forms import EmailAuthenticationForm, FacilitySignUpForm
from nurseries.models import Nursery



class EmailLoginView(View):
    template_name = 'registration/login.html'

    def get(self,request):
        form = EmailAuthenticationForm()
        return render(request, self.template_name,{'form':form})
    
    def post(self, request):
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('dashboard:home')
        return render(request, self.template_name,{'form':form})
     
class FacilitySignUpView(View):
    template_name = "registration/signup_facility.html"
    
    def get(self, request):
        return render(request, self.template_name, {"form":FacilitySignUpForm()})
    
    @transaction.atomic
    def post(self, request):
        form = FacilitySignUpForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form":form})
    
        User = get_user_model()    
        #ユーザー作成
        user = User.objects.create_user(
            username = form.cleaned_data["email"],
            email = form.cleaned_data["email"],
            password =form.cleaned_data["password1"],
            role = User.Role.FACILITY,
        )
        #園情報作成
        Nursery.objects.create(
            user = user,
            name = form.cleaned_data["nursery_name"],
            postal_code = form.cleaned_data["postal_code"],
            address = form.cleaned_data["address"],
            phone_number = form.cleaned_data["phone_number"],
        )
        
        login(request, user)
        return redirect('dashboard:home')
    