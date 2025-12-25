This comprehensive README.md provides the complete setup process, configuration details, and API documentation for your project in a single file:

```markdown
# Django LDAP Authentication System

This project is a Django-based authentication system featuring dual-backend support (LDAP and local database), custom user management, and automated profile synchronization.

## 1. System Prerequisites
Before installing Python packages, you must install the necessary LDAP development headers on your system:
```bash
sudo apt-get install libldap2-dev libsasl2-dev python3.11-dev

```

## 2. Installation and Setup

1. **Clone the Repository**:
```bash
git clone <repository-url>
cd authentication_system_task

```


2. **Install Dependencies**: Use the provided `requirements.txt` to install Django 5.2.6, django-auth-ldap 5.2.0, and other necessary libraries:
```bash
pip install -r requirements.txt

```


3. **Database Configuration**: The project is configured to use a MySQL database named `accounts_db` on `localhost:3306` with the user `accountant` and password `Activ8*o`.
4. **Environment Variables**: Create a `.env` file in the root directory and define the following variables required for LDAP communication:
* `AUTH_LDAP_SERVER_URI`: Your LDAP server address.
* `AUTH_LDAP_BIND_DN`: The Distinguished Name for binding.
* `AUTH_LDAP_BIND_PASSWORD`: The password for the bind DN.
* `AUTH_LDAP_SEARCH_BASE_DN`: The base DN for user searches.
* `LDAP_USERS_BASE_DN`: The base DN where users are created.


5. **Initialize Database**:
```bash
python manage.py migrate

```


6. **Run the Application**:
```bash
python manage.py runserver

```



## 3. Features and Usage

* **Custom User Model**: Uses `UserAccount` (extending `AbstractUser`) with an additional `phone_number` field and automated title-casing for names.
* **LDAP Integration**:
* **Registration**: Automatically creates users in the LDAP directory upon successful verification.
* **Synchronization**: Profile updates (names, email, phone) in Django are instantly synced to the LDAP server.
* **Deletion**: A `pre_delete` signal ensures LDAP entries are removed when a Django user is deleted.


* **Authentication**: Supports logging in via either a username or an email address.
* **Verification Codes**: For testing, the system uses static OTPs: **Phone: 111111** and **Email: 222222**.

## 4. API Endpoints

The following endpoints are accessible under the `/accounts/` path:

* `/login/`: Authenticate users.
* `/register/`: Initial user sign-up.
* `/verification/`: OTP entry and password setup.
* `/profile/`: View and edit user information (syncs with LDAP).
* `/home/`: Protected dashboard for authenticated users.
* `/logout/`: Terminate user session.
* `/forgot_password/` & `/reset_password/`: Password recovery workflows.

## 5. Management Commands

You can create an administrative user directly in the LDAP directory using the custom management command:

```bash
python manage.py create_ldap_superuser

