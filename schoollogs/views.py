from decimal import Decimal
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SchoolGrowthLogForm
from .models import SchoolGrowthLog 

class SchoolGrowthLogCreateView(LoginRequiredMixin, CreateView):
    model = SchoolGrowthLog
    form_class = SchoolGrowthLogForm
    template_name = 'growthlogs/school_growthlog_form.html'
    success_url = reverse_lazy('growthlogs:school_growthlog_form')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = date.today()
        initial.setdefault("temperature", Decimal("36.5"))
        return initial
