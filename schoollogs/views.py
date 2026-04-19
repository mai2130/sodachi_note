from decimal import Decimal
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST

from children.models import Child
from .forms import SchoolGrowthLogForm, HomeGrowthLogForm
from .models import GrowthLog
from families.models import Family

# 日付を決める共通関数
def _get_target_date(request, key="d"):
    # ?d=YYYY-MM-DD を日付にして返す（ない場合は今日）
    d_str = request.GET.get(key)
    if not d_str :
        return date.today()
    try:
        return datetime.strptime(d_str, "%Y-%m-%d").date()
    except ValueError:
        return date.today()

class SchoolGrowthLogView(LoginRequiredMixin, View):
    template_name = 'growthlogs/school_growthlog_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "nursery"):
            messages.error(
                request,
                "この画面は園アカウント専用です",
                extra_tags="home_message"
            )
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)
    
    def _ensure_active_child(self, request):
        # 園ユーザーの active_child が正しい園児になるように整える関数
        nursery = getattr(request.user, "nursery", None)
        if nursery is None:
            return None, None

        children = nursery.children.all().order_by("id")
        child = getattr(request.user, "active_child", None)

        if (not child) or (child.nursery_id != nursery.id):
            first = children.first()
            if not first:
                return children, None
            request.user.active_child = first
            request.user.save(update_fields=["active_child"])
            child = first

        return children, child
    
    def _redirect_home(self, target_date, child_id=None):
        # 保存後にホーム画面へ戻すための共通関数
        url = reverse("dashboard:home")
        if child_id:
            return redirect(f"{url}?d={target_date:%Y-%m-%d}&child_id={child_id}")
        return redirect(f"{url}?d={target_date:%Y-%m-%d}")
    
    def _get_or_create_log(self, child, target_date):
        # 園側の「その子・その日」の記録を取得し、無ければ作る関数
        log, _ = GrowthLog.objects.get_or_create(
            child=child,
            source=GrowthLog.Source.SCHOOL,
            date=target_date,
            defaults={"school_temperature": Decimal("36.5")},
        )
        return log
    
    def get(self, request):
        # 画面を開いたときの表示処理
        children, child = self._ensure_active_child(request)
        
        if not child:
            messages.error(request, "園児が選択されていません", extra_tags="home_message")
            return redirect("dashboard:home")
        
        target_date = _get_target_date(request, "d")
        log = self._get_or_create_log(child, target_date)
        form = SchoolGrowthLogForm(instance=log)
        
        return render(request, self.template_name,
        {
            "children":children,
            "selected_child":child,
            "form":form,
            "log":log,
            "date":target_date,
            "child":child
        },
        )
    
    def post(self, request):
        # 園側フォーム送信時の保存処理
        children, child = self._ensure_active_child(request)
        if not child:
            messages.error(request, "園児が選択されていません", extra_tags="home_message")
            return redirect("dashboard:home")
        
        target_date = _get_target_date(request, "d")
        log = self._get_or_create_log(child, target_date)

        if getattr(log, "submitted", False):
            messages.error(request, "提出後は修正できません", extra_tags="home_message")
            return self._redirect_home(target_date, child_id=child.id) 
        
        form = SchoolGrowthLogForm(request.POST, request.FILES, instance=log)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "children": children,
                    "selected_child": child,
                    "form": form,
                    "log": log,
                    "date": target_date,
                    "child": child,
                },
            )
        obj = form.save(commit=False)
        obj.child = child
        obj.source = GrowthLog.Source.SCHOOL
        obj.date = target_date

        action = request.POST.get("action")
        if action == "submit":
            obj.submitted = True
            messages.success(request, "提出しました", extra_tags="home_message")
        else:
            messages.success(request, "一時保存しました", extra_tags="home_message")

        obj.save()
        return self._redirect_home(target_date, child_id=child.id)
                
class HomeGrowthLogView(LoginRequiredMixin, View):
    template_name = "growthlogs/home_growthlog_form.html"

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, "nursery"):
            messages.error(
                request,
                "この画面は保護者アカウント専用です",
                extra_tags="home_message"
            )
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def _get_child(self, request):
        child = getattr(request.user, "active_child", None)
        if child:
            return child
        
        link = (
            Family.objects.filter(guardian=request.user)
            .select_related("child")
            .first()
        )
        if not link:
            return None
        
        request.user.active_child = link.child
        request.user.save(update_fields=["active_child"])
        return link.child

    def _redirect_home(self, target_date):
        url = reverse("dashboard:home")
        return redirect(f"{url}?d={target_date:%Y-%m-%d}")
    
    def _get_or_create_log(self, child, target_date):
        log, _ = GrowthLog.objects.get_or_create(
            child=child,
            source=GrowthLog.Source.HOME,
            date=target_date,
            defaults={"home_temperature": Decimal("37.0")},
        )
        return log
    
    def get(self, request):
        child = self._get_child(request)
        if not child:
            messages.error(request, "園児が選択されていません", extra_tags="home_message")
            return redirect("dashboard:home")

        target_date = _get_target_date(request, "d")

        log = self._get_or_create_log(child, target_date)
    
        form = HomeGrowthLogForm(instance=log)
        return render(
            request,
            self.template_name,
            {
            "form": form,
            "log": log,
            "date": target_date,
            "child": child,
            },
        )

    def post(self, request):
        child = self._get_child(request)
        if not child:
            messages.error(request, "園児が選択されていません", extra_tags="home_message")
            return redirect("dashboard:home")

        target_date = _get_target_date(request, "d")

        log = self._get_or_create_log(child, target_date)

        if getattr(log, "submitted", False):
            messages.error(request, "提出後は修正できません", extra_tags="home_message")
            return self._redirect_home(target_date)

        form = HomeGrowthLogForm(request.POST, instance=log)
        
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "log": log,
                    "date": target_date,
                    "child": child,
                },
        )
        
        obj = form.save(commit=False)
        obj.child = child
        obj.source = GrowthLog.Source.HOME
        obj.date = target_date
        
        action = request.POST.get("action")
        if action == "submit":
            if hasattr(obj, "submitted"):
                obj.submitted = True
            messages.success(request, "提出しました", extra_tags="home_message")
        else:
            messages.success(request, "一時保存しました", extra_tags="home_message")

        obj.save()
        return self._redirect_home(target_date)

@require_POST
@login_required
def select_child(request):
    child_id = request.POST.get("child_id")
    next_url = request.POST.get("next") or "dashboard:home"

    if not child_id:
        messages.error(request, "園児が選択されていません", extra_tags="home_message")
        return redirect(next_url)
    
    nursery = getattr(request.user, "nursery", None)
    if nursery is None:
        messages.error(request, "園情報が見つかりません", extra_tags="home_message")
        return redirect(next_url)
    
    child = get_object_or_404(
        Child, id= child_id,
        nursery=nursery,
    )
    request.user.active_child = child
    request.user.save(update_fields=["active_child"])

    return redirect(next_url)

        