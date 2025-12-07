from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q #条件を「OR」などで組み合わせたいときに使うクラス

from children.models import Child
#from nurseries.models import Classroom
from .models import Notice
from .forms import NoticeForm

#おたより一覧ページ   
class NoticeListView(LoginRequiredMixin, ListView):
    model = Notice
    template_name = 'notices/list.html'
    context_object_name = 'notices'
    paginate_by = 10
        
    def get_queryset(self):
        user = self.request.user
        today = timezone.localdate() #今日の日付
            
        qs = Notice.objects.filter(date__lte=today)
        
        get = self.request.GET
         
        # ユーザーが園アカウントか保護者アカウントかで絞り込み        
        if hasattr(user, "nursery"):
            qs = qs.filter(nursery=user.nursery) #園アカウントの場合は自分の園のおたよりのみ表示
        
        # 保護者アカウントの場合   
        else:
            children = (
                Child.objects
                .filter(family_links__guardian=user)
                .select_related("nursery")
                .distinct()
            ) 
                
            if not children:
                return Notice.objects.none()
            
            nursery_ids = {c.nursery_id for c in children}
            
            qs = qs.filter(nursery_id__in=nursery_ids)
          
        # 年月日（完全一致）
        date_str = get.get("date")
        if date_str:
            qs = qs.filter(date=date_str)

        # カテゴリ（0〜4 の整数）
        category = get.get("category")
        if category not in (None, ""):
            qs = qs.filter(category=int(category))

        # キーワード（タイトル or 本文に含まれる）
        keyword = get.get("keyword")
        if keyword:
            qs = qs.filter(
                Q(title__icontains=keyword) |
                Q(body__icontains=keyword)
            )

        # クラス（ManyToMany：Notice.classrooms）
        classroom = get.get("classroom")
        if classroom:
            qs = qs.filter(classrooms__id=classroom)      
       
        # 新しい順に並べて返す
        return qs.order_by("-date", "-id")  

# おたより詳細ページ                
class NoticeDetailView(LoginRequiredMixin, DetailView):
    model = Notice
    template_name = 'notices/detail.html'
    context_object_name = 'notice'
    
    def get_queryset(self):
        list_view = NoticeListView()
        list_view.request = self.request
        return list_view.get_queryset()

# おたより新規投稿ページ
class NoticeCreateView(LoginRequiredMixin, CreateView):
    model= Notice
    form_class = NoticeForm
    template_name = 'notices/create.html'
    success_url = reverse_lazy('notices:list')
    
    def form_valid(self, form):
        form.instance.nursery = self.request.user.nursery
        return super().form_valid(form)

# おたより編集ページ
class NoticeUpdateView(LoginRequiredMixin, UpdateView):
    model = Notice
    form_class = NoticeForm
    template_name = 'notices/edit.html'
    success_url = reverse_lazy('notices:list')
    
    def get_queryset(self):
        list_view = NoticeListView()
        list_view.request = self.request
        return list_view.get_queryset()
    
    def form_valid(self, form):
        if hasattr(self.request.user, "nursery"):
            form.instance.nursery = self.request.user.nursery
        return super().form_valid(form)