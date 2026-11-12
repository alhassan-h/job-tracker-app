import os
from datetime import datetime, timedelta
from app import app
from models import db, User, Job, Application, TimelineEvent

def seed_database(drop_tables=True):
    with app.app_context():
        if drop_tables:
            print("Recreating database tables...")
            db.drop_all()
            db.create_all()
        else:
            db.create_all()
            if User.query.first() is not None:
                print("Database already contains data, skipping seed.")
                return

        print("Seeding initial users...")
        # 1. Admin Account
        admin = User(
            full_name="Elena Vance (Talent Lead)",
            username="admin",
            email="admin@jobtracker.com",
            role="admin",
            phone="+1 (555) 019-2834"
        )
        admin.set_password("admin123")
        db.session.add(admin)

        # 2. Candidate Accounts
        candidate1 = User(
            full_name="Sarah Miller",
            username="sarahm",
            email="sarah.miller@example.com",
            role="candidate",
            phone="+1 (555) 234-5678"
        )
        candidate1.set_password("user123")
        db.session.add(candidate1)

        candidate2 = User(
            full_name="Alex Chen",
            username="alexchen",
            email="alex.chen@example.com",
            role="candidate",
            phone="+1 (555) 345-6789"
        )
        candidate2.set_password("user123")
        db.session.add(candidate2)

        candidate3 = User(
            full_name="Marcus Johnson",
            username="marcusj",
            email="marcus.johnson@example.com",
            role="candidate",
            phone="+1 (555) 456-7890"
        )
        candidate3.set_password("user123")
        db.session.add(candidate3)

        candidate4 = User(
            full_name="Jessica Taylor",
            username="jtaylor",
            email="jessica.taylor@example.com",
            role="candidate",
            phone="+1 (555) 567-8901"
        )
        candidate4.set_password("user123")
        db.session.add(candidate4)

        db.session.commit()

        print("Seeding sample job postings...")
        # Jobs
        job1 = Job(
            title="Senior Full-Stack Engineer (Python & React)",
            department="Engineering",
            location="Remote (US / Europe)",
            job_type="Full-time",
            experience_level="Senior",
            salary_range="$130,000 - $165,000 / yr",
            description="""We are looking for an experienced Senior Full-Stack Engineer to architect, build, and scale our core platform services. You will work closely with our product designers, backend teams, and data engineers to deliver fast, reliable, and user-centric features.

As part of our high-velocity team, you'll have significant ownership over technical design choices, code quality, and engineering best practices.""",
            requirements="""• 5+ years of software engineering experience with Python (FastAPI/Flask/Django) and modern JavaScript/TypeScript (React, Next.js or Vue).
• Strong familiarity with relational databases (PostgreSQL/SQLite) and ORM query optimization.
• Solid background designing RESTful APIs and microservices.
• Experience with cloud deployments (AWS, GCP, or Docker/Kubernetes).
• Excellent communication skills in remote, asynchronous environments.""",
            benefits="""• 100% Remote flexibility with home office setup stipend ($1,500).
• Comprehensive health, dental, and vision insurance.
• Unlimited Paid Time Off (minimum 4 weeks mandatory).
• Annual learning and conference budget ($2,000).
• 401(k) retirement match up to 5%.""",
            status="active",
            posted_by_id=admin.id,
            created_at=datetime.utcnow() - timedelta(days=12)
        )

        job2 = Job(
            title="UI/UX Product Designer",
            department="Design",
            location="New York, NY / Hybrid",
            job_type="Full-time",
            experience_level="Mid-Level",
            salary_range="$95,000 - $125,000 / yr",
            description="""Join our Design System team to craft intuitive, accessible, and delightful digital user journeys. You will spearhead user research, wireframing, high-fidelity prototypes in Figma, and design critique sessions with frontend engineers.

Our brand emphasizes clean minimalist typography, light blue soft gradients, and high usability.""",
            requirements="""• 3+ years of digital product design experience for desktop and mobile web.
• Advanced proficiency in Figma, design tokens, and scalable component libraries.
• Demonstrable portfolio highlighting user research, design thinking, and finished web apps.
• Understanding of WCAG 2.1 accessibility guidelines and responsive design principles.""",
            benefits="""• Modern ergonomic office space in Manhattan with commuter benefits.
• Generous wellness subsidy & gym membership.
• Flexible 2-day remote / 3-day office hybrid schedule.
• Top-of-the-line MacBook Pro and 4K external display.""",
            status="active",
            posted_by_id=admin.id,
            created_at=datetime.utcnow() - timedelta(days=9)
        )

        job3 = Job(
            title="Technical Product Manager (Core Platform)",
            department="Product",
            location="Remote",
            job_type="Full-time",
            experience_level="Senior",
            salary_range="$140,000 - $175,000 / yr",
            description="""We are seeking a data-driven Technical Product Manager to lead discovery, roadmapping, and feature prioritization for our platform APIs and developer integrations. You will act as the bridge between business strategy and engineering execution.""",
            requirements="""• 4+ years of product management experience within B2B SaaS or technical platforms.
• Strong analytical mindset: ability to query SQL databases and interpret product analytics metrics.
• Proven track record of launching developer APIs or enterprise workflows.
• Technical background or computer science degree is a strong plus.""",
            benefits="""• Competitive equity package with early exercise options.
• Flexible working hours across global timezones.
• Parental leave: 16 weeks fully paid for primary and secondary caregivers.""",
            status="active",
            posted_by_id=admin.id,
            created_at=datetime.utcnow() - timedelta(days=6)
        )

        job4 = Job(
            title="DevOps & Cloud Infrastructure Specialist",
            department="Engineering",
            location="San Francisco, CA / Remote",
            job_type="Full-time",
            experience_level="Senior",
            salary_range="$150,000 - $185,000 / yr",
            description="""Help us maintain our 99.99% uptime SLA by managing our Terraform configurations, CI/CD pipelines, Kubernetes clusters, and security compliance automation.""",
            requirements="""• 4+ years in site reliability engineering (SRE) or DevOps.
• Deep expertise with AWS or GCP, Terraform/OpenTofu, and Docker.
• Hands-on experience with Prometheus, Grafana, Datadog, or OpenTelemetry.
• Strong scripting ability in Python, Go, or Bash.""",
            benefits="""• Full medical, dental, and life insurance coverage.
• Annual company retreats in exciting destinations.
• Sponsored certifications (AWS Certified Solutions Architect, CKA).""",
            status="active",
            posted_by_id=admin.id,
            created_at=datetime.utcnow() - timedelta(days=4)
        )

        job5 = Job(
            title="Junior Frontend Developer",
            department="Engineering",
            location="Remote",
            job_type="Full-time",
            experience_level="Entry-Level",
            salary_range="$70,000 - $85,000 / yr",
            description="""A great opportunity for a rising frontend talent to build interactive, responsive user interfaces. You will collaborate with senior engineers to implement components, write tests, and polish user interactions.""",
            requirements="""• 1+ years building web applications with HTML5, CSS3, and JavaScript/TypeScript.
• Experience with React, Vue, or modern template engines.
• Familiarity with Git, pull requests, and component libraries (Tailwind CSS, Bootstrap).
• Eagerness to learn and take mentorship.""",
            benefits="""• Dedicated senior engineer mentor.
• Structured training program and paid courses.
• Home office equipment allowance.""",
            status="active",
            posted_by_id=admin.id,
            created_at=datetime.utcnow() - timedelta(days=2)
        )

        job6 = Job(
            title="Content Marketing & Social Media Lead",
            department="Marketing",
            location="Remote",
            job_type="Part-time",
            experience_level="Mid-Level",
            salary_range="$45,000 - $60,000 / yr (20 hrs/wk)",
            description="""Drive brand awareness, curate technical blog posts, and engage our tech community across LinkedIn, X/Twitter, and community newsletters.""",
            requirements="""• 2+ years writing content or managing social channels for tech startups.
• Excellent written English with a warm, informative voice.
• Basic design skills (Canva / Figma) for social asset creation.""",
            benefits="""• High autonomy and flexible schedule.
• Growth opportunity into full-time leadership.""",
            status="active",
            posted_by_id=admin.id,
            created_at=datetime.utcnow() - timedelta(days=1)
        )

        db.session.add_all([job1, job2, job3, job4, job5, job6])
        db.session.commit()

        print("Seeding sample applications with timeline history...")
        # App 1: Sarah Miller applied for Senior Full-Stack Engineer -> Interview Scheduled
        app1 = Application(
            job_id=job1.id,
            user_id=candidate1.id,
            applicant_name="Sarah Miller",
            applicant_email="sarah.miller@example.com",
            applicant_phone="+1 (555) 234-5678",
            linkedin_url="https://linkedin.com/in/sarah-miller-demo",
            portfolio_url="https://sarahmiller-portfolio.dev",
            cover_letter="I have over 6 years of experience architecting Python microservices and React web apps. I love building clean, user-centric software and would be thrilled to bring my passion for scalable architectures to your team.",
            resume_filename="Sarah_Miller_Resume_2026.pdf",
            resume_original_name="Sarah_Miller_Resume_2026.pdf",
            status="interview_scheduled",
            admin_notes="Candidate has impressive GitHub open source work and strong full-stack experience. Invited to technical round.",
            candidate_feedback="We are excited about your background! Your technical interview is scheduled for Tuesday at 2:00 PM EST via Google Meet.",
            applied_at=datetime.utcnow() - timedelta(days=8),
            updated_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(app1)
        db.session.flush()

        t1_1 = TimelineEvent(
            application_id=app1.id,
            status="submitted",
            title="Application Submitted",
            description="Sarah Miller submitted application for Senior Full-Stack Engineer.",
            created_at=datetime.utcnow() - timedelta(days=8)
        )
        t1_2 = TimelineEvent(
            application_id=app1.id,
            status="under_review",
            title="Profile Under Review",
            description="Resume and GitHub repositories screened by recruiting team.",
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        t1_3 = TimelineEvent(
            application_id=app1.id,
            status="interview_scheduled",
            title="Technical Interview Scheduled",
            description="Invited to 45-minute live technical discussion with Lead Architect.",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add_all([t1_1, t1_2, t1_3])

        # App 2: Sarah Miller applied for Technical Product Manager -> Under Review
        app2 = Application(
            job_id=job3.id,
            user_id=candidate1.id,
            applicant_name="Sarah Miller",
            applicant_email="sarah.miller@example.com",
            applicant_phone="+1 (555) 234-5678",
            linkedin_url="https://linkedin.com/in/sarah-miller-demo",
            portfolio_url="https://sarahmiller-portfolio.dev",
            cover_letter="My engineering background pairs naturally with product management. I have led sprint planning and developer API docs in my previous team.",
            status="under_review",
            admin_notes="Assessing fit against engineering vs product track.",
            candidate_feedback="Our hiring committee is actively reviewing your qualifications and portfolio.",
            applied_at=datetime.utcnow() - timedelta(days=4),
            updated_at=datetime.utcnow() - timedelta(days=3)
        )
        db.session.add(app2)
        db.session.flush()

        t2_1 = TimelineEvent(
            application_id=app2.id,
            status="submitted",
            title="Application Submitted",
            description="Application submitted via web portal.",
            created_at=datetime.utcnow() - timedelta(days=4)
        )
        t2_2 = TimelineEvent(
            application_id=app2.id,
            status="under_review",
            title="Under Review",
            description="Hiring committee reviewing candidate qualifications.",
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        db.session.add_all([t2_1, t2_2])

        # App 3: Alex Chen applied for UI/UX Designer -> Offer Extended
        app3 = Application(
            job_id=job2.id,
            user_id=candidate2.id,
            applicant_name="Alex Chen",
            applicant_email="alex.chen@example.com",
            applicant_phone="+1 (555) 345-6789",
            linkedin_url="https://linkedin.com/in/alexchen-design",
            portfolio_url="https://behance.net/alexchendesigns",
            cover_letter="Design is not just what it looks like, it's how it works. I specialize in scalable design systems and modern clean UI with light blue hues.",
            status="offer_extended",
            admin_notes="Exceptional design challenge score (98/100). Culture fit interview went smoothly. Formal offer package prepared.",
            candidate_feedback="Congratulations! We are delighted to extend a formal offer letter to join our team as UI/UX Product Designer. Please check your email for the detailed offer document.",
            applied_at=datetime.utcnow() - timedelta(days=10),
            updated_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add(app3)
        db.session.flush()

        t3_1 = TimelineEvent(application_id=app3.id, status="submitted", title="Application Submitted", created_at=datetime.utcnow() - timedelta(days=10))
        t3_2 = TimelineEvent(application_id=app3.id, status="under_review", title="Portfolio Evaluated", created_at=datetime.utcnow() - timedelta(days=8))
        t3_3 = TimelineEvent(application_id=app3.id, status="interview_scheduled", title="Design Presentation Interview", created_at=datetime.utcnow() - timedelta(days=5))
        t3_4 = TimelineEvent(application_id=app3.id, status="offer_extended", title="Offer Extended!", description="Offer sent to candidate with signing bonus details.", created_at=datetime.utcnow() - timedelta(days=1))
        db.session.add_all([t3_1, t3_2, t3_3, t3_4])

        # App 4: Marcus Johnson applied for DevOps Specialist -> Submitted
        app4 = Application(
            job_id=job4.id,
            user_id=candidate3.id,
            applicant_name="Marcus Johnson",
            applicant_email="marcus.johnson@example.com",
            applicant_phone="+1 (555) 456-7890",
            linkedin_url="https://linkedin.com/in/marcus-devops",
            cover_letter="Seasoned SRE with deep Terraform and AWS ECS experience.",
            status="submitted",
            applied_at=datetime.utcnow() - timedelta(hours=14),
            updated_at=datetime.utcnow() - timedelta(hours=14)
        )
        db.session.add(app4)
        db.session.flush()
        t4_1 = TimelineEvent(application_id=app4.id, status="submitted", title="Application Received", description="Application queued for initial screening.", created_at=datetime.utcnow() - timedelta(hours=14))
        db.session.add(t4_1)

        # App 5: Jessica Taylor applied for Junior Frontend -> Under Review
        app5 = Application(
            job_id=job5.id,
            user_id=candidate4.id,
            applicant_name="Jessica Taylor",
            applicant_email="jessica.taylor@example.com",
            applicant_phone="+1 (555) 567-8901",
            portfolio_url="https://jtaylor-code.io",
            cover_letter="Recent CS graduate eager to contribute frontend code and grow with an awesome engineering team.",
            status="under_review",
            admin_notes="Good GitHub project showcase. Check coding exercise score.",
            candidate_feedback="Your submission is currently with our engineering team lead for review.",
            applied_at=datetime.utcnow() - timedelta(days=1),
            updated_at=datetime.utcnow() - timedelta(hours=5)
        )
        db.session.add(app5)
        db.session.flush()
        t5_1 = TimelineEvent(application_id=app5.id, status="submitted", title="Application Submitted", created_at=datetime.utcnow() - timedelta(days=1))
        t5_2 = TimelineEvent(application_id=app5.id, status="under_review", title="Initial Engineering Review", created_at=datetime.utcnow() - timedelta(hours=5))
        db.session.add_all([t5_1, t5_2])

        db.session.commit()
        print("Database successfully seeded with realistic sample data!")

if __name__ == '__main__':
    seed_database()
