from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utcnow():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='candidate') # 'admin' or 'candidate'
    phone = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    # Relationships
    posted_jobs = db.relationship('Job', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='applicant', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    department = db.Column(db.String(80), nullable=False, default='Engineering')
    location = db.Column(db.String(100), nullable=False, default='Remote')
    job_type = db.Column(db.String(40), nullable=False, default='Full-time') # Full-time, Part-time, Remote, Contract, Hybrid
    experience_level = db.Column(db.String(50), nullable=False, default='Mid-Level') # Entry, Mid-Level, Senior, Lead
    salary_range = db.Column(db.String(60), nullable=True) # e.g. "$90,000 - $120,000"
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active') # active, closed, draft
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    posted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def application_count(self):
        return self.applications.count()

    def __repr__(self):
        return f'<Job {self.title}>'


class Application(db.Model):
    __tablename__ = 'applications'
    
    STATUSES = [
        ('submitted', 'Application Submitted', 'bg-sky-100 text-sky-800 border-sky-300'),
        ('under_review', 'Under Review', 'bg-blue-100 text-blue-800 border-blue-300'),
        ('interview_scheduled', 'Interview Scheduled', 'bg-indigo-100 text-indigo-800 border-indigo-300'),
        ('offer_extended', 'Offer Extended', 'bg-emerald-100 text-emerald-800 border-emerald-300'),
        ('accepted', 'Accepted & Hired', 'bg-teal-100 text-teal-800 border-teal-300'),
        ('rejected', 'Not Selected', 'bg-slate-100 text-slate-700 border-slate-300'),
        ('withdrawn', 'Withdrawn', 'bg-amber-100 text-amber-800 border-amber-300')
    ]

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    applicant_name = db.Column(db.String(120), nullable=False)
    applicant_email = db.Column(db.String(120), nullable=False)
    applicant_phone = db.Column(db.String(30), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    
    resume_filename = db.Column(db.String(255), nullable=True)
    resume_original_name = db.Column(db.String(255), nullable=True)
    
    # Status tracking
    status = db.Column(db.String(40), nullable=False, default='submitted')
    admin_notes = db.Column(db.Text, nullable=True) # Internal notes for admin only
    candidate_feedback = db.Column(db.Text, nullable=True) # Visible message / feedback to applicant
    
    applied_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    timeline_logs = db.relationship('TimelineEvent', backref='application', lazy='dynamic', cascade='all, delete-orphan', order_by="TimelineEvent.created_at.desc()")

    @property
    def status_label(self):
        mapping = {s[0]: s[1] for s in self.STATUSES}
        return mapping.get(self.status, self.status.replace('_', ' ').title())

    @property
    def status_badge_class(self):
        mapping = {s[0]: s[2] for s in self.STATUSES}
        return mapping.get(self.status, 'bg-slate-100 text-slate-800 border-slate-300')

    @property
    def progress_percentage(self):
        steps = {
            'submitted': 20,
            'under_review': 45,
            'interview_scheduled': 75,
            'offer_extended': 90,
            'accepted': 100,
            'rejected': 100,
            'withdrawn': 100
        }
        return steps.get(self.status, 20)

    def __repr__(self):
        return f'<Application {self.id} user={self.user_id} job={self.job_id}>'


class TimelineEvent(db.Model):
    __tablename__ = 'timeline_events'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    is_internal_only = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<TimelineEvent {self.id} for App {self.application_id}>'

