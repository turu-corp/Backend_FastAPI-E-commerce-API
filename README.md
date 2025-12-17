# FastAPI E-commerce API

A robust and feature-rich backend API for an e-commerce platform, built with Python, FastAPI, and PostgreSQL. This project serves as a powerful foundation for building modern online stores, featuring a clean architecture, comprehensive entity management, and a complete order processing workflow.

---

## 🚀 Key Features

- **Authentication & Authorization**: Secure JWT-based authentication with role-based access control (Admin vs. Customer).
- **Product Management**: Full CRUD for products, including variants (SKU, stock), images, brands, and hierarchical categories.
- **Shopping Cart**: Persistent shopping cart functionality for authenticated users.
- **Complete Order Lifecycle**: A sophisticated order workflow from creation to delivery.
  - **Preview**: Calculate costs, including discounts and shipping, before placing an order.
  - **Checkout**: Transactional order creation to ensure data integrity (stock reduction, cart clearing).
  - **Payment**: Initiate payments and handle status updates via simulated webhooks.
  - **Status Flow**: `Pending` -> `Processing` -> `Shipped` -> `Delivered` / `Cancelled`.
- **Dynamic E-commerce Entities**: Full management for Discounts, Shipping Methods, Brands, and Categories.
- **Data Validation**: Strong data validation and serialization using Pydantic schemas.
- **Automated Documentation**: Interactive API documentation with Swagger UI and ReDoc.
- **Database Migrations**: Schema management using Alembic.
- **Email Service Integration**: Automated email notifications for user registration and order confirmation.

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with SQLModel
- **Data Validation**: Pydantic
- **Authentication**: JWT, Passlib (for hashing)
- **Migrations**: Alembic
- **Server**: Uvicorn

## 🗂️ Project Structure

The project follows a clean and scalable structure, separating concerns into distinct modules.

```
ecommerce-api/
├── alembic/              # Database migration scripts
├── app/
│   ├── api/v1/           # API routers for each resource
│   ├── models/           # SQLModel database models
│   ├── schemas/          # Pydantic data validation schemas
│   ├── services/         # Business logic (e.g., EmailService)
│   ├── utils/            # Utility functions (e.g., security)
│   ├── dependencies.py   # FastAPI dependencies (e.g., get_current_user)
│   ├── database.py       # Database session management
│   └── main.py           # FastAPI application entry point
├── .env                  # Environment variables (ignored by Git)
├── .gitignore            # Git ignore file
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## ⚙️ Setup and Installation

Follow these steps to get the project running locally.

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Git

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd ecommerce-api
```

### 3. Set Up a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file by copying the example file.

```bash
cp .env.example .env
```

Now, edit the `.env` file with your local configuration.

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
SECRET_KEY=a_very_strong_and_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email Configuration (e.g., for Gmail App Password)
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-google-app-password
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

### 6. Set Up the Database

a. **Create the PostgreSQL database**:

```sql
CREATE DATABASE ecommerce_db;
```

b. **Configure Alembic**:
Open `alembic.ini` and set the `sqlalchemy.url` to your database connection string.

c. **Run Migrations**:
Apply all database migrations to create the tables.

```bash
alembic upgrade head
```

### 7. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## 📚 API Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## workflow Spotlight: Order Lifecycle

The order management system is a core feature with a well-defined state machine:

1.  **`PENDING`**: An order is created by a user but not yet paid. Stock is reduced.
2.  **`PROCESSING`**: A payment is successfully processed (simulated via webhook). The order is now ready for the warehouse team.
3.  **`SHIPPED`**: An admin marks the order as shipped. The customer is notified.
4.  **`DELIVERED`**: The customer confirms the receipt of the order.
5.  **`CANCELLED`**: The order is cancelled by the user or an admin. Stock is restored.

## 🚀 Deployment

### Using Docker

A `Dockerfile` is provided for easy containerization.

1.  **Build the Docker image:**
    ```bash
    docker build -t ecommerce-api .
    ```
2.  **Run the container:**
    Make sure your `.env` file is present in the root directory.
    ```bash
    docker run -p 8000:8000 --env-file .env ecommerce-api
    ```

### Manual Deployment (with Gunicorn)

For a production environment, it's recommended to use a production-grade server like Gunicorn.

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request for any improvements or bug fixes.

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
