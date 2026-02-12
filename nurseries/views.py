from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView #「編集（更新）画面」作成クラス、フォーム表示（GET）と保存（POST）を自動で実装
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from .models import Nursery
from .forms import NurseryMyPageForm

class NurseryMyPageView(LoginRequiredMixin, UpdateView):
    model = Nursery
    form_class = NurseryMyPageForm
    template_name = "nurseries/mypage.html"
    success_url = reverse_lazy("nurseries:nursery_mypage")
    
    def get_object(self, queryset =None):
        #ログインユーザーに紐づく園を編集対象にする
        return self.request.user.nursery
    
    def form_valid(self, form):
        messages.success(self.request, "保存しました！")
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        # 保護者が来たら弾く
        if hasattr(request.user, "is_guardian") and request.user.is_guardian():
            messages.error(request, "このページは園アカウント専用です")
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)
