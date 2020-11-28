from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserRegisterForm
from .models import lkpRole


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            role = request.user.role
            if str(role) == "Student":
                context = {}
                return render(request, 'soi_app/home_student.html', context)
            elif str(role) == "Professor":
                context = {}
                return render(request, 'soi_app/home_professor.html', context)
            else:
                return render(request, 'soi_app/index.html')
    else:
        print("User is not authenticated!")
        return render(request, 'soi_app/index.html')


def register(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.role = lkpRole.objects.get(name="Student")
            instance.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account created for ' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'soi_app/register.html', context)
