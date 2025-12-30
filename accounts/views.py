from django.views.generic import FormView
from django.contrib.auth import login, get_user_model # テンプレ表示/リダイレクト
from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction

from .forms import EmailAuthenticationForm, FacilitySignUpForm, GuardianSignUpForm
from nurseries.models import Nursery
from invites.models import InviteCode
from families.models import Family
from django.db.models import F

User = get_user_model()

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
    
        user = User.objects.create_user(
            username = form.cleaned_data["email"],
            email = form.cleaned_data["email"],
            password =form.cleaned_data["password1"],
            role = User.Role.FACILITY,
        )

        Nursery.objects.create(
            user = user,
            name = form.cleaned_data["nursery_name"],
            postal_code = form.cleaned_data["postal_code"],
            address = form.cleaned_data["address"],
            phone_number = form.cleaned_data["phone_number"],
        )
        
        login(request, user)
        return redirect('dashboard:home')
    
class GuardianSignUpView(FormView):
    template_name = "registration/signup_guardian.html"
    form_class = GuardianSignUpForm
    success_url = '/dashboard/'
    
    @transaction.atomic
    def form_valid(self, form):
        invite = form.cleaned_data["invite"]
        
        user = User.objects.create_user(
            username=form.cleaned_data["email"], 
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            role=User.Role.GUARDIAN,)
        
        Family.objects.get_or_create(
            guardian=user,
            child=invite.child,
            defaults={"relationship": form.cleaned_data["relationship"]}, 
        )
# 招待コードの使用回数を +1（DB側で安全に更新）        
        InviteCode.objects.filter(pk=invite.pk).update(
            users_count=F("users_count") + 1
        )
         
        login(self.request, user)   
        return super().form_valid(form)
