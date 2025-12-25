# Django LDAP Authentication System

This project is a Django-based authentication system integrated with LDAP for centralized user management, profile synchronization, and automated account provisioning.

## 1. System Prerequisites
Before installing Python packages, you must install the following system-level dependencies required for building `python-ldap`:
```bash
sudo apt-get install libldap2-dev libsasl2-dev python3.11-dev

```

## 2. Installation and Setup

1. **Clone and Install**:
```bash
git clone 'https://github.com/infin8-innov8/authentication_system_task/tree/main'
cd authentication_system_task
pip install -r requirements.txt

```


*The project requires Django 5.2.6, django-auth-ldap 5.2.0, and python-ldap 3.4.4.*
2. **Database Configuration**:
The system uses a MySQL database named `accounts_db`. Ensure your MySQL server is running on `localhost:3306` with the user `accountant` and password `Activ8*o`.
3. **Environment Variables**:
Create a `.env` file in the project root with the following LDAP configurations:
```env
AUTH_LDAP_SERVER_URI=ldap://your-ldap-server
AUTH_LDAP_BIND_DN=cn=admin,dc=example,dc=com
AUTH_LDAP_BIND_PASSWORD=your-password
AUTH_LDAP_SEARCH_BASE_DN=ou=users,dc=example,dc=com
LDAP_USERS_BASE_DN=ou=users,dc=example,dc=com

```


4. **Initialize and Run**:
```bash
python manage.py migrate
python manage.py runserver

```



## 3. Core Features

* **Custom User Model**: Extends `AbstractUser` with a `phone_number` field and automated name capitalization.
* **LDAP Integration**: New users created via registration are automatically provisioned in LDAP.
* **Profile Synchronization**: Updates to name, email, or phone in Django are automatically synced to the LDAP server.
* **Automated Cleanup**: A `pre_delete` signal ensures LDAP entries are removed when a user is deleted from the Django database.
* **Verification Codes**: For testing, the system uses static OTPs: **Phone: 111111** and **Email: 222222**.

## 4. API Endpoints

The following endpoints are available under the `/accounts/` path:

* `/login/`: User authentication (supports username or email).
* `/register/`: Initial registration form.
* `/verification/`: OTP verification and password setup.
* `/profile/`: View and edit user information (syncs with LDAP).
* `/home/`: Protected user dashboard.
* `/logout/`: Session termination.
* `/forgot_password/` & `/reset_password/`: Password recovery workflows.

## 5. Management Commands

Create an administrative user in both the local database and the LDAP directory simultaneously:

```bash
python manage.py create_ldap_superuser --username <user> --email <email>

```

**Supported Arguments**: `--username`, `--email`, `--first_name`, `--last_name`, `--phone_number`, `--password`.

```

```
