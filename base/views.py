from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q #this allows us search for more than just d topic name
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def loginUser(request):
    page = 'login'
    #once a user is logged in, he shouldn't be able to go to d login page manually again
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)

            if user is not None and user.check_password(password):
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid details.')

        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
# Put another try on line 24 to complement this exception on line 38
        except Exception as e:
            messages.error(request, f'Error occurred while logging in: {str(e)}')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


@csrf_protect
def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower() 
            user.save()
            login(request, user) 
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


@csrf_protect
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None   else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5] 
    context =  {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


@csrf_protect
def room(request, pk):
    room = Room.objects.get(id = pk)
    #to get all child properties in a many to one, varible.nameOfChildModel_set.all(), many2many is just .all()
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    #do not allow user to send message without login
    if request.method == 'POST' and not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST' and request.user:
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@csrf_protect
@login_required(login_url='login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    room_messages = user.message_set.all()
    topics = Topic.objects.all()[0:5]
    rooms = user.room_set.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@csrf_protect
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm() 
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@csrf_protect
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed to edit this!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.host = request.user
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@csrf_protect
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@csrf_protect
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@csrf_protect
@login_required(login_url='login')
def updateUser(request, user):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update_user.html', {'form': form})

@csrf_protect
def mobileTopics(request):
    q = request.GET.get('q') if request.GET.get('q') != None   else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/mobile_topics.html', {'topics': topics})

@csrf_protect
def mobileActivity(request):
    room_messages = Message.objects.all()
    return render(request, 'base/mobile_activity.html', {'room_messages': room_messages})
