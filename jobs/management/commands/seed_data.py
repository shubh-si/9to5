import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, SeekerProfile, EmployerProfile
from jobs.models import Category, Job, SavedJob
from applications.models import Application


class Command(BaseCommand):
    help = "Seeds database with realistic sample jobs, companies, seekers, and applications"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE(
                "Seeding JobPortal database with realistic initial data..."
            )
        )

        categories_data = [
            (
                "Engineering & Software",
                "engineering-software",
                "bi-code-slash",
                "Software engineering, backend, frontend, devops and cloud roles",
            ),
            (
                "Design & Creative",
                "design-creative",
                "bi-palette",
                "UI/UX design, product design, brand identity, and motion graphics",
            ),
            (
                "Product Management",
                "product-management",
                "bi-kanban",
                "Product strategy, roadmap delivery, technical product owners",
            ),
            (
                "Data & AI",
                "data-ai",
                "bi-cpu",
                "Machine learning, data engineering, analytics, and prompt engineering",
            ),
            (
                "Marketing & Growth",
                "marketing-growth",
                "bi-megaphone",
                "Growth hacking, performance marketing, content, and SEO",
            ),
            (
                "Finance & Operations",
                "finance-operations",
                "bi-cash-coin",
                "Corporate finance, accounting, business ops, and HR",
            ),
        ]

        categories_map = {}
        for name, slug, icon, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slug, defaults={"name": name, "icon": icon, "description": desc}
            )
            categories_map[slug] = cat
        self.stdout.write(
            self.style.SUCCESS(
                f"  Categories verified ({len(categories_map)} categories)"
            )
        )

        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@jobportal.local",
                "first_name": "System",
                "last_name": "Administrator",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True,
            },
        )
        if created or not admin_user.check_password("admin123"):
            admin_user.set_password("admin123")
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.role = User.Role.ADMIN
            admin_user.save()
        self.stdout.write(self.style.SUCCESS("  Admin user: admin / admin123"))

        employers_info = [
            {
                "username": "cloudscale",
                "email": "hiring@cloudscale.io",
                "first_name": "David",
                "last_name": "Miller",
                "company_name": "CloudScale Technologies",
                "industry": "Cloud Infrastructure & DevOps",
                "company_size": "51-200",
                "location": "Austin, TX",
                "website": "https://cloudscale.io",
                "description": "CloudScale builds high-throughput serverless orchestration tooling for Fortune 500 engineering teams. We are a fast-growing, remote-friendly team focused on developer experience and reliable distributed systems.",
            },
            {
                "username": "pulsefin",
                "email": "talent@pulsefin.com",
                "first_name": "Claire",
                "last_name": "Sterling",
                "company_name": "Pulse Financial",
                "industry": "Fintech & Payment APIs",
                "company_size": "201-500",
                "location": "New York, NY",
                "website": "https://pulsefin.com",
                "description": "Pulse Financial empowers modern e-commerce and B2B platforms with real-time settlement APIs and treasury intelligence. Headquartered in Manhattan with hybrid hubs worldwide.",
            },
            {
                "username": "apexhealth",
                "email": "careers@apexhealth.ai",
                "first_name": "Sanjay",
                "last_name": "Gupta",
                "company_name": "Apex Health Intelligence",
                "industry": "Healthcare & Biomedical AI",
                "company_size": "11-50",
                "location": "Boston, MA",
                "website": "https://apexhealth.ai",
                "description": "Apex Health combines clinical insights with cutting-edge computer vision and NLP models to accelerate rare disease diagnostics and streamline clinical workflows.",
            },
        ]

        employer_profiles = {}
        for emp_data in employers_info:
            emp_user, _ = User.objects.get_or_create(
                username=emp_data["username"],
                defaults={
                    "email": emp_data["email"],
                    "first_name": emp_data["first_name"],
                    "last_name": emp_data["last_name"],
                    "role": User.Role.EMPLOYER,
                    "is_verified": True,
                },
            )
            emp_user.set_password("pass123")
            emp_user.save()

            profile, _ = EmployerProfile.objects.get_or_create(
                user=emp_user,
                defaults={
                    "company_name": emp_data["company_name"],
                    "industry": emp_data["industry"],
                    "company_size": emp_data["company_size"],
                    "location": emp_data["location"],
                    "website": emp_data["website"],
                    "description": emp_data["description"],
                    "established_year": 2019,
                },
            )
            employer_profiles[emp_data["username"]] = profile
        self.stdout.write(
            self.style.SUCCESS(
                f"  Employers verified ({len(employer_profiles)} companies)"
            )
        )

        seekers_info = [
            {
                "username": "alex_dev",
                "email": "alex.rivera@example.com",
                "first_name": "Alex",
                "last_name": "Rivera",
                "headline": "Senior Backend Engineer | Python, Django, PostgreSQL & Cloud",
                "bio": "Passionate engineer with 6+ years designing scalable microservices, resilient relational database schemas, and developer-first REST & GraphQL APIs.",
                "location": "Austin, TX",
                "skills": "Python, Django, PostgreSQL, Docker, Redis, AWS, Celery, REST APIs",
                "expected_salary": 140000,
                "portfolio_url": "https://alexrivera.dev",
                "github_url": "https://github.com/alexrivera",
                "experience": [
                    {
                        "title": "Senior Software Engineer",
                        "company": "Datapoint Systems",
                        "period": "2021 - Present",
                        "description": "Architected high-throughput ingestion pipelines in Python/Django processing 15M daily events. Reduced query latency by 45%.",
                    },
                    {
                        "title": "Backend Developer",
                        "company": "StackFlow Software",
                        "period": "2018 - 2021",
                        "description": "Maintained core payments API and implemented automated reconciliation workflows.",
                    },
                ],
                "education": [
                    {
                        "degree": "B.S. in Computer Science",
                        "institution": "University of Texas at Austin",
                        "year": "2018",
                    }
                ],
            },
            {
                "username": "sarah_ux",
                "email": "sarah.chen@example.com",
                "first_name": "Sarah",
                "last_name": "Chen",
                "headline": "Lead Product Designer | Design Systems & SaaS UX",
                "bio": "End-to-end product designer focused on intuitive enterprise workflows, design tokens, and user-centered research methodologies.",
                "location": "San Francisco, CA",
                "skills": "Figma, Design Systems, UX Research, Prototyping, Wireframing, HTML/CSS",
                "expected_salary": 135000,
                "portfolio_url": "https://sarahchen.design",
                "github_url": "",
                "experience": [
                    {
                        "title": "Senior Product Designer",
                        "company": "Kite Metrics",
                        "period": "2020 - Present",
                        "description": "Led redesign of core analytics dashboard, boosting user engagement by 32%.",
                    }
                ],
                "education": [
                    {
                        "degree": "B.A. in Interaction Design",
                        "institution": "California College of the Arts",
                        "year": "2019",
                    }
                ],
            },
            {
                "username": "marcus_data",
                "email": "marcus.vance@example.com",
                "first_name": "Marcus",
                "last_name": "Vance",
                "headline": "Data & Machine Learning Engineer | PySpark, dbt & MLflow",
                "bio": "Specialized in building end-to-end predictive models, robust ETL architectures, and feature stores for high-growth tech platforms.",
                "location": "New York, NY",
                "skills": "Python, PySpark, SQL, dbt, Snowflake, MLflow, Docker, Airflow",
                "expected_salary": 150000,
                "portfolio_url": "https://marcusvance.tech",
                "github_url": "https://github.com/marcusvance",
                "experience": [
                    {
                        "title": "Data Platform Engineer",
                        "company": "FinLedger Analytics",
                        "period": "2022 - Present",
                        "description": "Built modern data stack with dbt and Snowflake, powering BI models across 8 departments.",
                    }
                ],
                "education": [
                    {
                        "degree": "M.S. in Data Analytics",
                        "institution": "Columbia University",
                        "year": "2021",
                    }
                ],
            },
            {
                "username": "elena_mkt",
                "email": "elena.rostova@example.com",
                "first_name": "Elena",
                "last_name": "Rostova",
                "headline": "Growth Marketing Lead | B2B SaaS & Organic Acquisition",
                "bio": "Track record of scaling ARR from $2M to $12M through performance marketing, product-led SEO, and lifecycle retention loops.",
                "location": "Chicago, IL",
                "skills": "SEO, Google Analytics 4, HubSpot, Copywriting, Paid Acquisition, A/B Testing",
                "expected_salary": 115000,
                "portfolio_url": "",
                "github_url": "",
                "experience": [],
                "education": [],
            },
        ]

        seeker_users = {}
        for s_data in seekers_info:
            s_user, _ = User.objects.get_or_create(
                username=s_data["username"],
                defaults={
                    "email": s_data["email"],
                    "first_name": s_data["first_name"],
                    "last_name": s_data["last_name"],
                    "role": User.Role.JOB_SEEKER,
                    "is_verified": True,
                },
            )
            s_user.set_password("pass123")
            s_user.save()

            s_prof, _ = SeekerProfile.objects.get_or_create(
                user=s_user,
                defaults={
                    "headline": s_data["headline"],
                    "bio": s_data["bio"],
                    "location": s_data["location"],
                    "skills": s_data["skills"],
                    "expected_salary": s_data["expected_salary"],
                    "portfolio_url": s_data["portfolio_url"],
                    "github_url": s_data["github_url"],
                    "experience_data": s_data["experience"],
                    "education_data": s_data["education"],
                },
            )
            seeker_users[s_data["username"]] = s_user
        self.stdout.write(
            self.style.SUCCESS(f"  Seekers verified ({len(seeker_users)} profiles)")
        )

        jobs_data = [
            {
                "title": "Senior Backend Engineer (Python / Django)",
                "employer": employer_profiles["cloudscale"],
                "category": categories_map["engineering-software"],
                "location": "Austin, TX",
                "is_remote": True,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.SENIOR,
                "salary_min": 135000,
                "salary_max": 165000,
                "description": "We are seeking an experienced Backend Engineer to lead development of our core orchestration engine. You will own architecture decisions, optimize PostgreSQL queries for scale, and build resilient distributed background workers.",
                "requirements": "- 5+ years building production web applications in Python/Django or FastAPI\n- Deep understanding of PostgreSQL, query planning, indexing, and connection pooling\n- Hands-on experience with Docker, Redis, and message queues (Celery/RabbitMQ)\n- Strong communication skills in an async, remote-first environment",
                "benefits": "- Comprehensive health, dental, and vision insurance\n- 401(k) match up to 5%\n- $2,500 annual home office & tech stipend\n- Flexible, outcome-oriented PTO",
                "status": Job.Status.APPROVED,
                "views_count": 142,
            },
            {
                "title": "Cloud DevOps & Infrastructure Specialist",
                "employer": employer_profiles["cloudscale"],
                "category": categories_map["engineering-software"],
                "location": "Remote - US",
                "is_remote": True,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.MID,
                "salary_min": 120000,
                "salary_max": 145000,
                "description": "Help scale our multi-region Kubernetes clusters and streamline CI/CD pipelines. You will partner with product engineers to guarantee 99.99% uptime and implement automated observability.",
                "requirements": "- 3+ years experience managing AWS or GCP infrastructure\n- Proficient in Terraform and Kubernetes manifest management\n- Solid scripting proficiency in Python or Bash\n- Familiarity with Datadog, Prometheus, or OpenTelemetry",
                "benefits": "- 100% remote flexibility\n- Generous wellness stipend\n- Annual company retreats in Colorado & Lisbon",
                "status": Job.Status.APPROVED,
                "views_count": 89,
            },
            {
                "title": "Staff API Architect & Security Lead",
                "employer": employer_profiles["pulsefin"],
                "category": categories_map["engineering-software"],
                "location": "New York, NY",
                "is_remote": False,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.LEAD,
                "salary_min": 180000,
                "salary_max": 220000,
                "description": "Define the next generation of real-time financial transaction APIs. You will work closely with compliance, banking partners, and engineering squads to ensure impenetrable security and ultra-low latency.",
                "requirements": "- 8+ years architecting enterprise REST/gRPC APIs\n- Thorough understanding of PCI-DSS compliance, OAuth2, mutual TLS, and tokenization\n- Strong background in high-volume relational databases and event streaming (Kafka)\n- Proven leadership mentoring senior and staff engineers",
                "benefits": "- Competitive equity package in Series B fintech\n- Full premium medical and mental health coverage\n- Commuter benefits & catered lunch in Manhattan office",
                "status": Job.Status.APPROVED,
                "views_count": 210,
            },
            {
                "title": "Lead UI/UX Product Designer",
                "employer": employer_profiles["pulsefin"],
                "category": categories_map["design-creative"],
                "location": "New York, NY",
                "is_remote": True,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.SENIOR,
                "salary_min": 125000,
                "salary_max": 155000,
                "description": "We need a visual and interaction design champion to elevate the merchant dashboard experience. You will translate complex ledger data into clear, actionable, and visually stunning interfaces.",
                "requirements": "- 4+ years of product design experience for complex B2B or fintech software\n- Advanced mastery of Figma, auto-layout, interactive components, and token systems\n- Demonstrated track record conducting usability studies and interpreting product telemetry\n- Solid grasp of frontend layout constraints (Bootstrap, CSS Grid, accessibility)",
                "benefits": "- Top tier health insurance\n- Annual conference and workshop budget\n- Flexible work schedule",
                "status": Job.Status.APPROVED,
                "views_count": 165,
            },
            {
                "title": "AI Research Scientist (Computer Vision & Medical Imaging)",
                "employer": employer_profiles["apexhealth"],
                "category": categories_map["data-ai"],
                "location": "Boston, MA",
                "is_remote": False,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.SENIOR,
                "salary_min": 160000,
                "salary_max": 195000,
                "description": "Join a clinical AI team training state-of-the-art vision models on radiological scans. You will publish findings, design novel model architectures, and work with hospital research partners.",
                "requirements": "- Ph.D. or M.S. in Computer Science, Bioengineering, or equivalent AI discipline\n- Proven track record with PyTorch and deep learning for computer vision (segmentation, classification)\n- Publications in NeurIPS, CVPR, MICCAI, or equivalent top conferences is a big plus",
                "benefits": "- Relocation assistance to Boston area\n- Comprehensive health and life insurance\n- Substantial equity grant",
                "status": Job.Status.APPROVED,
                "views_count": 94,
            },
            {
                "title": "Full-Stack Python / React Engineer",
                "employer": employer_profiles["apexhealth"],
                "category": categories_map["engineering-software"],
                "location": "Boston, MA",
                "is_remote": True,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.MID,
                "salary_min": 110000,
                "salary_max": 135000,
                "description": "Help build the diagnostic portal utilized by hundreds of oncology clinicians. You will work across the stack from PostgreSQL models to interactive frontend visualizations.",
                "requirements": "- 3+ years experience with Django, Flask, or FastAPI\n- Familiarity with modern JavaScript/TypeScript and clean HTML/CSS\n- Passion for healthcare impact and high code quality standards",
                "benefits": "- Full medical, dental, vision\n- 401(k) program\n- Flexible remote policy",
                "status": Job.Status.APPROVED,
                "views_count": 118,
            },
            {
                "title": "Growth Marketing & SEO Specialist",
                "employer": employer_profiles["cloudscale"],
                "category": categories_map["marketing-growth"],
                "location": "Austin, TX",
                "is_remote": True,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.MID,
                "salary_min": 85000,
                "salary_max": 110000,
                "description": "Own our organic search roadmap, developer documentation discoverability, and technical content engine. You will collaborate with dev advocates to expand developer adoption.",
                "requirements": "- 3+ years driving SEO and content growth for developer tools or B2B software\n- Data-fluent with GA4, Search Console, Ahrefs, and SQL\n- Excellent written communication skills",
                "benefits": "- Home office setup budget\n- Unlimited book and course allowance\n- Competitive compensation and bonus",
                "status": Job.Status.APPROVED,
                "views_count": 72,
            },
            {
                "title": "Senior Product Manager - Developer Platform",
                "employer": employer_profiles["cloudscale"],
                "category": categories_map["product-management"],
                "location": "Austin, TX",
                "is_remote": True,
                "job_type": Job.JobType.FULL_TIME,
                "experience_level": Job.Experience.SENIOR,
                "salary_min": 145000,
                "salary_max": 175000,
                "description": "Direct the product vision for our CLI and cloud console. You will interview software architects, prioritize roadmap initiatives, and coordinate releases across multiple agile pods.",
                "requirements": "- 4+ years of product management experience on technical or developer-centric products\n- Ability to read code and converse fluidly with distributed systems engineers\n- Customer empathy and strong analytical acumen",
                "benefits": "- Health, vision, dental\n- Generous equity\n- Annual travel stipend",
                "status": Job.Status.APPROVED,
                "views_count": 130,
            },
            {
                "title": "Junior Front-End Web Developer (Internship)",
                "employer": employer_profiles["pulsefin"],
                "category": categories_map["engineering-software"],
                "location": "New York, NY",
                "is_remote": True,
                "job_type": Job.JobType.INTERNSHIP,
                "experience_level": Job.Experience.ENTRY,
                "salary_min": 45000,
                "salary_max": 60000,
                "description": "Exciting 6-month paid internship working alongside our design engineering team. You will build reusable Bootstrap components and implement interactive widgets.",
                "requirements": "- Solid knowledge of HTML5, CSS3, JavaScript, and Bootstrap\n- Keen eye for typography, spacing, and responsive design\n- Eagerness to learn Django templates and server-rendered workflows",
                "benefits": "- 1-on-1 mentorship with senior staff engineers\n- Fast-track consideration for full-time junior role upon completion",
                "status": Job.Status.PENDING,
                "views_count": 12,
            },
            {
                "title": "Contract Financial Analyst (FP&A)",
                "employer": employer_profiles["pulsefin"],
                "category": categories_map["finance-operations"],
                "location": "New York, NY",
                "is_remote": False,
                "job_type": Job.JobType.CONTRACT,
                "experience_level": Job.Experience.MID,
                "salary_min": 90000,
                "salary_max": 115000,
                "description": "Short-term contract assisting with annual budgeting, variance analysis, and investor metrics preparation.",
                "requirements": "- 3+ years financial analysis in tech or investment banking\n- Expert-level Excel and financial modeling capabilities",
                "benefits": "- High hourly billing rate\n- Direct exposure to C-suite leadership",
                "status": Job.Status.PENDING,
                "views_count": 8,
            },
        ]

        created_jobs = []
        for j_info in jobs_data:
            job, _ = Job.objects.get_or_create(
                title=j_info["title"],
                employer=j_info["employer"],
                defaults={
                    "category": j_info["category"],
                    "location": j_info["location"],
                    "is_remote": j_info["is_remote"],
                    "job_type": j_info["job_type"],
                    "experience_level": j_info["experience_level"],
                    "salary_min": j_info["salary_min"],
                    "salary_max": j_info["salary_max"],
                    "description": j_info["description"],
                    "requirements": j_info["requirements"],
                    "benefits": j_info["benefits"],
                    "status": j_info["status"],
                    "views_count": j_info["views_count"],
                    "deadline": timezone.now().date() + timedelta(days=45),
                },
            )
            created_jobs.append(job)
        self.stdout.write(
            self.style.SUCCESS(
                f"  Jobs verified ({len(created_jobs)} jobs created, 2 pending moderation)"
            )
        )

        apps_data = [
            {
                "applicant": seeker_users["alex_dev"],
                "job_title": "Senior Backend Engineer (Python / Django)",
                "status": Application.Status.SHORTLISTED,
                "cover_letter": "Hello CloudScale team,\n\nI have spent the past 6 years building distributed Python and Django applications handling millions of requests daily. In my previous role at Datapoint Systems, I reduced database latency by 45% through query refactoring and PostgreSQL optimization. CloudScale's mission resonates strongly with me and I would love to contribute to your core orchestration engine.\n\nBest regards,\nAlex Rivera",
            },
            {
                "applicant": seeker_users["alex_dev"],
                "job_title": "Cloud DevOps & Infrastructure Specialist",
                "status": Application.Status.APPLIED,
                "cover_letter": "Hi there, I have substantial experience configuring multi-region AWS services, Terraform scripts, and CI/CD pipelines alongside my backend responsibilities. Looking forward to discussing how I can add value.",
            },
            {
                "applicant": seeker_users["sarah_ux"],
                "job_title": "Lead UI/UX Product Designer",
                "status": Application.Status.HIRED,
                "cover_letter": "Dear Pulse Financial Hiring Team,\n\nI specialize in crafting clear, high-density financial analytics interfaces and enterprise design systems. I led the dashboard redesign at Kite Metrics which lifted retention by 32%. I'm excited by the challenge of designing real-time treasury workflows at Pulse Financial.\n\nWarmly,\nSarah Chen",
            },
            {
                "applicant": seeker_users["marcus_data"],
                "job_title": "Senior Backend Engineer (Python / Django)",
                "status": Application.Status.APPLIED,
                "cover_letter": "Hello, I am a data-heavy backend engineer proficient in Python pipelines, PostgreSQL indexing, and distributed data orchestration. I would love to explore backend opportunities at CloudScale.",
            },
            {
                "applicant": seeker_users["elena_mkt"],
                "job_title": "Growth Marketing & SEO Specialist",
                "status": Application.Status.REJECTED,
                "cover_letter": "Hi CloudScale team, I have 3 years scaling organic acquisition for SaaS products and managing content funnels. I am eager to apply my technical marketing skillset to your developer tools.",
            },
        ]

        app_count = 0
        for a_info in apps_data:
            job_obj = Job.objects.filter(title=a_info["job_title"]).first()
            if job_obj:
                app, _ = Application.objects.get_or_create(
                    job=job_obj,
                    applicant=a_info["applicant"],
                    defaults={
                        "status": a_info["status"],
                        "cover_letter": a_info["cover_letter"],
                    },
                )
                app_count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"  Applications verified ({app_count} candidate submissions)"
            )
        )

        first_approved_job = Job.objects.filter(status=Job.Status.APPROVED).first()
        second_approved_job = Job.objects.filter(status=Job.Status.APPROVED).last()
        if first_approved_job:
            SavedJob.objects.get_or_create(
                user=seeker_users["alex_dev"], job=first_approved_job
            )
        if second_approved_job:
            SavedJob.objects.get_or_create(
                user=seeker_users["alex_dev"], job=second_approved_job
            )

        self.stdout.write(
            self.style.SUCCESS("Database seeding completed successfully!")
        )
        self.stdout.write(self.style.NOTICE("Test Credentials:"))
        self.stdout.write("  Admin:    admin / admin123")
        self.stdout.write("  Employer: cloudscale / pass123")
        self.stdout.write("  Employer: pulsefin / pass123")
        self.stdout.write("  Seeker:   alex_dev / pass123")
        self.stdout.write("  Seeker:   sarah_ux / pass123")
