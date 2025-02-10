# Contact Identification API

This is a Django REST API for identifying and managing contacts based on email and phone numbers. It determines the primary and secondary contacts linked to a given email or phone number.

> Task URL - [Bitespeed Backend Task: Identity Reconciliation](https://bitespeed.notion.site/Bitespeed-Backend-Task-Identity-Reconciliation-53392ab01fe149fab989422300423199)

## 🚀 Features

- Identify contacts based on email or phone number.
- Maintain primary and secondary contact relationships.
- Provide a structured response with all associated contact details.

## 📌 Tech Stack

- **Python** (Django, Django REST Framework)
- **PostgreSQL** (or SQLite for local development)
- **drf-yasg** (Swagger API Documentation)

---

## 🛠️ Setup and Installation

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/PragatiVerma18/BiteSpeed.git
```

### 2️⃣ Create and Activate a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3️⃣ Install Dependencies

```sh
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations

```sh
python manage.py migrate
```

### 5️⃣ Create a Superuser (for Django Admin)

```sh
python manage.py createsuperuser
```

### 6️⃣ Setup environment variables in `.env`

```sh
DEBUG=
DATABASE_URL=
SECRET_KEY=
```

### 7️⃣ Run the Development Server

```sh
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

### 8️⃣ Run Tests

```
pytest identity_reconciliation/tests/test_identify.py -v
```

---

## 📖 API Documentation

### 🔍 Identify Contact API

#### **Endpoint:**

```
POST /identify/
```

#### **Description:**

> Identifies primary and secondary contacts based on email or phone number. If no contact exists, a new primary contact is created.

#### **Request Body:**

```json
{
  "email": "user@example.com",
  "phoneNumber": "+1234567890"
}
```

#### **Response:**

- **Case 1:** New primary contact created

```json
{
  "contact": {
    "primaryContactId": 23,
    "emails": ["user@example.com"],
    "phoneNumbers": ["+1234567890"],
    "secondaryContactIds": []
  }
}
```

- **Case 2:** Existing contacts found, linked as secondary

```json
{
  "contact": {
    "primaryContactId": 1,
    "emails": ["user@example.com", "secondary@example.com"],
    "phoneNumbers": ["+1234567890", "+9876543210"],
    "secondaryContactIds": [2, 3]
  }
}
```

- **Case 3:** Existing primary contact converted to secondary

```json
{
  "contact": {
    "primaryContactId": 1,
    "emails": ["user@example.com", "oldprimary@example.com"],
    "phoneNumbers": ["+1234567890", "+1122334455"],
    "secondaryContactIds": [2, 3, 4]
  }
}
```

#### **Possible Errors:**

| Status Code | Error Message                                                    |
| ----------- | ---------------------------------------------------------------- |
| 400         | `{"error": "At least one of email or phoneNumber is required."}` |

#### **Swagger & ReDoc Documentation:**

- Swagger UI: [`/swagger/`](https://bitespeed-m8on.onrender.com/swagger/)
- ReDoc UI: [`/redoc/`](https://bitespeed-m8on.onrender.com/)

#### Access Admin Panel

**Username**: `admin`
**Password**: `admin123`
