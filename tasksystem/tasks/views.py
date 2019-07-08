from django.shortcuts import render

# Create your views here.

# helper class to fetch different data according to user_type
class MemberRepository():
    pass

class ManagerRepository():
    pass

class TasksActivity():
    # this view 
    pass

class Tasks(ListCreateView):
    pass


# /tasks/private
class PrivateTasksView(ListView):
    # this view lists all the variations of private tasks and accepts extra queries 
    # eg /tasks/private?q=
    pass

class PublicTasksView(ListView):
    # this view lists all the variations of public tasks and accepts extra queries
    # eg /tasks/public?q=
    pass