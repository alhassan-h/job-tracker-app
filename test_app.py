import io
import unittest
from app import app
from models import db, User, Job, Application, TimelineEvent

class JobTrackerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            # Create test admin
            self.admin = User(
                full_name="Admin User",
                username="admin_test",
                email="admin@test.com",
                role="admin"
            )
            self.admin.set_password("pass123")
            db.session.add(self.admin)

            # Create test candidate
            self.candidate = User(
                full_name="Candidate User",
                username="candidate_test",
                email="candidate@test.com",
                role="candidate"
            )
            self.candidate.set_password("pass123")
            db.session.add(self.candidate)

            # Create test job
            self.job = Job(
                title="Software Architect",
                department="Engineering",
                location="Remote",
                job_type="Full-time",
                experience_level="Senior",
                salary_range="$150,000 - $180,000",
                description="Lead architectural design.",
                requirements="10+ years experience",
                benefits="Health, 401k",
                status="active",
                posted_by_id=1
            )
            db.session.add(self.job)
            db.session.commit()

            self.admin_id = self.admin.id
            self.candidate_id = self.candidate.id
            self.job_id = self.job.id

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SkyHire', response.data)
        self.assertIn(b'Software Architect', response.data)

    def test_job_listing_and_filter(self):
        response = self.client.get('/jobs?department=Engineering')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Software Architect', response.data)

    def test_job_detail_page(self):
        response = self.client.get(f'/jobs/{self.job_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lead architectural design', response.data)

    def test_candidate_apply_and_track(self):
        # Login as candidate
        self.login('candidate@test.com', 'pass123')

        # Submit application
        data = {
            'full_name': 'Candidate User',
            'email': 'candidate@test.com',
            'phone': '123-456-7890',
            'cover_letter': 'Excited to apply for Software Architect.',
            'resume': (io.BytesIO(b"Dummy resume content"), 'test_resume.pdf')
        }
        res = self.client.post(f'/jobs/{self.job_id}/apply', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'submitted successfully', res.data)

        # Check in tracker
        tracker_res = self.client.get('/my-applications')
        self.assertEqual(tracker_res.status_code, 200)
        self.assertIn(b'Software Architect', tracker_res.data)
        self.assertIn(b'Application Submitted', tracker_res.data)

    def test_admin_post_job_and_update_status(self):
        # Login as admin
        self.login('admin@test.com', 'pass123')

        # Post new job
        res = self.client.post('/admin/jobs/new', data=dict(
            title='Data Scientist',
            department='AI Lab',
            location='Hybrid',
            job_type='Full-time',
            experience_level='Mid-Level',
            salary_range='$110k - $130k',
            description='Build machine learning pipelines.',
            requirements='Python, Pandas',
            benefits='Gym, Dental',
            status='active'
        ), follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Data Scientist', res.data)

        # Candidate applies
        self.logout()
        self.login('candidate@test.com', 'pass123')
        with app.app_context():
            new_job = Job.query.filter_by(title='Data Scientist').first()
            new_job_id = new_job.id

        self.client.post(f'/jobs/{new_job_id}/apply', data=dict(
            full_name='Candidate User',
            email='candidate@test.com',
            cover_letter='ML enthusiast'
        ), follow_redirects=True)

        # Admin logs back in to review & update candidate status
        self.logout()
        self.login('admin@test.com', 'pass123')

        with app.app_context():
            app_record = Application.query.filter_by(job_id=new_job_id).first()
            app_record_id = app_record.id

        # Update status to interview_scheduled with feedback
        update_res = self.client.post(f'/admin/applications/{app_record_id}/update-status', data=dict(
            status='interview_scheduled',
            candidate_feedback='We would love to interview you on Friday at 10 AM.',
            admin_notes='Strong candidate'
        ), follow_redirects=True)
        self.assertEqual(update_res.status_code, 200)

        # Verify candidate sees this status & message
        self.logout()
        self.login('candidate@test.com', 'pass123')
        cand_tracker = self.client.get('/my-applications')
        self.assertIn(b'Interview Scheduled', cand_tracker.data)
        self.assertIn(b'We would love to interview you on Friday at 10 AM', cand_tracker.data)

if __name__ == '__main__':
    unittest.main()

