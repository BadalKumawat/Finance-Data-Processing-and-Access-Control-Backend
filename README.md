# Finance Data Processing and Access Control Backend

This is a role-based backend service for a Finance Management Dashboard, built with Django and Django REST Framework (DRF). 

Rather than just building a simple CRUD application, I focused on **real-world financial business logic**, such as atomic balance updates, strict role-based access control (RBAC), and secure slug-based routing.

## Tech Stack
* **Framework:** Python, Django, Django REST Framework (DRF)
* **Database:** SQLite (Chosen for simplicity as per assignment guidelines; easily scalable to PostgreSQL)
* **Authentication:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
* **API Documentation:** Swagger UI & ReDoc (`drf-yasg`)
* **Data Processing:** Django ORM (Aggregations, Annotations)

---

## Core Features & Business Logic

### 1. Strict Role-Based Access Control (RBAC)
The system enforces authorization at both the view and object levels:
* **Admin:** Full access. Can view all global transactions, user directories, and manage categories.
* **Analyst:** Read-only access to global financial records and system-wide analytical dashboards.
* **Viewer (Standard User):** Isolated access. Can only create, view, and manage their *own* wallets and transactions. Their dashboard reflects only their personal financial health.

### 2. Transaction Integrity & Wallet Management
* **Atomic Transactions:** Wrapped transaction creation in `transaction.atomic()` to prevent race conditions and ensure the wallet balance is perfectly synced with income/expense entries.
* **Insufficient Funds Validation:** The backend automatically rejects 'Expense' transactions if the linked wallet lacks sufficient balance.

### 3. Data Security & Persistence
* **Slug-Based Routing:** Completely eliminated integer IDs from API endpoints (e.g., using `account-hdfc-a1b2` instead of `id: 5`) to prevent Insecure Direct Object Reference (IDOR) attacks.

### 4. Advanced Analytics Engine
* Instead of calculating totals in Python loops, the `/api/dashboard/summary/` endpoint utilizes Django ORM `Sum`, `TruncMonth`, and `values().annotate()` to process bulk data directly at the database level for maximum speed.

### 5. Production-Ready API Features
* **Pagination:** Implemented `PageNumberPagination` to handle large datasets efficiently.
* **Search & Filtering:** Dynamic filtering by Date, Type, Category, and text-based search across descriptions and names.

---

## Installation & Local Setup

### 1. **Clone the repository**

**git clone https://github.com/BadalKumawat/Finance-Data-Processing-and-Access-Control-Backend.git**
**cd finance_system**


### 2. **Create and activate a virtual environment**

python -m venv venv
#### On Windows
**venv\Scripts\activate**
#### On Mac/Linux
**source venv/bin/activate**

### --
### 3. **INSTALL DEPENDECY**

**pip install -r requirements.txt**

### 4. **Run Migrations & Setup Database**

python manage.py makemigrations
**python manage.py migrate**

### 5. **Create a Superuser (Admin)**

**python manage.py createsuperuser**


# API Documentation
* Once the server is running, you can explore and test all APIs interactively without Postman:

* Swagger UI: http://127.0.0.1:8000/swagger/

* ReDoc: http://127.0.0.1:8000/redoc/

 # -- Note: For protected endpoints, first login via /api/auth/login/, copy the access token, and paste it in the "Authorize" lock icon at the top of the Swagger page (Format: Bearer <your_token>).

# Assumptions & Trade-offs
* While designing this backend, I made the following practical assumptions:

* Database: Used SQLite for a simplified local setup as permitted. In a real production environment, this would be swapped to PostgreSQL with minimal configuration changes.

* User Onboarding: Assumed users will self-register via the API and default to a standard role (Viewer/Customer), while Admins and Analysts are assigned via the Django Admin panel or secure Admin directory APIs.
