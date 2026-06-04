from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolio.models import Profile, SkillCategory, Skill, Experience, Project, Education


class Command(BaseCommand):
    help = 'Load initial portfolio data from resume'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'ajayhkr2002@gmail.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / admin123)'))

        profile, created = Profile.objects.get_or_create(
            pk=1,
            defaults={
                'name': 'Ajay A',
                'title': 'Python Developer | Backend | Django | REST APIs',
                'summary': (
                    'Python Developer with 1+ years of experience in building backend systems, '
                    'REST APIs, and web applications using Python and Django. Skilled in PostgreSQL, '
                    'SQL query optimization, Docker, and Linux environments. Experienced in developing '
                    'real-world financial and data-driven applications with clean, maintainable Python code. '
                    'Proficient in Django REST Framework, WebSockets, JWT authentication, ORM, database design, '
                    'and backend system optimization.'
                ),
                'email': 'ajayhkr2002@gmail.com',
                'phone': '+91 8270187897',
                'location': 'Kochi, Kerala',
                'github_url': 'https://github.com/ajayhkr20',
                'linkedin_url': 'https://linkedin.com/in/ajaycode',
            },
        )
        if created:
            self.stdout.write('Profile created')

        if not SkillCategory.objects.exists():
            categories = {
                'Languages': ['Python (primary)', 'SQL', 'JavaScript'],
                'Frameworks': ['Django', 'Django REST Framework', 'Django Channels', 'React.js (basic)'],
                'Databases': ['PostgreSQL', 'MySQL', 'SQLite'],
                'Backend & APIs': ['REST API', 'WebSockets', 'JWT', 'Knox', 'RBAC', 'ORM', 'CRUD'],
                'DevOps & Tools': ['Docker', 'Git', 'GitHub', 'Linux', 'Postman', 'Render', 'VS Code'],
            }
            for i, (cat_name, skills) in enumerate(categories.items()):
                cat = SkillCategory.objects.create(name=cat_name, order=i)
                for j, skill_name in enumerate(skills):
                    Skill.objects.create(category=cat, name=skill_name, order=j)
            self.stdout.write('Skills loaded')

        if not Experience.objects.exists():
            Experience.objects.create(
                company='STC Technologies',
                role='Python Backend Developer (6 months Contract)',
                location='Kochi, Kerala',
                start_date='Sep 2023',
                end_date='Feb 2024',
                order=0,
                description=(
                    'Developed a Python/Django backend for a financial domain platform, building 10+ REST APIs '
                    'handling 300+ daily transactions.\n'
                    'Optimized PostgreSQL queries and used ORM techniques (select_related, prefetch_related) '
                    'to reduce API response time by 35%.\n'
                    'Implemented Knox token authentication, secure file upload handling, and role-based access control (RBAC).\n'
                    'Collaborated using Git, participated in code reviews, and supported production deployments on Linux/Docker.'
                ),
            )
            Experience.objects.create(
                company='LCC Computer Education',
                role='Python Django Developer',
                location='Kochi, Kerala',
                start_date='Oct 2022',
                end_date='May 2023',
                order=1,
                description=(
                    'Built 5+ Python/Django web applications serving 50+ student users, focusing on authentication and CRUD workflows.\n'
                    'Integrated scikit-learn ML modules into Django views for data classification and prediction tasks.\n'
                    'Mentored 10+ students on Django project structure and REST API design.'
                ),
            )
            self.stdout.write('Experience loaded')

        if not Project.objects.exists():
            Project.objects.create(
                title='Financial Data Processing System',
                tech_stack='Python, Django REST Framework, PostgreSQL, Knox, Docker, Render',
                order=0,
                description=(
                    'Developed a backend with offline-capable REST APIs, achieving a 40% performance improvement '
                    'through query optimization. Featured secure Knox authentication and RBAC endpoints.'
                ),
            )
            Project.objects.create(
                title='Real-Time Chat Application',
                tech_stack='Python, Django Channels, WebSockets, Redis, MySQL, Render',
                order=1,
                description=(
                    'Created a real-time chat app supporting 100+ concurrent users with a Redis channel layer '
                    'and persistent message history. Deployed on Render with environment-based configuration.'
                ),
            )
            self.stdout.write('Projects loaded')

        if not Education.objects.exists():
            Education.objects.create(
                degree='B.Sc Computer Science',
                institution='Muslim Arts College, Manonmaniam Sundaranar University',
                period='2020 – 2023',
                order=0,
            )
            Education.objects.create(
                degree='Python Django Trainee Certification',
                institution='Srishti Innovative Computer Systems Pvt. Ltd',
                period='Jul 2023 – Feb 2024',
                order=1,
            )
            self.stdout.write('Education loaded')

        self.stdout.write(self.style.SUCCESS('Initial data loaded successfully!'))
