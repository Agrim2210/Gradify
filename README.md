# Gradify 🎓

> **Enterprise-Grade Multi-Tenant Classroom & Academic Workflow Management Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=flat&logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Gradify is a scalable, modern educational platform architected around **Clean Architecture / Domain-Driven Design (DDD)** principles. It powers end-to-end institutional workflows—from workspace creation and multi-role member onboarding (Admin, Teacher, Student) to dynamic classroom management, assignment lifecycle tracking, automated gradebooks, and secure document distribution.

---

## ✨ Key Features

### 🏢 Multi-Tenant Workspaces & Role-Based Access
- **Workspace Isolation**: Multi-workspace tenancy allowing organizations to partition teachers, students, and classrooms.
- **Role Hierarchy**: Strict permission gates across **Admin**, **Teacher**, and **Student** roles.
- **Invitation Lifecycle**: Secure tokenized invitation flows with email dispatch, invitation acceptance, and automatic role assignment.
- **Teacher Delegation**: Teachers can directly invite students into workspaces and classrooms.

### 📚 Classrooms & Academic Workflows
- **Targeted Classrooms**: Teachers create and administer isolated classrooms within their workspaces.
- **Lecture Notes Repository**: Teachers upload and share lecture materials and study resources stored securely via **Backblaze B2 Object Storage**.

### 📝 Student Cockpit
- **To-Do Panel**: Real-time view of active assignments, deadlines, remaining time, and submission forms.
- **Completed Panel**: History of submitted assignments, upload timestamps, and direct file access.
- **Scores & Evaluations**: Individual performance scorecard showing awarded marks and qualitative feedback provided by teachers.

### 📊 Teacher Command Center & Automated Gradebook
- **Categorized Submissions**: Live triage of student submissions grouped into:
  - *On Time*: Submissions turned in before the deadline.
  - *Missed Deadline*: Submissions turned in late.
  - *All Submissions*: Comprehensive audit log.
- **Grading Engine**: Instant score input and qualitative feedback assignment with immediate synchronization.
- **Automated Gradebook Record**: Master grade roster that automatically records **0 marks** for students who missed submission deadlines, preventing evaluation loopholes.

### ⚙️ High-Reliability Architecture
- **Transactional Outbox Pattern**: Guaranteed email notifications (invitations, verifications) without dual-write inconsistency risks.
- **Asynchronous Task Queue**: Celery workers powered by Redis to handle background operations and email delivery cleanly.
- **Modern Security**: Argon2 password hashing, stateless JWT authentication, and scoped workspace context middleware.

---

## 🛠️ Tech Stack

| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance Python async REST API framework |
| **Database & ORM** | [PostgreSQL](https://www.postgresql.org/) + [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Async database access via syncpg |
| **Migrations** | [Alembic](https://alembic.sqlalchemy.org/) | Schema migration tracking and revision management |
| **Task Queue** | [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/) | Outbox worker and asynchronous mail dispatch |
| **Cloud Storage** | [Backblaze B2](https://www.backblaze.com/b2/) | S3-compatible cloud object storage for notes and assignments |
| **Security** | [Argon2-cffi](https://argon2-cffi.readthedocs.io/) & [PyJWT](https://pyjwt.readthedocs.io/) | Password hashing and authentication tokens |
| **Frontend UI** | [React 19](https://react.dev/) + [Vite](https://vitejs.dev/) | Modern reactive web frontend |
| **Styling & Motion** | [Tailwind CSS](https://tailwindcss.com/) + [Framer Motion](https://www.framer.com/motion/) | Sleek, dark-mode modern educational interface |
| **Icons** | [Lucide React](https://lucide.dev/) | Consistent iconography across dashboards |

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- **PostgreSQL 15+**
- **Redis** (for Celery background workers)

---

### 2. Environment Configuration

Clone the repository and copy the environment template into Backend/:

`ash
git clone https://github.com/Agrim2210/Gradify.git
cd Gradify/Backend
cp .env.example .env
`

Open Backend/.env and configure your credentials:
`env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/gradify

# Security
SECRET_KEY=generate-a-strong-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Backblaze B2 Object Storage
B2_APPLICATION_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_app_key
B2_BUCKET_NAME=your_bucket_name
B2_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com

# SMTP Email Dispatch
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Celery Task Broker
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
`

---

### 3. Backend Setup

1. **Navigate to the Backend directory and create a virtual environment**:
   `ash
   cd Gradify/Backend

   # Windows PowerShell
   python -m venv myenv
   .\myenv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv myenv
   source myenv/bin/activate
   `

2. **Install dependencies**:
   `ash
   pip install -r requirements.txt
   `

3. **Run database migrations**:
   `ash
   alembic upgrade head
   `

4. **Start the API server**:
   `ash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   `
   *FastAPI Swagger documentation will be available at http://127.0.0.1:8000/docs.*

---

### 4. Celery Outbox Worker (Background Processing)

From the Backend/ directory, launch the Celery worker to process email dispatch and outbox tasks:

`ash
celery -A app.shared.infra.celery.app.celery_app worker --loglevel=info
`

---

### 5. Frontend Setup

1. **Navigate to the frontend directory**:
   `ash
   cd Gradify/Frontend
   `

2. **Install dependencies**:
   `ash
   npm install
   `

3. **Run development server**:
   `ash
   npm run dev
   `
   *The application will open at http://localhost:5173.*

4. **Build for production**:
   `ash
   npm run build
   `

---

## 🧪 Testing

Run backend tests using Pytest from the Backend/ directory:

`ash
cd Backend
pytest tests/
`

To run with coverage reporting:
`ash
pytest --cov=app tests/
`

---

## 🤝 Contribution Guidelines

1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m 'feat: add some amazing feature')
4. Push to the Branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License.
