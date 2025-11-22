from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SchoolGrowthLogForm
from .models import SchoolGrowthLog 

class SchoolGrowthLogCreateView(LoginRequiredMixin, CreateView):
    model = SchoolGrowthLog
    form_class = SchoolGrowthLogForm
    template_name = 'schoollogs/school_growthlog_form.html'
    success_url = reverse_lazy('schholloogs:school_growthlog_create')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = date.today()
        return initial
