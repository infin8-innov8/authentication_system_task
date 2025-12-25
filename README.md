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
