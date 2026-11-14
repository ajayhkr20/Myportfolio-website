from io import BytesIO
import json
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import BlockedVisitor, Profile, Project, SiteVisitor, Skill, SkillCategory


class VisitorAccessTests(TestCase):
    def test_homepage_records_visit_without_exposing_logs(self):
        response = self.client.get(reverse('home'), HTTP_USER_AGENT='Portfolio test')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SiteVisitor.objects.count(), 1)
        self.assertEqual(SiteVisitor.objects.get().page, 'home')
        self.assertNotContains(response, 'Site Visitors')
        self.assertNotContains(response, 'Someone just visited your portfolio')
        self.assertContains(response, 'hero-card-designation')
        self.assertContains(response, 'hero-card-name')
        self.assertContains(response, 'hero-card-location')
        self.assertContains(response, 'Software Engineer')
        self.assertNotContains(response, '@ajay.offx_2')
        self.assertNotContains(response, 'instagram-profile-card')

    def test_visitor_logs_require_staff_access(self):
        url = reverse('visitor_list')
        self.assertEqual(self.client.get(url).status_code, 302)

        User.objects.create_user(username='visitor', password='test-password')
        self.client.login(username='visitor', password='test-password')
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.logout()
        User.objects.create_user(username='staff', password='test-password', is_staff=True)
        self.client.login(username='staff', password='test-password')
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_staff_can_block_and_unblock_visitor_ips(self):
        staff = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff)
        url = reverse('toggle_visitor_block')

        response = self.client.post(url, {
            'ip_address': '203.0.113.10',
            'action': 'block',
        })
        self.assertRedirects(response, reverse('visitor_list'))
        self.assertTrue(BlockedVisitor.objects.filter(ip_address='203.0.113.10').exists())

        self.client.logout()
        response = self.client.get(reverse('home'), REMOTE_ADDR='203.0.113.10')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SiteVisitor.objects.count(), 0)

        self.client.force_login(staff)
        response = self.client.post(url, {
            'ip_address': '203.0.113.10',
            'action': 'unblock',
        })
        self.assertRedirects(response, reverse('visitor_list'))
        self.assertFalse(BlockedVisitor.objects.exists())

        self.client.logout()
        response = self.client.get(reverse('home'), REMOTE_ADDR='203.0.113.10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SiteVisitor.objects.count(), 1)

    def test_non_staff_cannot_block_visitors(self):
        User.objects.create_user(username='visitor', password='test-password')
        self.client.login(username='visitor', password='test-password')

        response = self.client.post(reverse('toggle_visitor_block'), {
            'ip_address': '203.0.113.10',
            'action': 'block',
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(BlockedVisitor.objects.exists())

    def test_dashboard_does_not_render_chatbot(self):
        staff = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'aj-chat-wrap')

    def test_chatbot_welcome_uses_current_profile_information(self):
        Profile.objects.create(
            name='Ajay Updated',
            title='Django Developer',
            summary='Updated profile summary for the assistant.',
            email='ajay@example.com',
            phone='+91 1234567890',
            location='Kochi',
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Updated profile summary for the assistant.')
        self.assertContains(response, 'Django Developer')

    @patch('portfolio.views.gemini_client')
    def test_chatbot_answers_using_current_profile_information(self, gemini_client):
        Profile.objects.create(
            name='Ajay Updated',
            title='Django Developer',
            summary='Updated profile summary for the assistant.',
            email='ajay@example.com',
            phone='+91 1234567890',
            location='Kochi',
        )
        gemini_client.models.generate_content.return_value.text = 'Updated answer'

        response = self.client.post(
            reverse('chatbot_stream'),
            data=json.dumps({'messages': [{'role': 'user', 'content': 'Tell me about Ajay.'}]}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'reply': 'Updated answer'})
        prompt = gemini_client.models.generate_content.call_args.kwargs['contents']
        self.assertIn('Updated profile summary for the assistant.', prompt)
        self.assertIn('Ajay Updated', prompt)


class ProjectURLValidationTests(TestCase):
    def test_unsafe_project_links_are_rejected(self):
        project = Project(
            title='Portfolio test',
            description='Test project',
            tech_stack='Django',
            live_url='javascript:alert(1)',
        )

        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_project_create_rejects_unsafe_link(self):
        staff = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.post(reverse('crud_create', args=['project']), {
            'title': 'Unsafe project',
            'description': 'Test project',
            'tech_stack': 'Django',
            'github_url': '',
            'live_url': 'javascript:alert(1)',
            'order': '0',
            'is_active': 'on',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 0)
        self.assertContains(response, 'Enter a valid HTTP or HTTPS URL.')

    def test_project_edit_rejects_unsafe_link(self):
        project = Project.objects.create(
            title='Safe project',
            description='Test project',
            tech_stack='Django',
            live_url='https://example.com',
        )
        staff = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.post(
            reverse('crud_edit', args=['project', project.pk]),
            {
                'title': project.title,
                'description': project.description,
                'tech_stack': project.tech_stack,
                'github_url': '',
                'live_url': 'javascript:alert(1)',
                'order': '0',
                'is_active': 'on',
            },
        )

        project.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(project.live_url, 'https://example.com')
        self.assertContains(response, 'Enter a valid HTTP or HTTPS URL.')


class SkillDashboardTests(TestCase):
    def setUp(self):
        staff = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff)

    def test_staff_can_add_category_and_skill_from_dashboard(self):
        response = self.client.post(reverse('skill_manager'), {
            'name': 'Backend',
            'order': '1',
        })
        self.assertRedirects(response, reverse('skill_manager'))
        category = SkillCategory.objects.get(name='Backend')

        response = self.client.post(reverse('skill_create'), {
            'category': str(category.pk),
            'name': 'Django',
            'order': '1',
        })
        self.assertRedirects(response, reverse('skill_manager'))
        self.assertTrue(Skill.objects.filter(category=category, name='Django').exists())

    def test_skills_dashboard_displays_categories_and_edit_actions(self):
        category = SkillCategory.objects.create(name='Backend')
        skill = Skill.objects.create(category=category, name='Django')

        response = self.client.get(reverse('skill_manager'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend')
        self.assertContains(response, 'Django')
        self.assertContains(response, reverse('skill_edit', args=[skill.pk]))

    def test_add_skill_page_preselects_its_category(self):
        category = SkillCategory.objects.create(name='Backend')

        response = self.client.get(reverse('skill_create'), {'category': category.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['category'].value(), category.pk)

    def test_skill_can_be_edited_and_deleted(self):
        category = SkillCategory.objects.create(name='Backend')
        skill = Skill.objects.create(category=category, name='Django')

        response = self.client.post(reverse('skill_edit', args=[skill.pk]), {
            'category': str(category.pk),
            'name': 'Django REST Framework',
            'order': '2',
        })
        self.assertRedirects(response, reverse('skill_manager'))
        skill.refresh_from_db()
        self.assertEqual(skill.name, 'Django REST Framework')

        response = self.client.post(reverse('skill_delete', args=[skill.pk]))
        self.assertRedirects(response, reverse('skill_manager'))
        self.assertFalse(Skill.objects.filter(pk=skill.pk).exists())


class ProfileUploadTests(TestCase):
    def setUp(self):
        staff = User.objects.create_user(
            username='staff',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff)
        self.profile = Profile.objects.create(
            name='Ajay',
            title='Developer',
            summary='Portfolio profile',
            email='ajay@example.com',
        )

    def test_staff_can_upload_profile_photo_and_resume_without_cloudinary(self):
        image_data = BytesIO()
        Image.new('RGB', (1, 1), color='blue').save(image_data, format='PNG')
        image_data.seek(0)
        storages = {
            'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
            'staticfiles': {
                'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
            },
        }

        with tempfile.TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root,
            STORAGES=storages,
        ):
            response = self.client.post(reverse('manage_profile'), {
                'name': self.profile.name,
                'title': self.profile.title,
                'summary': self.profile.summary,
                'email': self.profile.email,
                'phone': '+91 1234567890',
                'location': 'Kochi',
                'github_url': '',
                'linkedin_url': '',
                'profile_photo': SimpleUploadedFile(
                    'profile.png',
                    image_data.getvalue(),
                    content_type='image/png',
                ),
                'resume': SimpleUploadedFile(
                    'resume.pdf',
                    b'%PDF-1.4 test resume',
                    content_type='application/pdf',
                ),
            })

            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('dashboard'))
            self.profile.refresh_from_db()
            self.assertTrue(self.profile.profile_photo.name.endswith('profile.png'))
            self.assertTrue(self.profile.resume.name.endswith('resume.pdf'))
            self.assertTrue(self.profile.profile_photo.storage.exists(self.profile.profile_photo.name))
            self.assertTrue(self.profile.resume.storage.exists(self.profile.resume.name))
            photo_response = self.client.get(self.profile.profile_photo.url)
            self.assertEqual(photo_response.status_code, 200)
            photo_response.close()

            resume_response = self.client.get(reverse('download_resume'))
            self.assertEqual(resume_response.status_code, 302)
            resume_file_response = self.client.get(resume_response['Location'])
            self.assertEqual(resume_file_response.status_code, 200)
            resume_file_response.close()
