from django.shortcuts import redirect, render
from .forms import * 
from django.contrib import messages
from django.views.generic import DetailView
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
	return render(request,'dashboard/home.html')

@login_required
def notes(request):
	if request.method == 'POST':
		form = NotesForm(request.POST)
		if form.is_valid():
			notes = Notes(user=request.user,title=request.POST['title'],desc=request.POST['desc'])
			notes.save()
			messages.success(request,f"Notes from {request.user.username} added successfully")
	else: 
		form = NotesForm()
	notes = Notes.objects.filter(user=request.user)
	context = {"notes":notes,"form":form}
	return render(request,'dashboard/notes.html',context)

@login_required
def delete_note(request,pk=None):
	Notes.objects.get(id=pk).delete()
	return redirect("notes")

class NotesDetailView(DetailView):
	model = Notes


@login_required
def homework(request):
	if request.method == 'POST':
		form = HomeworkForm(request.POST)
		if form.is_valid():
			try:
				finished = request.POST['is_finished']
				if finished == 'on':
					finished = True
				else:
					finished = False
			except:
				finished = False
			homeworks = Homework(
				user=request.user,
				subject = request.POST['subject'],
				title = request.POST['title'],
				desc = request.POST['desc'],
				due = request.POST['due'],
				is_finished = finished
			)		
			homeworks.save()
			messages.success(request,f"Homework added from {request.user.username}")
	else:
		form = HomeworkForm()
	homework = Homework.objects.filter(user= request.user)
	if len(homework) == 0:
		hw_done = True	
	else:
		hw_done = False
	context = {"homework":homework,"hw_done":hw_done,"form":form}
	return render(request,'dashboard/homework.html',context)
	
@login_required
def update_homework(request,pk=None):
	homework = Homework.objects.get(id=pk)
	if homework.is_finished==True:
		homework.is_finished = False
	else:
		homework.is_finished = True
	homework.save()
	return redirect('homework')

@login_required
def delete_homework(request,pk=None):
	Homework.objects.get(id=pk).delete()
	return redirect('homework')

@login_required
def youtube(request):
	if request.method == 'POST':
		form = DashboardForm(request.POST)
		text = request.POST['text']
		video = VideosSearch(text,limit=10)
		result_list = []
		for i in video.result()['result']:
			result_dict = {
			'input':text,
			'title':i['title'],
			'duration':i['duration'],
			'thumbnail': i['thumbnails'][0]['url'],
			'channel': i['channel']['name'],
			'link': i['link'],
			'viewCount': i['viewCount']['short'],
			'publishedTime': i['publishedTime'],
			}
			desc = ''
			if i['descriptionSnippet']:
				for k in i['descriptionSnippet']:
					desc+=k['text']
			result_dict['desc'] = desc
			result_list.append(result_dict)
		context = {"result": result_list,"form":form}
		return render(request,'dashboard/youtube.html',context)
	else:
		form = DashboardForm()
	search = DashboardForm()
	context = {"search":search}
	return render(request,'dashboard/youtube.html',context)


@login_required
def todo(request):
	if request.method == 'POST':
		form = TodoForm(request.POST)
		if form.is_valid():
			todo = Todo(
				user = request.user,
				title = request.POST['title']
			)
			todo.save()
			messages.success(request,f"Todo added from {request.user.username}")
	else:
		form = TodoForm()
	todo = Todo.objects.filter(user=request.user)
	if len(todo) == 0:
		empty = True
	else:
		empty = False
	context = {"Todo":todo,"form":form,"empty":empty}
	return render(request,"dashboard/todo.html",context)

@login_required
def update_todo(request,pk=None):
	todo = Todo.objects.get(id=pk)
	if todo.is_finished==True:
		todo.is_finished = False
	else:
		todo.is_finished = True
	todo.save()
	return redirect('todo')

@login_required
def delete_todo(request,pk=None):
	Todo.objects.get(id=pk).delete()
	return redirect('todo')


@login_required
def books(request):
	if request.method == 'POST':
		form = DashboardForm(request.POST)
		text = request.POST['text']
		#  Try catch required
		url = "https://www.googleapis.com/books/v1/volumes?q="+text;
		r = requests.get(url)
		ans = r.json()
		result_list = []
		for i in range(10):
			result_dict = {
			'title':ans['items'][i]['volumeInfo']['title'],
			'subTitle':ans['items'][i]['volumeInfo'].get('subtitle'),
			'desc':ans['items'][i]['volumeInfo'].get('description'),
			'count':ans['items'][i]['volumeInfo'].get('pageCount'),
			'categories':ans['items'][i]['volumeInfo'].get('categories'),
			'rating':ans['items'][i]['volumeInfo'].get('pageRating'),
			'thumbnail':ans['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
			'preview':ans['items'][i]['volumeInfo'].get('previewLink'),
			}
			result_list.append(result_dict)
		context = {"result": result_list,"form":form}
		return render(request,'dashboard/books.html',context)
	else:
		form = DashboardForm()
	search = DashboardForm()
	context = {"search":search}
	return render(request,'dashboard/books.html',context)



@login_required
def dictionary(request):
	if request.method == 'POST':
		form = DashboardForm(request.POST)
		text = request.POST['text']
		#  Try catch required
		url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text;
		r = requests.get(url)
		ans = r.json()
		try:
			phonetics = ans[0]['phonetics'][0]['text']
			audio = ans[0]['phonetics'][0]['audio']
			defintion = ans[0]['meanings'][0]['definitions'][0]['definition']
			example = ans[0]['meanings'][0]['definitions'][0]['example']
			synonyms = ans[0]['meanings'][0]['definitions'][0]['synonyms']
			context = {
			'form':form,
			'input'	: text,
			'audio': audio,
			'phonetics': phonetics,
			'defintion': defintion,
			'example': example,
			'synonyms': synonyms,
			}
		except:
			context = {"form":form,'input': ""}
		return render(request,"dashboard/dictionary.html",context)
	else:
		form = DashboardForm()
		context = {"form":form}
		return render(request,"dashboard/dictionary.html",context)

@login_required
def wiki(request):
	if request.method == 'POST':
		text = request.POST['text']
		form = DashboardForm(request.POST)
		# Try catch required
		search = wikipedia.page(text)
		context = {
		"form":form,
		'title'	: search.title,
		'link': search.url,
		'details': search.summary,
		}
		return render(request,"dashboard/wiki.html",context)
	else:
		form = DashboardForm()
		context = {"form":form}
		return render(request,"dashboard/wiki.html",context)

@login_required
def conversion(request):
	if request.method == 'POST':
		form = ConversionForm(request.POST)
		if request.POST['measurement'] == 'length':
			measurementForm = ConversionLengthForm()
			context = {
				'form': form,
				'm_form': measurementForm,
				'input': True,
			}
			if 'input' in request.POST:
				first = request.POST['measure1']
				second = request.POST['measure2']
				input = request.POST['input']
				ans = ''
				if input and int(input) >= 0:
					if first == 'yard' and second == 'foot':
						ans = f'{input} yard = {int(input)*3} foot'
					if first == 'foot' and second == 'yard':
						ans = f'{input} foot = {int(input)/3} yard'
				context = {"form":form,"m_form":measurementForm,"input":True,
				"ans": ans
				}
		if request.POST['measurement'] == 'mass':
			measurementForm = ConversionMassForm()
			context = {
				'form': form,
				'm_form': measurementForm,
				'input': True,
			}
			if 'input' in request.POST:
				first = request.POST['measure1']
				second = request.POST['measure2']
				input = request.POST['input']
				ans = ''
				if input and int(input) >= 0:
					if first == 'pound' and second == 'kilogram':
						ans = f'{input} pound = {int(input)*0.453592} kg'
					if first == 'kilogram' and second == 'pound':
						ans = f'{input} kg = {int(input)*2.20462} pound'
				context = {"form":form,"m_form":measurementForm,"input":True,
				"ans": ans
				}
	else: 
		form = ConversionForm()
		context = {"form":form,'input':False}
	return render(request,"dashboard/conversion.html",context)


def register(request):
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request,f"Account created for {username} successfully")
			return redirect('dashboard/login.html')
	else:
		form = UserRegistrationForm()
		context = {"form":form}
		return render(request,"dashboard/register.html",context)

@login_required
def profile(request):
	homeworks = Homework.objects.filter(is_finished=False,user=request.user)
	todos = Todo.objects.filter(is_finished=False,user=request.user)
	if len(homeworks) == 0:
		homeworks_done = True 
	else: 
		homeworks_done = False
	if len(todos) == 0:
		todos_done = True 
	else: 
		todos_done = False
	context = {
		"homeworks": homeworks,
		"todos": todos,
		"hw_done": homeworks_done,
		"td_done": todos_done,
	}
	return render(request,"dashboard/profile.html",context)