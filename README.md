# Gradify 🎓

> **Enterprise-Grade Multi-Tenant Classroom & Academic Workflow Management Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=flat&logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![Render](https://img.shields.io/badge/Deploy%20to-Render-46E3B7?style=flat&logo=render&logoColor=white)](https://render.com)
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
| **Database & ORM** | [PostgreSQL](https://www.postgresql.org/) + [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Async database access via `asyncpg` |
| **Migrations** | [Alembic](https://alembic.sqlalchemy.org/) | Schema migration tracking and revision management |
| **Task Queue** | [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/) | Outbox worker and asynchronous mail dispatch |
| **Cloud Storage** | [Backblaze B2](https://www.backblaze.com/b2/) | S3-compatible cloud object storage for notes and assignments |
| **Security** | [Argon2-cffi](https://argon2-cffi.readthedocs.io/) & [PyJWT](https://pyjwt.readthedocs.io/) | Password hashing and authentication tokens |
| **Frontend UI** | [React 19](https://react.dev/) + [Vite](https://vitejs.dev/) | Modern reactive web frontend |
| **Styling & Motion** | [Tailwind CSS](https://tailwindcss.com/) + [Framer Motion](https://www.framer.com/motion/) | Sleek, dark-mode modern educational interface |
| **Icons** | [Lucide React](https://lucide.dev/) | Consistent iconography across dashboards |

---

## ☁️ Deploying to Render (Blueprint)

Gradify is fully pre-configured for automated deployment on [Render](https://render.com) using the included [`render.yaml`](./render.yaml) blueprint specification.

### 1. What Render Provisions Automatically:
- **`gradify-db`**: Managed PostgreSQL Database.
- **`gradify-redis`**: Managed Key-Value store for Celery/caching.
- **`gradify-backend`**: FastAPI Web Service with automatic pre-deploy database migrations (`alembic upgrade head`), health check (`/health`), and dynamic PostgreSQL connection adapter.
- **`gradify-frontend`**: React + Vite Static Site with global CDN distribution and SPA rewrite routing (`/*` -> `/index.html`).

### 2. Steps to Deploy:
1. Push your repository to **GitHub**.
2. Go to the [Render Dashboard](https://dashboard.render.com/) and click **New +** ➔ **Blueprint**.
3. Connect your **Gradify** repository.
4. Render will parse `render.yaml` and display all resources to create.
5. In the Render Dashboard, configure any secret credentials:
   - `B2_APPLICATION_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`, `B2_ENDPOINT_URL` (for file storage).
   - `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_SENDER_EMAIL` (for email notifications).
6. Click **Apply**. Render will automatically provision the database, run migrations, build the frontend, and deploy your services!

---

## 🚀 Local Development Setup

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- **PostgreSQL 15+**
- **Redis** (for Celery background workers)

---

### 2. Environment Configuration

Clone the repository and set up environment files:

```bash
git clone https://github.com/Agrim2210/Gradify.git
cd Gradify

# Setup Backend Environment
cd Backend
cp .env.example .env

# Setup Frontend Environment
cd ../Frontend
cp .env.example .env
```

Open `Backend/.env` and configure your credentials (DB, JWT, B2, SMTP, Celery).

---

### 3. Backend Setup

```bash
cd Gradify/Backend

# Create and activate virtual environment
python -m venv myenv
# Windows PowerShell:
.\myenv\Scripts\Activate.ps1
# Linux / macOS:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*FastAPI Swagger documentation will be available at `http://127.0.0.1:8000/docs`.*

---

### 4. Celery Outbox Worker (Optional)

In a separate terminal, launch the Celery worker from `Backend/`:

```bash
cd Gradify/Backend
celery -A app.shared.infra.celery.app.celery_app worker --loglevel=info
```
*(Note: FastAPI also includes direct background dispatch for email verification and invitations).*

---

### 5. Frontend Setup

```bash
cd Gradify/Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
*The application will open at `http://localhost:5173`.*

---

## 🧪 Testing

Run backend tests using Pytest from the `Backend/` directory:

```bash
cd Gradify/Backend
pytest tests/
```

To run with coverage reporting:
```bash
pytest --cov=app tests/
```

---

## 🤝 Contribution Guidelines

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License.
