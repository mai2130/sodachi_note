from decimal import Decimal
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View

from children.models import Child
from .forms import SchoolGrowthLogForm, HomeGrowthLogForm
from .models import GrowthLog

def _get_target_date(request, key="d"):
    d_str = request.GET.get(key)
    if not d_str :
        return date.today()
    try:
        return datetime.strptime(d_str, "%Y-%m-%d").date()
    except ValueError:
        return date.today()

class SchoolGrowthLogView(LoginRequiredMixin, View):
    template_name = 'growthlogs/school_growthlog_form.html'

    def _get_child(self, request):
        child_id = request.GET.get("child_id")
        if not child_id:
            return None
        return get_object_or_404(
            Child,
            pk=child_id,
            nursery=request.user.nursery,
        )
        
    def get(self, request):
        child = self._get_child(request)
        if not child:
            messages.error(request, "園児が選択されていません")
            return redirect("dashboard:home")
        
        target_date = _get_target_date(request, "d")
        
        log, _ = GrowthLog.objects.get_or_create(
            child=child,
            source=GrowthLog.Source.SCHOOL,
            date=target_date,
            defaults={"school_temperature": Decimal("36.5")},
        )
        
        form = SchoolGrowthLogForm(instance=log)
        return render(request, self.template_name, {"form":form, "log":log, "date":target_date, "child":child})
    
    def post(self, request):
        child = self._get_child(request)
        if not child:
            messages.error(request, "園児が選択されていません")
            return redirect("dashboard:home")

        target_date = _get_target_date(request, "d")

        log, _ = GrowthLog.objects.get_or_create(
            child=child,
            source=GrowthLog.Source.SCHOOL,
            date=target_date,
            defaults={"school_temperature": Decimal("36.5")},
        )

        form = SchoolGrowthLogForm(request.POST, request.FILES, instance=log)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.child = child
            obj.source = GrowthLog.Source.SCHOOL
            obj.date = target_date
            obj.save()
            messages.success(request, "保存しました！")
            return redirect(f"{reverse('schoollogs:school_growthlog_form')}?child_id={child.id}&d={target_date}")

        return render(request, self.template_name, {"form": form, "log": log, "date": target_date, "child": child})

class HomeGrowthLogView(LoginRequiredMixin, View):
    template_name = "growthlogs/home_growthlog_form.html"

    def get(self, request):
        child = getattr(request.user, "active_child", None)
        if not child:
            messages.error(request, "園児が選択されていません")
            return redirect("dashboard:home")

        target_date = _get_target_date(request, "d")

        log, _ = GrowthLog.objects.get_or_create(
            child=child,
            source=GrowthLog.Source.HOME,
            date=target_date,
            defaults={"home_temperature": Decimal("37.0")},
        )

        form = HomeGrowthLogForm(instance=log)
        return render(request, self.template_name, {"form": form, "log": log, "date": target_date})

    def post(self, request):
        child = getattr(request.user, "active_child", None)
        if not child:
            messages.error(request, "園児が選択されていません")
            return redirect("dashboard:home")

        target_date = _get_target_date(request, "d")

        log, _ = GrowthLog.objects.get_or_create(
            child=child,
            source=GrowthLog.Source.HOME,
            date=target_date,
            defaults={"home_temperature": Decimal("37.0")},
        )

        if log.submitted:
            messages.error(request, "提出後は修正できません")
            return redirect(f"{reverse('schoollogs:home_growthlog_form')}?d={target_date}")

        form = HomeGrowthLogForm(request.POST, instance=log)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "log": log, "date": target_date})

        obj = form.save(commit=False)
        obj.child = child
        obj.source = GrowthLog.Source.HOME
        obj.date = target_date
        
        action = request.POST.get("action")
        if "action" == "submit":
            messages.success(request, "提出しました")
        else:
            messages.success(request, "一時保存しました")

        obj.save()
        return redirect(f"{reverse('schoollogs:home_growthlog_form')}?d={target_date:%Y-%m-%d}")
        