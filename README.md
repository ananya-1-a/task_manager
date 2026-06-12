# Task Manager API

A scalable REST API with JWT authentication, role-based access control (RBAC), and full CRUD operations. Built with Flask, PostgreSQL, and SQLAlchemy.

---

## Tech Stack

- **Backend**: Python 3.10+, Flask 3.0
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Auth**: JWT (Flask-JWT-Extended), Bcrypt password hashing
- **Docs**: Swagger UI (Flasgger)
- **CORS**: Flask-CORS

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/task-manager-api.git
cd task-manager-api
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env .env.local
# Edit .env with your values:
```
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |

### 5. Create PostgreSQL database
```sql
CREATE DATABASE taskmanager;
```

### 6. Run the server
```bash
python app.py
```

Server runs at `http://localhost:5000`

---

## API Endpoints

### Authentication — `/api/v1/auth`
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Register new user | ❌ |
| POST | `/login` | Login, returns JWT | ❌ |
| GET | `/me` | Get current user profile | ✅ |

### Tasks — `/api/v1/tasks`
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Get all tasks (filter by status/priority) | ✅ |
| POST | `/` | Create new task | ✅ |
| GET | `/<id>` | Get single task | ✅ |
| PUT | `/<id>` | Update task | ✅ |
| DELETE | `/<id>` | Delete task | ✅ |

### Admin — `/api/v1/admin` (admin role only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List all users |
| GET | `/tasks` | List all tasks across all users |
| DELETE | `/users/<id>` | Delete a user |

### Authentication header
```
Authorization: Bearer <your_jwt_token>
```

---

## API Documentation

Swagger UI available at: `http://localhost:5000/docs/`

---

## Frontend

Open `frontend/index.html` in any browser. Connects to the local API on port 5000.

Features:
- Register & login
- View tasks with status/priority filters
- Create, edit, delete tasks
- Live stats dashboard

---

## Project Structure

```
task-manager-api/
├── app.py                  # App factory, Swagger config, error handlers
├── config.py               # Environment-based configuration
├── extensions.py           # Shared Flask extensions (db, jwt, bcrypt)
├── models.py               # User and Task SQLAlchemy models
├── routes/
│   ├── auth.py             # Register, login, profile endpoints
│   ├── tasks.py            # Full CRUD for tasks
│   └── admin.py            # Admin-only endpoints
├── middleware/
│   └── auth_middleware.py  # JWT + role decorators
├── frontend/
│   └── index.html          # Single-file vanilla JS frontend
└── requirements.txt
```

---

## Security Practices

- Passwords hashed with **bcrypt** (never stored in plain text)
- **JWT tokens** expire after 24 hours
- Role claims embedded in JWT payload, verified server-side on every request
- Input validation on all endpoints (length, format, enum values)
- SQL injection prevented via SQLAlchemy ORM parameterized queries
- CORS configured via Flask-CORS

---

## Scalability Note

This project is structured for growth across several dimensions:

**Horizontal Scaling**
The stateless JWT design means any number of API instances can run behind a load balancer (Nginx / AWS ALB) — no session state is stored server-side.

**Caching**
Redis can be introduced for caching frequent reads (e.g., task lists) using Flask-Caching with minimal code changes. The blueprint structure isolates cache invalidation to specific route modules.

**Database**
Connection pooling (via SQLAlchemy's built-in pool) and read replicas on PostgreSQL can handle increased load. Schema migrations are straightforward with Flask-Migrate.

**Microservices Path**
The blueprint architecture maps cleanly to microservices: `auth`, `tasks`, and `admin` can each become independent services communicating over REST or a message queue (RabbitMQ/Kafka) with minimal refactoring.

**Containerization**
Docker-ready: each service needs only a `Dockerfile` + `docker-compose.yml` to run isolated with its own environment. CI/CD via GitHub Actions can automate tests and deployment on push.

**Monitoring**
Structured logging (Python `logging` module) is already in place. APM tools like Datadog or Sentry can be added with a single SDK integration per service.