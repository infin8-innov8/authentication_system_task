# Django LDAP Authentication System

A Django-based authentication system integrated with LDAP (Lightweight Directory Access Protocol) for centralized user management, featuring a custom user model and profile synchronization.

## Features

* **Custom User Model**: Extends `AbstractUser` to include a `phone_number` field and automated name capitalization.
* **Dual Authentication**: Supports both standard Django database authentication and LDAP-based authentication.
* **LDAP Integration**:
    * **User Provisioning**: New users are automatically created in the LDAP directory during registration.
    * **Profile Synchronization**: Updates made to user profiles (name, email, phone) are synchronized between the local database and the LDAP server.
    * **Automated Deletion**: A Django signal (`pre_delete`) ensures that when a user is deleted from the database, their corresponding LDAP entry is also removed.
* **Registration Workflow**: Includes a simulated OTP verification step (Phone: `111111`, Email: `222222`) before user creation.
* **Flexible Login**: Users can authenticate using either their username or email address.

## Prerequisites

### System Dependencies
The following packages are required to build `python-ldap` and related tools:
```bash
sudo apt-get install libldap2-dev libsasl2-dev python3.11-dev

# Django LDAP Authentication System

This project provides a Django-based authentication system integrated with LDAP for centralized user management and profile synchronization.

## Prerequisites
* **System Dependencies**: The following packages are required to build `python-ldap` and related tools: `libldap2-dev`, `libsasl2-dev`, and `python3.11-dev`.

## Installation
* **Clone the repository**: Use `git clone <repository-url>` and navigate into `authentication_system_task`.
* **Install Python dependencies**: Run `pip install -r requirements.txt` to install required packages including `Django`, `django-auth-ldap`, and `python-ldap`.
* **Database Configuration**: The project uses a MySQL database named `accounts_db`. Update the database credentials in `settings.py` or via environment variables if preferred.
* **Environment Variables**: Create a `.env` file in the project root with the following LDAP configurations:
    ```env
    AUTH_LDAP_SERVER_URI=ldap://your-ldap-server
    AUTH_LDAP_BIND_DN=cn=admin,dc=example,dc=com
    AUTH_LDAP_BIND_PASSWORD=your-password
    AUTH_LDAP_SEARCH_BASE_DN=ou=users,dc=example,dc=com
    LDAP_USERS_BASE_DN=ou=users,dc=example,dc=com
    ```
* **Run Migrations**: Execute `python manage.py migrate` to set up the database schema.
* **Start the Server**: Run `python manage.py runserver` to launch the development server.

## API Endpoints
* **`/accounts/login/`**: Handles user login and supports both username and email credentials.
* **`/accounts/register/`**: Manages user registration by capturing details like username, email, and phone number.
* **`/accounts/verification/`**: Performs OTP verification (using static codes `111111` for phone and `222222` for email) and creates the user in the LDAP directory.
* **`/accounts/profile/`**: Allows authenticated users to view and update their profile, which automatically synchronizes changes with the LDAP server.
* **`/accounts/home/`**: Serves as a protected dashboard for logged-in users.
* **`/accounts/logout/`**: Manages user logout and session termination.

## Core Features
* **Custom User Model**: Uses `UserAccount`, which extends `AbstractUser` to include a `phone_number` field and automated name capitalization.
* **LDAP Integration**: Features automatic user provisioning during registration and bidirectional profile updates.
* **Automated Cleanup**: A `pre_delete` signal ensures that deleting a user from the Django database also removes their entry from the LDAP server.
* **Management Commands**: Includes a custom command to create an LDAP superuser for administrative purposes.
* **Logging**: Application and authentication events are logged to `logs/debug.log`.
