from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404
from django.db.models import Q

from .models import (
    Profile, SkillCategory, Experience, Project,
    Education, ContactMessage, SiteVisitor,
)
from .forms import ContactForm, ProfileForm, UserCreateForm, UserUpdateForm


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_visitor(request, page='home'):
    SiteVisitor.objects.create(
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
        page=page,
    )


def home(request):
    # log_visitor(request, 'home')
    profile = Profile.objects.filter(is_active=True).first()
    return render(request, 'portfolio/home.html', {
        'profile': profile,
        'skills': SkillCategory.objects.prefetch_related('skills').all(),
        'experiences': Experience.objects.filter(is_active=True),
        'projects': Project.objects.filter(is_active=True),
        'education': Education.objects.all(),
        'contact_form': ContactForm(),
    })


def contact_submit(request):
    if request.method != 'POST':
        return redirect('home')

    form = ContactForm(request.POST)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.ip_address = get_client_ip(request)
        contact.save()

        recipient = settings.CONTACT_RECIPIENT_EMAIL
        body = (
            f"New contact message from your portfolio\n\n"
            f"Name: {contact.name}\n"
            f"Email: {contact.email}\n"
            f"Subject: {contact.subject}\n\n"
            f"Message:\n{contact.message}\n"
        )
        try:
            send_mail(
                subject=f'Portfolio Contact: {contact.subject}',
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            messages.success(request, 'Thank you! Your message has been sent successfully.')
        except Exception:
            messages.warning(
                request,
                'Message saved. Email delivery failed — check SMTP settings in .env',
            )
    else:
        messages.error(request, 'Please correct the errors in the contact form.')

    return redirect('home')


def download_resume(request):
    profile = Profile.objects.filter(is_active=True).first()
    if not profile or not profile.resume:
        raise Http404('Resume not available')
    return redirect(profile.resume.url)


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(login_required(view_func))


@staff_required
def dashboard(request):
    return render(request, 'portfolio/dashboard/index.html', {
        'message_count': ContactMessage.objects.filter(is_read=False).count(),
        'visitor_count': SiteVisitor.objects.count(),
        'user_count': User.objects.count(),
        'project_count': Project.objects.count(),
        'recent_messages': ContactMessage.objects.all()[:5],
        'recent_visitors': SiteVisitor.objects.all()[:5],
    })


@staff_required
def manage_profile(request):
    profile = Profile.objects.first()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'portfolio/dashboard/profile_form.html', {'form': form})


@staff_required
def message_list(request):
    messages_qs = ContactMessage.objects.all()
    q = request.GET.get('q', '')
    if q:
        messages_qs = messages_qs.filter(
            Q(name__icontains=q) | Q(email__icontains=q) | Q(subject__icontains=q)
        )
    return render(request, 'portfolio/dashboard/message_list.html', {
        'messages_list': messages_qs,
        'q': q,
    })


@staff_required
def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save(update_fields=['is_read'])
    return render(request, 'portfolio/dashboard/message_detail.html', {'msg': msg})


@staff_required
def message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        msg.delete()
        messages.success(request, 'Message deleted.')
        return redirect('message_list')
    return render(request, 'portfolio/dashboard/confirm_delete.html', {
        'object': msg,
        'cancel_url': 'message_list',
    })


@staff_required
def visitor_list(request):
    visitors = SiteVisitor.objects.all()
    return render(request, 'portfolio/dashboard/visitor_list.html', {'visitors': visitors})


@staff_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'portfolio/dashboard/user_list.html', {'users': users})


@staff_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'portfolio/dashboard/user_form.html', {
        'form': form,
        'title': 'Add User',
    })


@staff_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'portfolio/dashboard/user_form.html', {
        'form': form,
        'title': f'Edit {user.username}',
    })


@staff_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted.')
        return redirect('user_list')
    return render(request, 'portfolio/dashboard/confirm_delete.html', {
        'object': user,
        'cancel_url': 'user_list',
    })


# Generic CRUD helpers for Experience, Project, Education
CRUD_CONFIG = {
    'experience': (Experience, ['company', 'role', 'location', 'start_date', 'end_date', 'description', 'order', 'is_active']),
    'project': (Project, ['title', 'description', 'tech_stack', 'github_url', 'live_url', 'image', 'order', 'is_active']),
    'education': (Education, ['degree', 'institution', 'period', 'order']),
}


@staff_required
def crud_list(request, model_name):
    model, _ = CRUD_CONFIG[model_name]
    items = model.objects.all()
    return render(request, 'portfolio/dashboard/crud_list.html', {
        'items': items,
        'model_name': model_name,
        'model_verbose': model._meta.verbose_name_plural,
    })


@staff_required
def crud_create(request, model_name):
    model, fields = CRUD_CONFIG[model_name]
    if request.method == 'POST':
        data = {f: request.POST.get(f) for f in fields if f not in ('image', 'is_active')}
        if 'is_active' in fields:
            data['is_active'] = request.POST.get('is_active') == 'on'
        if 'order' in data and data['order']:
            data['order'] = int(data['order'])
        if 'image' in fields and request.FILES.get('image'):
            data['image'] = request.FILES['image']
        obj = model.objects.create(**{k: v for k, v in data.items() if v is not None and v != ''})
        if 'order' in fields and not data.get('order'):
            obj.order = 0
            obj.save()
        messages.success(request, f'{model._meta.verbose_name} created.')
        return redirect('crud_list', model_name=model_name)
    return render(request, 'portfolio/dashboard/crud_form.html', {
        'model_name': model_name,
        'fields': fields,
        'title': f'Add {model._meta.verbose_name}',
        'field_values': {},
    })


@staff_required
def crud_edit(request, model_name, pk):
    model, fields = CRUD_CONFIG[model_name]
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        for f in fields:
            if f == 'is_active':
                setattr(obj, f, request.POST.get('is_active') == 'on')
            elif f == 'image':
                if request.FILES.get('image'):
                    setattr(obj, f, request.FILES['image'])
            elif f == 'order':
                val = request.POST.get(f)
                setattr(obj, f, int(val) if val else 0)
            else:
                setattr(obj, f, request.POST.get(f, ''))
        obj.save()
        messages.success(request, f'{model._meta.verbose_name} updated.')
        return redirect('crud_list', model_name=model_name)
    field_values = {f: getattr(obj, f, '') for f in fields}
    return render(request, 'portfolio/dashboard/crud_form.html', {
        'model_name': model_name,
        'fields': fields,
        'obj': obj,
        'field_values': field_values,
        'title': f'Edit {model._meta.verbose_name}',
    })


@staff_required
def crud_delete(request, model_name, pk):
    model, _ = CRUD_CONFIG[model_name]
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{model._meta.verbose_name} deleted.')
        return redirect('crud_list', model_name=model_name)
    return render(request, 'portfolio/dashboard/confirm_delete.html', {
        'object': obj,
        'cancel_url': 'crud_list',
        'cancel_kwargs': {'model_name': model_name},
    })

# ─────────────────────────────────────────────
#  AI CHATBOT — returns JSON reply server-side
#  API key stays on server, works on Vercel
# ─────────────────────────────────────────────
import json as _json
import os as _os
import urllib.request as _urllib_req
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decouple import config as _config

AJAY_SYSTEM_PROMPT = """
You are a friendly AI assistant on Ajay A's personal portfolio website.
Answer visitor questions warmly and concisely (2-4 sentences) using only the information below.
Never make up information. If you don't know something, say: "Please reach out to Ajay directly at ajayhkr2002@gmail.com"

=== ABOUT ===
Name: Ajay A
Title: Python Developer | Backend | Django | REST APIs
Location: Kochi, Kerala, India
Email: ajayhkr2002@gmail.com
Phone: +91 8270187897
GitHub: https://github.com/ajayhkr20
LinkedIn: https://linkedin.com/in/ajaycode
Summary: Python Developer with 1+ years of experience building backend systems, REST APIs,
and web applications using Python and Django. Skilled in PostgreSQL, SQL query optimization,
Docker, and Linux environments. Proficient in Django REST Framework, WebSockets, JWT
authentication, ORM, database design, and backend system optimization.

=== SKILLS ===
Languages: Python (primary), SQL, JavaScript
Frameworks: Django, Django REST Framework, Django Channels, React.js (basic)
Databases: PostgreSQL, MySQL, SQLite
Backend & APIs: REST API, WebSockets, JWT, Knox, RBAC, ORM, CRUD
DevOps & Tools: Docker, Git, GitHub, Linux, Postman, Render, VS Code

=== EXPERIENCE ===
1. Python Backend Developer (6-month contract) - STC Technologies, Kochi (Sep 2023 - Feb 2024)
   - Built 10+ REST APIs handling 300+ daily transactions for a financial domain platform
   - Optimized PostgreSQL queries, reducing API response time by 35%
   - Implemented Knox token authentication, secure file uploads, and RBAC
   - Used Git, code reviews, and production deployments on Linux/Docker

2. Python Django Developer - LCC Computer Education, Kochi (Oct 2022 - May 2023)
   - Built 5+ Django web applications for 50+ student users
   - Integrated scikit-learn ML modules for classification and prediction
   - Mentored 10+ students on Django and REST API design

=== PROJECTS ===
1. Financial Data Processing System - Python, Django REST Framework, PostgreSQL, Knox, Docker, Render
   40% performance improvement via query optimization. Secure Knox auth and RBAC endpoints.

2. Real-Time Chat Application - Python, Django Channels, WebSockets, Redis, MySQL, Render
   Supports 100+ concurrent users with Redis channel layer and persistent message history.

=== EDUCATION ===
- B.Sc Computer Science - Muslim Arts College, Manonmaniam Sundaranar University (2020-2023)
- Python Django Trainee Certification - Srishti Innovative Computer Systems Pvt. Ltd (Jul 2023 - Feb 2024)

=== AVAILABILITY ===
Open to full-time backend roles and freelance Django/Python projects.
For contact questions, always share the email ajayhkr2002@gmail.com and mention the contact form on this page.
""".strip()


@csrf_exempt
@require_POST
def chatbot_stream(request):
    """
    POST /chatbot/  { "messages": [{role, content}, ...] }
    Returns:        { "reply": "..." }
    Works on Vercel (no streaming needed).
    """
    try:
        body = _json.loads(request.body)
        chat_messages = body.get('messages', [])
        if not chat_messages:
            return JsonResponse({'error': 'No messages provided'}, status=400)
    except (_json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    api_key = _config('ANTHROPIC_API_KEY', default=_os.environ.get('ANTHROPIC_API_KEY', ''))
    if not api_key:
        return JsonResponse({'error': 'ANTHROPIC_API_KEY not configured on server'}, status=500)

    payload = _json.dumps({
        'model': 'claude-haiku-4-5-20251001',
        'max_tokens': 400,
        'system': AJAY_SYSTEM_PROMPT,
        'messages': chat_messages[-10:],
    }).encode('utf-8')

    req = _urllib_req.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
        },
        method='POST',
    )
    try:
        with _urllib_req.urlopen(req, timeout=30) as resp:
            data = _json.loads(resp.read().decode('utf-8'))
            reply = ''.join(
                block.get('text', '')
                for block in data.get('content', [])
                if block.get('type') == 'text'
            )
            return JsonResponse({'reply': reply})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=502)