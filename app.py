import os
import uuid
from functools import wraps
from datetime import datetime, timezone
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort, send_from_directory, jsonify
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Job, Application, TimelineEvent

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Custom decorator for Admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in with an administrator account.', 'warning')
            return redirect(url_for('login', next=request.url))
        if not current_user.is_admin:
            flash('Access restricted to administrators.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Context processor to inject common variables into templates
@app.context_processor
def inject_globals():
    return {
        'now': datetime.now(timezone.utc),
        'all_statuses': Application.STATUSES
    }


# ==========================================
# PUBLIC / AUTH ROUTES
# ==========================================

@app.route('/')
def index():
    featured_jobs = Job.query.filter_by(status='active').order_by(Job.created_at.desc()).limit(6).all()
    departments = db.session.query(Job.department).filter_by(status='active').distinct().all()
    department_list = [d[0] for d in departments if d[0]]
    
    total_active_jobs = Job.query.filter_by(status='active').count()
    total_candidates = User.query.filter_by(role='candidate').count()
    total_applications = Application.query.count()
    
    return render_template(
        'index.html',
        featured_jobs=featured_jobs,
        departments=department_list,
        stats={
            'jobs': total_active_jobs,
            'candidates': total_candidates,
            'applications': total_applications
        }
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('my_applications'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('//') and not next_page.startswith('http'):
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('my_applications'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/quick-login/<role>')
def quick_login(role):
    """Convenience endpoint to quickly switch between demo accounts for testing."""
    if role == 'admin':
        user = User.query.filter_by(email='admin@jobtracker.com').first()
        target = url_for('admin_dashboard')
    else:
        user = User.query.filter_by(email='sarah.miller@example.com').first()
        if not user:
            user = User.query.filter_by(role='candidate').first()
        target = url_for('my_applications')

    if user:
        login_user(user)
        flash(f'Switched to {user.full_name} ({user.role.capitalize()}) mode.', 'info')
        return redirect(target)
    else:
        flash('Demo account not found. Please log in manually.', 'warning')
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'candidate')
        phone = request.form.get('phone', '').strip()

        # Sanitize role: only allow 'candidate' or 'admin'
        if role not in ['candidate', 'admin']:
            role = 'candidate'

        if not full_name or not email or not username or not password:
            flash('Please fill in all required fields.', 'warning')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with this email address already exists.', 'warning')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('That username is already taken. Please choose another.', 'warning')
            return render_template('register.html')

        new_user = User(
            full_name=full_name,
            email=email,
            username=username,
            role=role,
            phone=phone
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash(f'Account created successfully! Welcome to SkyHire, {new_user.full_name}.', 'success')
        
        if new_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('jobs'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))


# ==========================================
# JOB BOARD & SEARCH
# ==========================================

@app.route('/jobs')
def jobs():
    query = request.args.get('q', '').strip()
    department = request.args.get('department', '').strip()
    job_type = request.args.get('job_type', '').strip()
    location = request.args.get('location', '').strip()
    experience = request.args.get('experience', '').strip()

    jobs_query = Job.query.filter_by(status='active')

    if query:
        search_filter = f"%{query}%"
        jobs_query = jobs_query.filter(
            (Job.title.ilike(search_filter)) |
            (Job.description.ilike(search_filter)) |
            (Job.requirements.ilike(search_filter))
        )

    if department:
        jobs_query = jobs_query.filter(Job.department == department)
        
    if job_type:
        jobs_query = jobs_query.filter(Job.job_type == job_type)

    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))

    if experience:
        jobs_query = jobs_query.filter(Job.experience_level == experience)

    job_list = jobs_query.order_by(Job.created_at.desc()).all()

    # Get distinct filter options from active jobs
    departments = [d[0] for d in db.session.query(Job.department).filter_by(status='active').distinct().all() if d[0]]
    job_types = [t[0] for t in db.session.query(Job.job_type).filter_by(status='active').distinct().all() if t[0]]
    experiences = [e[0] for e in db.session.query(Job.experience_level).filter_by(status='active').distinct().all() if e[0]]

    # If current user is logged in as candidate, find which jobs they already applied for
    applied_job_ids = set()
    if current_user.is_authenticated and not current_user.is_admin:
        applied_job_ids = {a.job_id for a in current_user.applications}

    return render_template(
        'jobs.html',
        jobs=job_list,
        applied_job_ids=applied_job_ids,
        departments=departments,
        job_types=job_types,
        experiences=experiences,
        current_filters={
            'q': query,
            'department': department,
            'job_type': job_type,
            'location': location,
            'experience': experience
        }
    )


@app.route('/jobs/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if user already applied
    existing_application = None
    if current_user.is_authenticated:
        existing_application = Application.query.filter_by(job_id=job.id, user_id=current_user.id).first()

    similar_jobs = Job.query.filter(
        Job.status == 'active',
        Job.department == job.department,
        Job.id != job.id
    ).limit(3).all()

    return render_template(
        'job_detail.html',
        job=job,
        existing_application=existing_application,
        similar_jobs=similar_jobs
    )


# ==========================================
# APPLICATION PROCESS & TRACKING
# ==========================================

@app.route('/jobs/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)

    if job.status != 'active':
        flash('This job posting is no longer accepting applications.', 'warning')
        return redirect(url_for('job_detail', job_id=job.id))

    if current_user.is_admin:
        flash('Administrators cannot submit job applications. Please use a candidate account.', 'warning')
        return redirect(url_for('job_detail', job_id=job.id))

    existing = Application.query.filter_by(job_id=job.id, user_id=current_user.id).first()
    if existing:
        flash('You have already submitted an application for this position! You can view its progress below.', 'info')
        return redirect(url_for('my_applications'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip() or current_user.full_name
        email = request.form.get('email', '').strip().lower() or current_user.email
        phone = request.form.get('phone', '').strip() or (current_user.phone or '')
        linkedin_url = request.form.get('linkedin_url', '').strip()
        portfolio_url = request.form.get('portfolio_url', '').strip()
        cover_letter = request.form.get('cover_letter', '').strip()

        # Handle resume upload
        resume_filename = None
        resume_original_name = None

        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                if allowed_file(file.filename):
                    original_name = secure_filename(file.filename)
                    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'pdf'
                    unique_filename = f"{uuid.uuid4().hex}_{int(datetime.now(timezone.utc).timestamp())}.{ext}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    resume_filename = unique_filename
                    resume_original_name = original_name
                else:
                    flash('Invalid file format for resume. Allowed: PDF, DOC, DOCX, TXT.', 'danger')
                    return render_template('apply.html', job=job)

        application = Application(
            job_id=job.id,
            user_id=current_user.id,
            applicant_name=full_name,
            applicant_email=email,
            applicant_phone=phone,
            linkedin_url=linkedin_url,
            portfolio_url=portfolio_url,
            cover_letter=cover_letter,
            resume_filename=resume_filename,
            resume_original_name=resume_original_name,
            status='submitted'
        )
        db.session.add(application)
        db.session.flush()

        # Add initial timeline log
        event = TimelineEvent(
            application_id=application.id,
            status='submitted',
            title='Application Submitted',
            description=f'Application received for {job.title}. Candidate profile and resume recorded.'
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Congratulations! Your application for {job.title} has been submitted successfully.', 'success')
        return redirect(url_for('my_applications'))

    return render_template('apply.html', job=job)


@app.route('/my-applications')
@login_required
def my_applications():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.applied_at.desc()).all()
    
    # Calculate stats for candidate
    total = len(applications)
    active = sum(1 for a in applications if a.status in ['submitted', 'under_review', 'interview_scheduled'])
    interviews = sum(1 for a in applications if a.status == 'interview_scheduled')
    offers = sum(1 for a in applications if a.status in ['offer_extended', 'accepted'])

    return render_template(
        'my_applications.html',
        applications=applications,
        stats={
            'total': total,
            'active': active,
            'interviews': interviews,
            'offers': offers
        }
    )


@app.route('/applications/<int:app_id>/withdraw', methods=['POST'])
@login_required
def withdraw_application(app_id):
    application = Application.query.get_or_404(app_id)

    if application.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if application.status in ['withdrawn', 'accepted', 'rejected']:
        flash('This application cannot be withdrawn at its current stage.', 'warning')
        return redirect(url_for('my_applications'))

    application.status = 'withdrawn'
    application.updated_at = datetime.now(timezone.utc)

    event = TimelineEvent(
        application_id=application.id,
        status='withdrawn',
        title='Application Withdrawn',
        description='The applicant voluntarily withdrew this application.'
    )
    db.session.add(event)
    db.session.commit()

    flash('Your application has been withdrawn.', 'info')
    return redirect(url_for('my_applications'))


@app.route('/resumes/<filename>')
@login_required
def download_resume(filename):
    # Only allow authorized user: candidate who owns it or an admin
    safe_name = secure_filename(filename)
    app_record = Application.query.filter_by(resume_filename=safe_name).first_or_404()

    if not current_user.is_admin and app_record.user_id != current_user.id:
        abort(403)

    download_name = app_record.resume_original_name or safe_name
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        safe_name,
        as_attachment=True,
        download_name=download_name
    )


# ==========================================
# ADMIN PORTAL
# ==========================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(status='active').count()
    total_apps = Application.query.count()
    pending_review = Application.query.filter(Application.status.in_(['submitted', 'under_review'])).count()
    interview_count = Application.query.filter_by(status='interview_scheduled').count()
    offer_count = Application.query.filter(Application.status.in_(['offer_extended', 'accepted'])).count()

    recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(7).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        stats={
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_apps': total_apps,
            'pending_review': pending_review,
            'interview_count': interview_count,
            'offer_count': offer_count
        },
        recent_applications=recent_applications,
        recent_jobs=recent_jobs
    )


@app.route('/admin/jobs')
@admin_required
def admin_jobs():
    search = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()

    jobs_query = Job.query

    if search:
        jobs_query = jobs_query.filter(Job.title.ilike(f"%{search}%"))
    if status:
        jobs_query = jobs_query.filter_by(status=status)

    all_jobs = jobs_query.order_by(Job.created_at.desc()).all()
    return render_template('admin/jobs.html', jobs=all_jobs, current_search=search, current_status=status)


@app.route('/admin/jobs/new', methods=['GET', 'POST'])
@admin_required
def admin_create_job():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time')
        experience_level = request.form.get('experience_level', 'Mid-Level')
        salary_range = request.form.get('salary_range', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        benefits = request.form.get('benefits', '').strip()
        status = request.form.get('status', 'active')

        if not title or not description:
            flash('Job Title and Description are required.', 'warning')
            return render_template('admin/job_form.html', job=None)

        job = Job(
            title=title,
            department=department or 'Engineering',
            location=location or 'Remote',
            job_type=job_type,
            experience_level=experience_level,
            salary_range=salary_range,
            description=description,
            requirements=requirements,
            benefits=benefits,
            status=status,
            posted_by_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()

        flash(f'Job posting "{job.title}" created successfully!', 'success')
        return redirect(url_for('admin_jobs'))

    return render_template('admin/job_form.html', job=None)


@app.route('/admin/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_job(job_id):
    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        job.title = request.form.get('title', '').strip()
        job.department = request.form.get('department', '').strip()
        job.location = request.form.get('location', '').strip()
        job.job_type = request.form.get('job_type', 'Full-time')
        job.experience_level = request.form.get('experience_level', 'Mid-Level')
        job.salary_range = request.form.get('salary_range', '').strip()
        job.description = request.form.get('description', '').strip()
        job.requirements = request.form.get('requirements', '').strip()
        job.benefits = request.form.get('benefits', '').strip()
        job.status = request.form.get('status', 'active')
        job.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        flash(f'Job posting "{job.title}" updated successfully.', 'success')
        return redirect(url_for('admin_jobs'))

    return render_template('admin/job_form.html', job=job)


@app.route('/admin/jobs/<int:job_id>/toggle-status', methods=['POST'])
@admin_required
def admin_toggle_job_status(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = 'closed' if job.status == 'active' else 'active'
    job.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    flash(f'Job "{job.title}" status changed to {job.status.capitalize()}.', 'info')
    return redirect(request.referrer or url_for('admin_jobs'))


@app.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
@admin_required
def admin_delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f'Job posting "{title}" and all associated applications have been deleted.', 'info')
    return redirect(url_for('admin_jobs'))


@app.route('/admin/applications')
@admin_required
def admin_applications():
    job_id = request.args.get('job_id', type=int)
    status = request.args.get('status', '').strip()
    search = request.args.get('q', '').strip()

    apps_query = Application.query

    if job_id:
        apps_query = apps_query.filter_by(job_id=job_id)
    if status:
        apps_query = apps_query.filter_by(status=status)
    if search:
        apps_query = apps_query.filter(
            (Application.applicant_name.ilike(f"%{search}%")) |
            (Application.applicant_email.ilike(f"%{search}%"))
        )

    applications = apps_query.order_by(Application.applied_at.desc()).all()
    all_jobs = Job.query.order_by(Job.title.asc()).all()

    return render_template(
        'admin/applications.html',
        applications=applications,
        jobs=all_jobs,
        selected_job_id=job_id,
        selected_status=status,
        search_query=search
    )


@app.route('/admin/applications/<int:app_id>')
@admin_required
def admin_application_detail(app_id):
    application = Application.query.get_or_404(app_id)
    return render_template('admin/application_detail.html', application=application)


@app.route('/admin/applications/<int:app_id>/update-status', methods=['POST'])
@admin_required
def admin_update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status', '').strip()
    candidate_feedback = request.form.get('candidate_feedback', '').strip()
    admin_notes = request.form.get('admin_notes', '').strip()

    valid_statuses = [s[0] for s in Application.STATUSES]
    if new_status not in valid_statuses:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('admin_application_detail', app_id=app_id))

    old_status = application.status
    application.status = new_status
    if candidate_feedback:
        application.candidate_feedback = candidate_feedback
    if admin_notes:
        application.admin_notes = admin_notes
    application.updated_at = datetime.now(timezone.utc)

    # Record event on timeline
    status_label = dict((s[0], s[1]) for s in Application.STATUSES).get(new_status, new_status.replace('_', ' ').title())
    timeline_title = f"Status updated to: {status_label}"
    desc = candidate_feedback if candidate_feedback else f"Application moved from {old_status.replace('_', ' ')} to {status_label} by recruiting team."

    event = TimelineEvent(
        application_id=application.id,
        status=new_status,
        title=timeline_title,
        description=desc
    )
    db.session.add(event)
    db.session.commit()

    flash(f"Application status for {application.applicant_name} updated to '{status_label}'.", 'success')
    return redirect(url_for('admin_application_detail', app_id=app_id))


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
