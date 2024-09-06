from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from .models import Room, Topic, Message, User
from . forms import RoomForm, UserForm, MyUserCreationForm

def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request=request, message="User does not exist")

        user = authenticate(request=request, email=email, password=password)
        if user is not None:
            login(request=request, user=user)
            return redirect('home')
        else:
            messages.error(request=request, message="Email OR password does not exist")
    context = {"page": page}
    return render(request=request, template_name='base/login_register.html', context=context)

def logoutUser(request):
    logout(request=request)
    return redirect('home')

def registerPage(request):
    page = "register"

    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request=request, user=user)
            return redirect('home')
        else:
            messages.error(request=request, message="An error occured during registration")

    context = {'page': page, 'form': form}
    return render(request=request, template_name='base/login_register.html', context=context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__contains=q) |
        Q(description__contains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, "topics": topics, "room_count": room_count, 'room_messages': room_messages}
    return render(request=request, template_name='base/home.html', context=context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, "room_messages": room_messages, 'participants': participants}
    return render(request=request, template_name='base/room.html', context=context)

def activityPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    room_messages = Message.objects.filter(room__topic__name__icontains=q)
    context = {"room_messages": room_messages}
    return render(request=request, template_name='base/activity.html', context=context)

def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request=request, template_name='base/topics.html', context=context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    rooms = user.room_set.all()
    context = {"user": user, "rooms":rooms, 'room_messages': room_messages, "topics":  topics}
    return render(request=request, template_name='base/profile.html', context=context)

@login_required(login_url='login')
def createRoom(request):
    page = "create"
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # form = RoomForm(request.POST)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            price = request.POST.get('price'),
            image = request.FILES['image'],
            description = request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, "topics": topics, "page": page}
    return render(request=request, template_name='base/room_form.html', context=context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form =  RoomForm(instance=room)
    
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here!!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.host = request.user
        room.topic = topic
        room.name = request.POST.get('name')
        room.price = request.POST.get('price')
        if request.POST.get("image"):
            room.image = request.FILES.get('image')
            
        room.description = request.POST.get('description')

        room.save()
        return redirect('home')

    context = {"form": form, "topics": topics, "room": room}
    return render(request=request, template_name='base/room_form.html', context=context)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("You are not allowed here!!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request=request, template_name='base/delete.html', context={"obj": room})

@login_required(login_url='/login')
def deleteMessage(request, pk):
    room_message = Message.objects.get(id=pk)

    if request.user != room_message.user:
        return HttpResponse("You are not allowed here!!")
    if request.method == 'POST':
        room_message.delete()
        return redirect('home')
    return render(request=request, template_name='base/delete.html', context={'obj': room_message})



@login_required(login_url='/login')
def updateUser(request):
    form = UserForm(instance=request.user)
    context = {"form": form}
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=request.user.id)
    return render(request=request, template_name='base/edit-user.html', context=context)