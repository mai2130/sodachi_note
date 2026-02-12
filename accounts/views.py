from django.views.generic import FormView
from django.contrib.auth import login, get_user_model 
from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView

from .forms import EmailAuthenticationForm, FacilitySignUpForm, GuardianSignUpForm ,ChildMyPageForm
from nurseries.models import Nursery
from invites.models import InviteCode
from families.models import Family
from django.db.models import F
from django.urls import reverse_lazy
from .forms import ChildMyPageForm

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
    success_url = reverse_lazy('dashboard:home')
    
    @transaction.atomic
    def form_valid(self, form):
        invite = form.cleaned_data.get("invite")
        if not invite:
            form.add_error("invite_code", "無効な認証コードです")
            return self.form_invalid(form)
        
        if not invite.is_available:
            form.add_error("invite_code", "この認証コードは利用上限に達しています")
            return self.form_invalid(form)
        
        user = User.objects.create_user(
            username=form.cleaned_data["email"], 
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            role=User.Role.GUARDIAN,
        )
        
        Family.objects.get_or_create(
            guardian=user,
            child=invite.child,
            defaults={"relationship": form.cleaned_data["relationship"]}, 
        )
        
        user.active_child = invite.child
        user.save(update_fields=["active_child"])
        
# 招待コードの使用回数を +1（DB側で安全に更新）        
        InviteCode.objects.filter(pk=invite.pk).update(
            users_count=F("users_count") + 1
        )
        login(self.request, user)   
        return super().form_valid(form)

class ChildMyPageView(LoginRequiredMixin, View):
    template_name = "accounts/child_mypage.html"

    def get(self, request):
        child = request.user.active_child
        if not child:
            messages.error(request,"園児が選択されていません")
            return redirect("dashboard:home")

        form = ChildMyPageForm(instance=request.user)

        return render(request, self.template_name,{
            "form": form,
            "child": child,
            "guardian":request.user
        })
    
    def post(self, request):
        child = request.user.active_child
        if not child:
            messages.error(request,"園児が選択されていません")
            return redirect("dashboard:home")
        
        form = ChildMyPageForm(request.POST, instance=request.user)
        
        if not form.is_valid():
            messages.error(request, "未入力項目があります")
            return render(request, self.template_name,{
                "form" : form,
                "child": child,
                "guardian":request.user,
            })
        form.save()
        messages.success(request, "保存しました！")
        return redirect("accounts:child_mypage")
    
class UserPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change")

    def form_valid(self, form):
        messages.success(self.request, "パスワードを変更しました")
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user

        if hasattr(user, "role") and user.role == user.Role.FACILITY:
            return reverse_lazy("nurseries:mypage")   
        return reverse_lazy("accounts:child_mypage")