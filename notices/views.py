from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q #条件を「OR」などで組み合わせたいときに使うクラス

from children.models import Child
from .models import Notice
from .forms import NoticeForm
import re

#おたより一覧ページ   
class NoticeListView(LoginRequiredMixin, ListView):
    model = Notice
    template_name = 'notices/list.html'
    context_object_name = 'notices'
    paginate_by = 10
        
    def get_queryset(self):
        user = self.request.user
        today = timezone.localdate() #今日の日付
        # 今日以前のおたよりだけに限定   
        qs = Notice.objects.filter(date__lte=today)
        
        get = self.request.GET
        # ユーザーが園もしくは保護者アカウントか絞る
        # 園アカウントの場合:自分の園のおたよりのみ表示
        if hasattr(user, "nursery"):
            qs = qs.filter(nursery=user.nursery) 
        
        # 保護者アカウントの場合   
        else:
            # 保護者に紐づく園児一覧
            children = (
                Child.objects
                .filter(family_links__guardian=user)
                .select_related("classroom", "nursery")
                .distinct()
            ) 
                
            if not children.exists():
                return Notice.objects.none()
            
            # 今見ている園児（active_child)があるならその子だけ対象
            active_child = getattr(user, "active_child", None)

            if active_child:
                # 園を固定
                qs = qs.filter(nursery_id=active_child.nursery_id)
                # クラス指定ありのおたより：そのクラスに含まれるものだけ
                # クラス指定なし：全体発信なので表示OK
                qs = qs.filter(
                    Q(noticeclassroom__isnull=True)|Q(classrooms=active_child.classroom)
                ).distinct()

            else:
                # active_childがない場合は紐づく園児の園まで許可
                nursery_ids = {c.nursery_id for c in children}
                qs = qs.filter(nursery_id__in=nursery_ids)

                  
        # 年月日で絞る
        month = get.get("month")
        if month:
            from datetime import date
            import calendar

            y,m = map(int, month.split("-"))
            start = date(y, m, 1)
            end = date(y, m, calendar.monthrange(y,m)[1])
            qs = qs.filter(date__range=(start, end))
        
        category = get.get("category")
        if category not in(None, ""):
            qs =qs.filter(category=int(category))
        
        keyword = get.get("keyword")
        if keyword:
            qs = qs.filter(
                Q(title__icontains=keyword)|
                Q(body__icontains=keyword)
            )
        
        classroom = get.get("classroom")
        if classroom:
            qs = qs.filter(classrooms__id=classroom)

        return qs.order_by("-date", "-id").distinct()
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 年月プルダウン用：直近12ヶ月
        today = timezone.localdate()
        month_options = []
        y, m = today.year, today.month
        for i in range(12):
            mm = m - i
            yy = y
            while mm <= 0:
                mm += 12
                yy -= 1
            month_options.append({
                "value": f"{yy:04d}-{mm:02d}",
                "label": f"{yy:04d}年{mm:02d}月"
            })
        ctx["month_options"] = month_options

        # カテゴリプルダウン用
        ctx["category_options"] = [{"value": v, "label": l} for v, l in Notice.Category.choices]

        # クラスプルダウン用
        user = self.request.user
        if hasattr(user, "nursery"):
            # 園アカウント：自園のクラス
            ctx["classroom_options"] = user.nursery.classrooms.all()
        else:
            # 保護者：active_child があればその園のクラス、なければ紐づく園児の園のクラス
            active_child = getattr(user, "active_child", None)
            if active_child:
                ctx["classroom_options"] = active_child.nursery.classrooms.all()
            else:
                children = (
                    Child.objects
                    .filter(family_links__guardian=user)
                    .select_related("nursery")
                    .distinct()
                )
                nursery_ids = {c.nursery_id for c in children}

                from nurseries.models import Classroom
                ctx["classroom_options"] = Classroom.objects.filter(nursery_id__in=nursery_ids)

        # 投稿画面へ（園だけ表示にしたい時用）
        ctx["can_post"] = hasattr(user, "nursery")
        ctx["can_edit"] = hasattr(user, "nursery")

        return ctx

# おたより詳細ページ                
class NoticeDetailView(LoginRequiredMixin, DetailView):
    model = Notice
    template_name = 'notices/detail.html'
    context_object_name = 'notice'
    
    def get_queryset(self):
        list_view = NoticeListView()
        list_view.request = self.request
        return list_view.get_queryset()
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["can_edit"] = hasattr(user, "nursery")

        body = self.object.body or ""
        body = body.replace("\r\n", "\n").replace("\r", "\n")
        body = body.lstrip(" \t　\n")
        body = re.sub(r'^(?:<br\s*/?>\s*)+', "", body, flags=re.IGNORECASE)

        ctx["body_clean"] = body

        return ctx 

# おたより新規投稿ページ
class NoticeCreateView(LoginRequiredMixin, CreateView):
    model= Notice
    form_class = NoticeForm
    template_name = 'notices/create.html'
    success_url = reverse_lazy('notices:list')

    def dispatch(self, request, *args, **kwargs):
        # 園以外は /create/ を開けないように
        if not hasattr(request.user, "nursery"):
            from django.http import Http404
            raise Http404
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.nursery = self.request.user.nursery
        return super().form_valid(form)

# おたより編集ページ
class NoticeUpdateView(LoginRequiredMixin, UpdateView):
    model = Notice
    form_class = NoticeForm
    template_name = 'notices/edit.html'
    success_url = reverse_lazy('notices:list')

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "nursery"):
            from django.http import Http404
            raise Http404
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Notice.objects.filter(nursery=self.request.user.nursery)
    
    def form_valid(self, form):
        form.instance.nursery = self.request.user.nursery
        return super().form_valid(form)