# Leave Management System

A full-stack **Leave Management System** built with **FastAPI**, **MongoDB (Motor)**, and **Vue 3 (Shadcn-Vue)**. Supports **Role-Based Access Control** — **Employees** can apply for leave, while **Employers** can approve or reject requests with optional rejection reasons.

---

## ✨ Features

### Core Functionality

- **User Registration & Login** — JWT-based authentication with email/password.
- **Role-Based Access Control** — Separate flows for **Employees** (apply for leave) and **Employers** (manage all requests).
- **Leave Application** — Employees submit requests with type (sick, casual, annual, other), date range, and reason.
- **Status Management** — Employers can approve or reject requests; employees see real-time status updates.
- **Leave Listing** — Employees see their own requests; employers see all requests across the organization.

### Additional Features

- **Database Integrity** — Automatic MongoDB unique-index creation on startup via [FastAPI Lifespan events](https://fastapi.tiangolo.com/advanced/events/), guaranteeing data integrity from the moment the server boots.
- **Robust Validation** — Frontend **Zod** schemas mirror backend **Pydantic v2** models, ensuring consistent validation on both sides of the stack.
- **Custom Validation Error Handler** — FastAPI's `RequestValidationError` handler flattens complex Pydantic errors into a single readable string, which the frontend surfaces as a Sonner toast notification.
- **Security Hardened** — Python 3.13-compatible bcrypt hashing, Axios 401 interceptors for automatic logout, and configurable JWT expiry.
- **Global Notifications** — Toast notifications powered by **Sonner** for every success, error, and validation event.

---

## 🛠️ Tech Stack

| Layer         | Technology                                                                                          |
| ------------- | --------------------------------------------------------------------------------------------------- |
| Backend       | FastAPI · Pydantic v2 · Motor (async MongoDB)                                                       |
| Tooling       | [uv](https://docs.astral.sh/uv/) — lightning-fast dependency management & reproducible environments |
| Auth          | python-jose (JWT) · bcrypt                                                                          |
| Database      | MongoDB                                                                                             |
| Frontend      | Vue 3 · TypeScript · Vite                                                                           |
| UI            | Shadcn-Vue · Tailwind CSS v4 · Lucide Icons                                                         |
| Forms         | VeeValidate · Zod · @vee-validate/zod                                                               |
| HTTP          | Axios (with interceptors for JWT & 401 redirect)                                                    |
| Routing       | Vue Router 4 (navigation guards)                                                                    |
| Notifications | vue-sonner                                                                                          |

---

## 📁 Folder Structure

```
leave_management/
├── backend/
│   ├── main.py              # FastAPI app, lifespan events, CORS, routers
│   ├── database.py          # Motor client & collection references
│   ├── auth.py              # JWT creation/validation, bcrypt, RBAC deps
│   ├── models.py            # Pydantic schemas (User, Leave, Token)
│   ├── pyproject.toml       # Python dependencies
│   └── routes/
│       ├── auth_routes.py   # /auth/register, /auth/login, /auth/me
│       └── leave_routes.py  # /leaves/apply, /leaves/all, /leaves/{id}/status
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.vue
│       ├── main.ts
│       ├── lib/
│       │   ├── api.ts       # Axios instance with JWT interceptors
│       │   └── utils.ts
│       ├── router/
│       │   └── index.ts     # Routes & navigation guards
│       ├── views/
│       │   ├── Login.vue
│       │   └── Dashboard.vue
│       └── components/
│           ├── auth/
│           │   └── AuthForm.vue
│           ├── dashboard/
│           │   ├── LeaveRequestForm.vue
│           │   └── LeaveTable.vue
│           └── ui/
│               ├── badge/
│               ├── button/
│               ├── calendar/
│               ├── card/
│               ├── dialog/
│               ├── form/
│               ├── input/
│               ├── popover/
│               ├── select/
│               ├── sonner/
│               ├── table/
│               ├── tabs/
│               ├── textarea/
│               └── tooltip/
│
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites

- **Python** ≥ 3.13
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — fast Python package manager
- **Node.js** ≥ 18
- **MongoDB** instance (local or [MongoDB Atlas](https://www.mongodb.com/atlas))

### Backend

> Uses **uv** for lightning-fast dependency resolution and reproducible lock-file environments.

```bash
cd backend

# 1. Create a .env file
cat <<EOF > .env
MONGO_DETAILS=mongodb://localhost:27017
JWT_SECRET=your-super-secret-key
JWT_EXPIRE_MINUTES=60
EOF

# 2. Sync dependencies (creates .venv automatically)
uv sync

# 3. Start the server
uv run uvicorn main:app --reload
```

The API will be available at **http://localhost:8000** and interactive docs at **http://localhost:8000/docs**.

### Frontend

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. (Optional) Configure API URL — defaults to http://localhost:8000
#    Create a .env file:
#    VITE_API_URL=http://localhost:8000

# 3. Start the dev server
npm run dev
```

The app will be available at **http://localhost:5173**.

---

## 📡 API Documentation

FastAPI auto-generates interactive API docs — visit **`/docs`** (Swagger UI) or **`/redoc`** (ReDoc) when the server is running.

### Core Endpoints

| Method  | Endpoint              | Auth     | Description                                      |
| ------- | --------------------- | -------- | ------------------------------------------------ |
| `POST`  | `/auth/register`      | Public   | Register a new user (employee/employer)          |
| `POST`  | `/auth/login`         | Public   | Authenticate & receive JWT token                 |
| `GET`   | `/auth/me`            | Bearer   | Get current authenticated user                   |
| `POST`  | `/leaves/apply`       | Employee | Submit a new leave request                       |
| `GET`   | `/leaves/all`         | Bearer   | List leaves (own for employee, all for employer) |
| `PATCH` | `/leaves/{id}/status` | Employer | Approve or reject a leave request                |

---

## 🔒 Security Highlights

- **JWT with Expiry** — Tokens are signed with HS256 and expire after a configurable duration (default: 60 min).
- **bcrypt Password Hashing** — Uses the `bcrypt` library directly, compatible with Python 3.13+.
- **RBAC Dependencies** — FastAPI dependency injection enforces `require_employee` / `require_employer` at the route level.
- **Navigation Guards** — Vue Router's `beforeEach` hook redirects unauthenticated users to login and prevents authenticated users from accessing the login page.
- **Axios Interceptors** — Automatically attaches Bearer tokens to every request; clears auth state and redirects on 401 responses.
- **Unique Email Index** — MongoDB unique index on `email` is created at startup, preventing duplicate registrations at the database level.

---

## 🧩 Technical Challenges & Solutions

| Challenge                             | Solution                                                                                                                                                                                                                                                                                                        |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **bcrypt on Python 3.13**             | Python 3.13 removed the deprecated `_hashlib` fallback that `passlib` relied on. This project uses the `bcrypt` library directly (`bcrypt.hashpw` / `bcrypt.checkpw`), bypassing `passlib` entirely for forward-compatible password hashing.                                                                    |
| **Registration Race Conditions**      | Two concurrent sign-ups with the same email could both pass the application-level check. A **MongoDB unique index** on the `email` field (created at startup via FastAPI Lifespan) acts as a database-level constraint, guaranteeing exactly one write succeeds and the duplicate receives a clear `400` error. |
| **Pydantic Errors → Readable Toasts** | FastAPI's default `422` response returns a verbose JSON array of validation errors. A custom `RequestValidationError` handler extracts the first error, flattens it to `"field: message"`, and returns it as a plain `detail` string — which the frontend displays as a single, human-readable Sonner toast.    |

---

## 🌐 Deployment

### Deployment Topology

This app uses a **Decoupled Architecture**: a statically-hosted Vue 3 frontend communicates over REST with a containerized FastAPI backend, while **MongoDB Atlas** serves as the persistent data layer. The frontend and backend are deployed independently — the frontend is a pure static build served by Vercel's CDN, and the backend runs as a long-lived process on Render. The two are connected at runtime by the `VITE_API_URL` (baked into the frontend at build time) and the `FRONTEND_URL` (used by the backend for CORS).

### Backend (Render)

1. Create a new **Web Service** on [Render](https://render.com) and connect your repository.
2. Set the **Root Directory** to `backend`.
3. Set the **Build Command** to:
   ```bash
   uv sync
   ```
4. Set the **Start Command** to:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Add these **Environment Variables** before the first deploy:
   - `MONGO_DETAILS` — Your MongoDB Atlas connection string.
   - `JWT_SECRET` — A strong, random secret key.
   - `JWT_EXPIRE_MINUTES` — Token expiry (e.g., `60`).
6. Deploy the backend. Once it's live, note the service URL (e.g., `https://your-backend.onrender.com`).
7. **After the frontend is live**, come back and add one more environment variable:
   - `FRONTEND_URL` — The deployed frontend URL (e.g., `https://your-app.vercel.app`).
8. **Redeploy** the backend so the CORS middleware picks up the new `FRONTEND_URL` and allows cross-origin requests from the frontend.

### Frontend (Vercel)

1. Import your repository into [Vercel](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. **Before the first deployment**, add this environment variable so the build embeds the correct API base URL:
   - `VITE_API_URL` — The deployed backend URL (e.g., `https://your-backend.onrender.com`).
4. Deploy. Vercel will auto-detect Vite, run `npm run build`, and serve the `dist` output.
5. A `vercel.json` file is included in the `frontend/` directory to configure SPA routing — it rewrites all paths to `index.html`, preventing 404 errors on page refresh when using Vue Router in history mode.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
