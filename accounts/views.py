from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View
from .forms import EmailAuthenticationForm

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
            return redirect('home')
        return render(request, self.template_name,{'form':form})
    
        