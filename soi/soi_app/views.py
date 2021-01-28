from time import timezone

from django.contrib import messages
from django.db.models import F
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, GroupCreationForm, StudentAddGroupForm, TaskCreationForm, SubmitSolutionForm
from .forms import TaskInputOutputForm
from .models import lkpRole, Group, Task, TaskInputOutput, Results
from django.views.decorators.cache import never_cache
from solutions import *

from django.http import HttpResponseRedirect
import datetime
import collections
import pytz

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from django.http import HttpResponseRedirect


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


def update_group(request, group_id):
    group_id = int(group_id)
    try:
        group_sel = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return redirect('index')
    # group_form = GroupCreate(request.POST or None, instance = group_sel)
    group_form = GroupCreationForm(request.POST, instance=group_sel)
    if group_form.is_valid():
        group_form.save()
        # group_name = group_sel.cleaned_data.get('name')
        return redirect('index')
    return render(request, 'soi_app/group.html', {'upload_form': group_form})


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

def is_greater_equal_date_now(year, month, day,  year_now, month_now, day_now):
    if (year < year_now): return  1
    elif (year == year_now and month < month_now ): return  1
    elif (year == year_now and month == month_now and day < day_now): return  1
    elif (year == year_now and month == month_now and day == day_now): return  1
    else: return 0

def is_greater_date_now(year, month, day,  year_now, month_now, day_now):
    if (year < year_now): return  1
    elif (year == year_now and month < month_now ): return  1
    elif (year == year_now and month == month_now and day < day_now): return  1
    else: return 0

def is_equal(year, month, day, year_now, month_now, day_now):

    if (year == year_now and month == month_now and day == day_now): return  1
    else: return 0

def group(request, code):
    form = TaskCreationForm()
    if request.method == 'GET':
        role = request.user.role

        if str(role) == 'Professor':
            query = Group.objects.filter(code=code, users=request.user).first()
            all_tasks = Task.objects.filter(group=query.id)
            all_users = query.users.all()
            all_students = []
            for i in range(len(all_users)):
                if(all_users[i].role.name == "Student"):
                    all_students.append({
                        'username' : all_users[i].username,
                        'id' : all_users[i].id,
                        'group_id' : query.id,
                    })
            
            query1 = Group.objects.get(code=code)
            form = TaskCreationForm(initial={'group': query1})

            if query:
                context = {"object_list": query, "form": form, "all_tasks": all_tasks, "all_users": all_users,"all_students" : all_students}
                return render(request, 'soi_app/group_professor.html', context)
            else:
                messages.warning(request, 'Wrong group code')
                return render(request, 'soi_app/index.html')

        if str(role) == 'Student':
            current_group = Group.objects.get(code=code)
            all_tasks = Task.objects.filter(group=current_group.id)
            now = datetime.datetime.now().replace(microsecond=0)

            all_tasks_list = []
            for current_task in all_tasks:
                now = datetime.datetime.now()
                utc = pytz.UTC

                current_task_started_at = current_task.started_at.replace(tzinfo=utc)

                current_task_visible = current_task.visible.replace(tzinfo=utc)
                current_time = now.replace(tzinfo=utc)

                started_time = datetime.datetime.strptime(str(current_task_started_at), '%Y-%m-%d %H:%M:%S%z')
                started_time = datetime.time(started_time.hour, started_time.minute, started_time.second)

                visible_time = datetime.datetime.strptime(str(current_task_visible), '%Y-%m-%d %H:%M:%S%z')
                visible_time = datetime.time(visible_time.hour, visible_time.minute, visible_time.second)

                now_time = datetime.datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S.%f%z')
                now_time = datetime.time(now_time.hour, now_time.minute, now_time.second)

                current_is_bigger_started = is_greater_equal_date_now(current_task_started_at.year,
                                                                current_task_started_at.month,
                                                                current_task_started_at.day,
                                                                current_time.year,
                                                                current_time.month,
                                                                current_time.day)

                current_is_bigger_visible = is_greater_date_now(current_task_visible.year,
                                                                 current_task_visible.month,
                                                                 current_task_visible.day,
                                                                 current_time.year,
                                                                 current_time.month,
                                                                 current_time.day)

                equal_visible_now = is_equal(current_task_visible.year,
                                              current_task_visible.month,
                                              current_task_visible.day,
                                              current_time.year,
                                              current_time.month,
                                              current_time.day)

                equal_started_now = is_equal(current_task_started_at.year,
                                             current_task_started_at.month,
                                             current_task_started_at.day,
                                             current_time.year,
                                             current_time.month,
                                             current_time.day)


                if (current_is_bigger_started == 1 and current_is_bigger_visible == 0):
                    if (equal_started_now == 1):
                        if (started_time < now_time):
                            submit = 1
                        else:
                            submit = 0

                    if (equal_visible_now == 1):
                        if (visible_time < now_time):
                            submit = 0
                        else:
                            submit = 1


                    if (equal_started_now == 0 and equal_visible_now == 0):
                        submit = 1
                else:
                    submit = 0

                if (submit == 1): all_tasks_list.append(current_task)


            if current_group:
                context = {"current_group": current_group, "all_tasks": all_tasks_list, "current_time": now}
                return render(request, 'soi_app/group_student.html', context)
            else:
                messages.warning(request, 'Wrong group code')
                return render(request, 'soi_app/index.html')

    if request.method == 'POST':
        form = TaskCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            instance = form.save(commit=False)
            instance.group = Group.objects.filter(code=code, users=request.user).first()
            instance.save()
            task_name = form.cleaned_data.get('name')
            messages.success(request, 'Task ' + task_name + ' created!')
            return render(request, 'soi_app/index.html')





def task(request, code, task_id):
    # form = TaskCreationForm()
    if request.method == 'GET':
        role = request.user.role
        if str(role) == 'Professor':
            current_task = Task.objects.filter(id=task_id).first()

            # Popuni formu sa vrijednostima iz current_task kverija.
            form = TaskCreationForm(instance=current_task)

            # Drugi nacin da popunimo samo neke vrijednosti.
            # form = TaskCreationForm(initial={'name': current_task.name, 'description': current_task.description})
            context = {'form': form, 'current_task': current_task}
            return render(request, 'soi_app/task_professor.html', context)

        if str(role) == 'Student':
            solution_form = SubmitSolutionForm()
            current_task = Task.objects.get(id=task_id)

            now = datetime.datetime.now()
            utc = pytz.UTC
            current_task_started_at = current_task.started_at.replace(tzinfo=utc)
            current_task_finished_at = current_task.finished_at.replace(tzinfo=utc)
            current_time = now.replace(tzinfo=utc)

            started_time = datetime.datetime.strptime(str(current_task_started_at), '%Y-%m-%d %H:%M:%S%z')
            started_time = datetime.time(started_time.hour, started_time.minute, started_time.second)

            finished_time = datetime.datetime.strptime(str(current_task_finished_at), '%Y-%m-%d %H:%M:%S%z')
            finished_time = datetime.time(finished_time.hour, finished_time.minute, finished_time.second)

            now_time = datetime.datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S.%f%z')
            now_time = datetime.time(now_time.hour, now_time.minute, now_time.second)

            current_is_bigger_started = is_greater_equal_date_now(current_task_started_at.year,
                                                            current_task_started_at.month,
                                                            current_task_started_at.day,
                                                            current_time.year,
                                                            current_time.month,
                                                            current_time.day)

            current_is_bigger_finished = is_greater_date_now(current_task_finished_at.year,
                                                             current_task_finished_at.month,
                                                             current_task_finished_at.day,
                                                             current_time.year,
                                                             current_time.month,
                                                             current_time.day)

            equal_finished_now = is_equal(current_task_finished_at.year,
                                                             current_task_finished_at.month,
                                                             current_task_finished_at.day,
                                                             current_time.year,
                                                             current_time.month,
                                                             current_time.day)

            equal_started_now = is_equal(current_task_started_at.year,
                                          current_task_started_at.month,
                                          current_task_started_at.day,
                                          current_time.year,
                                          current_time.month,
                                          current_time.day)

            if (current_is_bigger_started == 1 and current_is_bigger_finished == 0):
                if (equal_started_now == 1):
                    if (started_time < now_time):
                        submit = 1
                    else:
                        submit = 0

                if (equal_finished_now == 1):
                    if (finished_time < now_time):
                        submit = 0
                    else:
                        submit = 1


                if (equal_started_now == 0 and equal_finished_now == 0):
                    submit = 1
            else:
                submit = 0

            context = {'solution_form': solution_form, 'current_task': current_task, "sumbit": submit}
            return render(request, 'soi_app/task_student.html', context)

    if request.method == 'POST':
        solution_form = SubmitSolutionForm(request.POST)
        role = request.user.role
        if str(role) == 'Student':
            #selectovat vrijeme i poredit
            if solution_form.is_valid():
                # TODO Student mora dat naziv funkcije ovako:
                # <user_id>_fun dat cemo mu user id ili ispunit formu sa tamplate!
                # Rijesi i problem ako submita dva puta ili napravi da je moguce submit samo jednom
                # nakon toga da je readonly njegova funkcija

                f = open("solutions.py", "a+")
                submitted_fun = solution_form.cleaned_data.get('solution')

                # Ime funkcije proslijedi u context
                try:
                    submitted_fun_name = submitted_fun.split('(')[0].split(' ')[1]
                except Exception as e:
                    messages.warning(request, 'Syntax error!')
                    return HttpResponseRedirect(request.path_info)
                else:
                    pass

                if check_syntax(submitted_fun) == 1:
                    f.write('\n')
                    f.write('\n')
                    f.write(submitted_fun)
                    messages.success(request, 'Solution submitted! ' + submitted_fun_name)
                    context = {'submitted_fun_name': submitted_fun_name, 'task_id': task_id}
                    return render(request, 'soi_app/solution_student.html', context)
                else:
                    messages.warning(request, 'Syntax error! ' + submitted_fun_name)
                    return HttpResponseRedirect(request.path_info)
                    # return render(request, 'soi_app/index.html')

                #### OVAJ DIO IDE NA DRUGU RUTU I IZVRSAVA SE NAKON STO SE KLIKNE VALIDATE####
                #### ruta treba primati ime nove funkcije dole submitted_fun_name i izvristi je####
                #### nakon toga porediti rezultate sa outputom i dati bodove u zavisnosti koliko ####
                #### rjesenja je tacno ####
                # input_output = TaskInputOutput.objects.only('input').filter(task=task_id)
                # Selektujem sve inpute iz baze, pretvorim ih u int i proslijedim funkciji eval
                # Selektujemo inpute kao string npr ako je u bazi 10,20 selektovat cemo 10,20
                # ovo bi trebalo raditi za 1 i vise parametara kad funkcija prima int
                input_test = TaskInputOutput.objects.filter(task=task_id).values_list('input', flat=True)
                user_id = request.user.id

                for input in input_test:
                    # Za svaki input kreiraj listu intova
                    my_list_int = [int(item) for item in input.split(',')]

                    # Ovako za inpute koji su int i string, za niz probaj
                    # if item[0] == '['
                    # for item in input.split(','):
                    #    if item[0] == '"':
                    #        my_generic_list.append(str(item))
                    #    else:
                    #        my_list_generic.append(int(item))

                    # Proslijedi ime funkcije i u njemu argumente iz liste
                    fun_name = submitted_fun_name + '(*my_list_int)'
                    # fun_name = 'fun2_' + str(user_id) + '(*my_list_int)'

                    # Pokreni funkciju iz solutions.py tako sto eval proslijeidmo njeno ime
                    user_output = eval(fun_name)

                    # Upisi dobijene rezultate u results.txt
                    # TODO ovaj reults mora imati jedinstveno ime npr id_zad_results
                    # TODO dodaji ove fajlove u neki folder
                    f2 = open('results.txt', 'a+')
                    f2.write('\n')
                    f2.write(str(user_output))
                # TODO uzmi output iz baze i poredi id_zad_results sa outputom i dodjeljuj score
                # TODO 1 Probaj da das tip svakom parametru na sistemu npr 10,"benjo",[1,2,3] i pored
                # TODO 1 polje u koji se unosi int,str,list. tako da my_list na liniji 172 mozes napraviti
                # TODO 1 generickom i proslijediti dalje, prvo testira radi li ovo:
                # TODO 1 my_list_int = [10,"benjo"] i prosjeldi je u eval kao *my_lust_int
                # radi
                # for input in input_output:
                #    input = int(input)
                #    fun_name = 'fun2_' + str(user_id) + '(input)'
                #    user_output = eval(fun_name)

                # output = fun2(5)
                context = {'output': user_output}
                messages.success(request, "Solution submitted!")
                return render(request, 'soi_app/task_student.html', context)


def validate_solution(request, task_id, fun_name):
    if request.method == 'GET':
        # messages.success(request, task_id + ' ' + fun_name)
        input_test = TaskInputOutput.objects.filter(task=task_id).values_list('input', flat=True)
        user_full_output = []
        file_name = task_id + fun_name + '.txt'
        fun_name = fun_name + '(*my_generic_list)'
        score = 0

        for input in input_test:
            my_generic_list = []
            for item in input.split(','):
                if item[0] == '"':
                    item_sliced = item[1:len(item) - 1]
                    my_generic_list.append(str(item_sliced))
                    # kod iznad treba rijesiti problem da se fji prosliejdi "abc"
                    # sa navodnicima tj string iz baze koji ima i navodnike
                    # my_generic_list.append(str(item))
                elif item[0] == '[':
                    temp_list = []
                    # [10;20;30] -> 10;20;30
                    item_sliced = item[1:len(item) - 1]
                    for list_element in item_sliced.split(';'):
                        # Provjerava da li je element list int ili string
                        if list_element[0] == '"':
                            list_element_sliced = list_element[1:len(list_element) - 1]
                            temp_list.append(str(list_element_sliced))
                        else:
                            temp_list.append(int(list_element))
                    my_generic_list.append(temp_list)
                else:
                    my_generic_list.append(int(item))

            user_output = eval(fun_name)

            user_full_output.append(user_output)
            f = open(file_name, 'a+')
            f.write('\n')
            f.write(str(user_output))

        user_full_output.sort()
        output_test = TaskInputOutput.objects.filter(task=task_id).values_list('output', flat=True)
        output_test_list = []
        for output in output_test:
            if output[0] == '"':
                output_sliced = output[1:len(output) - 1]
                output_test_list.append(str(output_sliced))
                # output_test_list.append(str(output))
            else:
                output_test_list.append(int(output))

            output_test_list.sort()

            # Provjeravamo da li je output iz baze jednak outputu usera.
            # Ako jeste zadatak je tacan
            # TODO: Provjeri sve vrijednosti ako npr. postoje 4 outputa, a user ima 3 tacna dobija 0.75 bodova
            # TODO: output_test_list moze biti i double ne samo int!
            # TODO: u solutions.py treba biti omogucen unos importa ?
            if collections.Counter(user_full_output) == collections.Counter(output_test_list):
                score = 1
            else:
                score = 0

        # Add score into db
        if not Results.objects.filter(task=task_id, user=request.user).exists():
            result = Results()
            result.task = Task.objects.filter(id=task_id).first()
            result.user = request.user
            result.score = score
            result.save()
        else:
            current_result = Results.objects.filter(task=task_id, user=request.user).update(score=score)

        if score == 1:
            messages.success(request, 'Solution accpeted! ' + str(user_full_output))
            return render(request, 'soi_app/index.html')
        else:
            messages.warning(request, 'Solution rejected! ' + str(user_full_output))
            return render(request, 'soi_app/index.html')



def input_output(request, task_id):
    form = TaskInputOutputForm()
    if request.method == 'GET':
        role = request.user.role
        if str(role) == 'Professor':
            current_task = Task.objects.filter(id=task_id).first()
            query = Group.objects.filter(task=task_id).first()
             #query = Group.objects.filter(code=code, users=request.user).first()
            context = {'form': form, 'current_task': current_task, 'group':query}
            return render(request, 'soi_app/input_output.html', context)

    if request.method == 'POST':
        role = request.user.role

        if str(role) == 'Professor':
            form = TaskInputOutputForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.task = Task.objects.get(id=task_id)
                instance.save()
                messages.success(request, 'Input - Output created!')

                context = {'form': form}
                return render(request, 'soi_app/input_output.html', context)


# funckija koja provjerava ispravnost sintakse prilikom submita rjesenja zadatka
def check_syntax(code_string):
    output = list()
    try:
        tree = compile(code_string, 'mystr', 'exec')
    except Exception as e:
        # print(e)
        return 0
    else:
        # exec(tree)
        return 1


def update_group(request, group_id):
    group_id = int(group_id)
    try:
        group_sel = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return redirect('index')
    # group_form = GroupCreate(request.POST or None, instance = group_sel)
    group_form = GroupCreationForm(request.POST, instance=group_sel)
    if group_form.is_valid():
        group_form.save()
        # group_name = group_sel.cleaned_data.get('name')
        return redirect('index')
    return render(request, 'soi_app/group.html', {'upload_form': group_form})



def delete_group(request, group_id):
    group_id = int(group_id)
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return redirect('index')
    group.delete()
    return redirect('index')

def generate_report_user(request,user_id,group_id):
    user_id = int(user_id)
    group_id = int(group_id)

    data = [
        ['Ime', 'Prezime', 'Naziv grupe', 'Naziv zadatka', 'Uspjesnost' ],
    ]

    results = Results.objects.filter(user_id = user_id)
    
    suffix = ""
    group_name = ""
    for i in range(len(results)):
        temp_data = []
        temp_data.append(results[i].user.first_name)
        temp_data.append(results[i].user.last_name)
        temp_data.append(results[i].task.group.name)
        temp_data.append(results[i].task.name)
        temp_data.append(results[i].score)
        data.append(temp_data)
        group_name = results[i].task.group.name
        suffix = results[i].user.first_name + "_" + results[i].user.last_name

    parts_of_group_name = group_name.split(" ")
    if(len(parts_of_group_name) > 0):
        group_name = ""
        for i in range(len(parts_of_group_name)):
            group_name += parts_of_group_name[i]

    suffix += "_"
    suffix += group_name
    fileName = 'media/documents/' + suffix + ".pdf"
    pdf = SimpleDocTemplate(
    fileName,
    pagesize=letter
    )
    table = Table(data)
    style = TableStyle([
    ('BACKGROUND', (0,0), (3,0), colors.green),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),

    ('ALIGN',(0,0),(-1,-1),'CENTER'),

    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 14),

    ('BOTTOMPADDING', (0,0), (-1,0), 12),

    ('BACKGROUND',(0,1),(-1,-1),colors.beige),
    ])
    table.setStyle(style)

    # 2) Alternate backgroud color
    rowNumb = len(data)
    for i in range(1, rowNumb):
        if i % 2 == 0:
            bc = colors.burlywood
        else:
            bc = colors.beige
        
        ts = TableStyle(
            [('BACKGROUND', (0,i),(-1,i), bc)]
        )
        table.setStyle(ts)

    # 3) Add borders
    ts = TableStyle(
        [
        ('BOX',(0,0),(-1,-1),2,colors.black),

        ('LINEBEFORE',(2,1),(2,-1),2,colors.red),
        ('LINEABOVE',(0,2),(-1,2),2,colors.green),

        ('GRID',(0,1),(-1,-1),2,colors.black),
        ]
    )
    table.setStyle(ts)

    elems = []
    elems.append(table)

    pdf.build(elems)

    return HttpResponseRedirect("/"+fileName)

def generate_report_task(request,task_id):
    task_id = int(task_id)

    titles = ['Ime', 'Prezime', 'Naziv grupe', 'Naziv zadatka', 'Uspjesnost' ]
    data = [
        
    ]


    results = Results.objects.filter(task_id = task_id)
    
    suffix = ""
    group_name = ""
    task_name = ""
    for i in range(len(results)):
        temp_data = []
        temp_data.append(results[i].user.first_name)
        temp_data.append(results[i].user.last_name)
        temp_data.append(results[i].task.group.name)
        temp_data.append(results[i].task.name)
        temp_data.append(results[i].score)
        data.append(temp_data)
        group_name = results[i].task.group.name
        task_name = results[i].task.name

    data.sort(key=lambda x: x[4], reverse = True)
    data.insert(0,titles)

    parts_of_group_name = group_name.split(" ")
    if(len(parts_of_group_name) > 0):
        group_name = ""
        for i in range(len(parts_of_group_name)):
            group_name += parts_of_group_name[i]

    
    suffix += group_name
    suffix += "_"
    suffix += task_name

    fileName = 'media/documents/' + suffix + ".pdf"
    pdf = SimpleDocTemplate(
    fileName,
    pagesize=letter
    )
    table = Table(data)
    style = TableStyle([
    ('BACKGROUND', (0,0), (3,0), colors.green),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),

    ('ALIGN',(0,0),(-1,-1),'CENTER'),

    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 14),

    ('BOTTOMPADDING', (0,0), (-1,0), 12),

    ('BACKGROUND',(0,1),(-1,-1),colors.beige),
    ])
    table.setStyle(style)

    # 2) Alternate backgroud color
    rowNumb = len(data)
    for i in range(1, rowNumb):
        if i % 2 == 0:
            bc = colors.burlywood
        else:
            bc = colors.beige
        
        ts = TableStyle(
            [('BACKGROUND', (0,i),(-1,i), bc)]
        )
        table.setStyle(ts)

    # 3) Add borders
    ts = TableStyle(
        [
        ('BOX',(0,0),(-1,-1),2,colors.black),

        ('LINEBEFORE',(2,1),(2,-1),2,colors.red),
        ('LINEABOVE',(0,2),(-1,2),2,colors.green),

        ('GRID',(0,1),(-1,-1),2,colors.black),
        ]
    )
    table.setStyle(ts)

    elems = []
    elems.append(table)

    pdf.build(elems)

    return HttpResponseRedirect("/"+fileName)

    



