from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import math
from django.template import loader
from .models import stu

# Create your views here.
def hello(request):
    return HttpResponse("Hello World")

def dt(request):
    dt = datetime.now()
    msg = "unknown"
    if dt.hour < 12 :
        msg = "Good Morning Today's date & time : %s" %dt
    elif dt.hour <= 16 & dt.hour > 12 :
        msg = "Good Afternoon"
    else:
        msg = "Good Evevning"
    return HttpResponse(msg)

def welcome(request):
    temp = loader.get_template('demohtmlpage.html')
    # student = {"name" : "Rahul", "id" : 1, "age" : 23, "city" : "Mumbai"}
    s1 = {"name" : "Rahul", "id" : 1, "age" : 23, "address" : "Mumbai"}
    s2 = {"name" : "Kartik", "id" : 2, "age" : 24, "address" : "Mulshi"}
    s3 = {"name" : "Pratik", "id" : 3, "age" : 24, "address" : "Kokan"}

    dt = datetime.now()
    msg = "unknown"
    if dt.hour < 12 :
        msg = "Good Morning "
    elif dt.hour <= 16 & dt.hour > 12 :
        msg = "Good Afternoon"
    else:
        msg = "Good Evevning"

    student = {'sdict' : [s1,s2,s3], "greeting" : msg, "number" : 3}

    return HttpResponse(temp.render(student,request))

def navbar(request):
    temp = loader.get_template('menu.html')
    return HttpResponse(temp.render())

def navbar2(request):
    temp = loader.get_template('menu2.html')
    return HttpResponse(temp.render())

def form(request):
    if request.method == "GET":
        return render(request, "form.html")
    elif request.method == "POST":
        firstname = request.POST.get("name")
        email = request.POST.get("email")
        phoneno = request.POST.get("phoneno") 

        stuobj = stu(name=firstname, email=email, phoneno=phoneno)
        stuobj.save()
        return HttpResponse("registration successful")
        

def display(request):
    if request.method == "GET":
        stuobj = stu.objects.all()
        return render(request,'display.html', {"sob": stuobj})
    
def edit(request,id):
    if request.method == "GET":
        stuobj = stu.objects.get(id=id)
        return render(request, 'update.html', {"student" : stuobj})

    elif request.method == "POST":
        sid = request.POST.get('id')
        stuobj = stu.objects.get(id=sid)

        firstname = request.POST.get("name")
        email = request.POST.get("email")
        phoneno = request.POST.get("phoneno") 
        stuobj.name = firstname
        stuobj.email = email
        stuobj.phoneno = phoneno
        stuobj.save()
        # return render(request,'showupdated.html', {"sob": stuobj})
        # return HttpResponse(request, 'display.html')
        stuobj2 = stu.objects.all()
        return render(request,'display.html', {"sob": stuobj2})
        

def delete(request, id):
    if request.method == "GET":
        stuobj = stu.objects.get(id=id)
        stuobj.delete()
        # return HttpResponse("Data deleted successfully")
        stuobj1 = stu.objects.all()
        return render(request,'display.html', {"sob": stuobj1})