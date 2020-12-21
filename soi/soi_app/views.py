from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, GroupCreationForm, StudentAddGroupForm
from .models import lkpRole, Group, User
from django.views.decorators.cache import never_cache


# Create your views here.
@never_cache
def index(request):
    if request.user.is_authenticated:

        if request.method == 'GET':
            role = request.user.role

            if str(role) == "Student":
                form = StudentAddGroupForm()
                queryset = Group.objects.filter(users=request.user)
                context = {"object_list": queryset, "form": form}
                return render(request, 'soi_app/home_student.html', context)

            elif str(role) == "Professor":
                form = GroupCreationForm()
                queryset = Group.objects.filter(users=request.user)
                context = {"object_list": queryset, "form": form}
                return render(request, 'soi_app/home_professor.html', context)

            else:
                return render(request, 'soi_app/index.html')

        if request.method == 'POST':
            role = request.user.role

            if str(role) == 'Professor':
                form = GroupCreationForm(request.POST)

                if form.is_valid():
                    form.save()
                    instance = form.save(commit=False)
                    instance.users.add(request.user)
                    instance.save()
                    group_name = form.cleaned_data.get('name')
                    messages.success(request, 'Created group ' + group_name)
                    return redirect('index')

            if str(role) == 'Student':
                form = StudentAddGroupForm(request.POST)
                if form.is_valid():
                    group_code = form.cleaned_data.get('code')
                    current_group = Group.objects.filter(code=group_code).first()

                    if current_group is None:
                        messages.warning(request, 'Group with code ' + group_code + 'does not exist')
                        return redirect('index')
                    else:
                        user = request.user
                        user.save()
                        current_group.users.add(user)
                        current_group.save()
                        messages.success(request, 'User added to group!')
                        return redirect('index')
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


def group(request, code):

    if request.method == 'GET':
        role = request.user.role

        if str(role) == 'Professor':
            query = Group.objects.filter(code=code, users=request.user).first()
            if query:
                context = {"object_list": query}
                return render(request, 'soi_app/group_professor.html', context)
            else:
                messages.warning(request, 'Wrong group code')
                return render(request, 'soi_app/index.html')

        if str(role) == 'Student':
            query = Group.objects.filter(code=code, users=request.user).first()
            if query:
                context = {"object_list": query}
                return render(request, 'soi_app/group_student.html', context)
            else:
                messages.warning(request, 'Wrong group code')
                return render(request, 'soi_app/index.html')


