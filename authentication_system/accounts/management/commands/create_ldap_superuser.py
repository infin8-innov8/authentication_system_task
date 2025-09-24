import os
import sys
import getpass
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authentication_system.settings')

import django
django.setup()

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import ldap
from ldap import modlist

class Command(BaseCommand):
    help = 'Creates a superuser in both LDAP and Django database with all custom attributes'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--first_name', type=str, help='First name')
        parser.add_argument('--last_name', type=str, help='Last name')
        parser.add_argument('--phone_number', type=str, help='Phone number')
        parser.add_argument('--password', type=str, help='Password (less secure)')
        parser.add_argument('--noinput', action='store_true', help='Non-interactive mode')
    
    def get_ldap_connection(self):
        """Establish connection to LDAP server"""
        try:
            con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            con.set_option(ldap.OPT_REFERRALS, 0)
            con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
            self.stdout.write(self.style.SUCCESS("✓ Connected to LDAP server"))
            return con
        except Exception as e:
            self.stderr.write(f"✗ LDAP Error: {e}")
            return None
    
    def collect_user_info(self, options):
        """Collect all required user information"""
        # Username
        if options['username']:
            username = options['username']
        else:
            username = input("Username: ").strip()
        
        # Email
        if options['email']:
            email = options['email']
        else:
            email = input("Email address: ").strip()
        
        # First name
        if options['first_name']:
            first_name = options['first_name']
        else:
            first_name = input("First name: ").strip() or username  # Default to username if empty
        
        # Last name
        if options['last_name']:
            last_name = options['last_name']
        else:
            last_name = input("Last name: ").strip() or username  # Default to username if empty
        
        # Phone number
        if options['phone_number']:
            phone_number = options['phone_number']
        else:
            phone_number = input("Phone number (optional): ").strip()
        
        # Password
        if options['password']:
            password = options['password']
            password2 = password
        else:
            password = getpass.getpass("Password: ")
            password2 = getpass.getpass("Password (again): ")
        
        return {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'password': password,
            'password2': password2
        }
    
    def validate_user_info(self, user_info):
        """Validate all user information"""
        if not user_info['username']:
            self.stderr.write("✗ Error: Username is required")
            return False
        
        if not user_info['email']:
            self.stderr.write("✗ Error: Email is required")
            return False
        
        if user_info['password'] != user_info['password2']:
            self.stderr.write("✗ Error: Passwords do not match")
            return False
        
        if len(user_info['password']) < 8:
            self.stderr.write("✗ Error: Password must be at least 8 characters long")
            return False
        
        return True
    
    def create_ldap_user(self, user_info):
        """Create user in LDAP server with all attributes"""
        connection = self.get_ldap_connection()
        if not connection:
            return False
        
        try:
            username = user_info['username']
            base_dn = getattr(settings, 'AUTH_LDAP_SEARCH_BASE_DN', settings.SEARCH_BASE_DN)
            user_dn = f"uid={username},{base_dn}"
            
            # Check if user already exists
            search_filter = f"(uid={username})"
            result = connection.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
            if result:
                self.stdout.write(self.style.WARNING(f"User '{username}' already exists in LDAP"))
                connection.unbind()
                return True
            
            # Prepare all LDAP attributes
            attrs = {
                'objectClass': [b'top', b'person', b'organizationalPerson', b'inetOrgPerson'],
                'uid': [username.encode('utf-8')],
                'cn': [user_info['first_name'].encode('utf-8')],  # Common Name (usually first name)
                'sn': [user_info['last_name'].encode('utf-8')],   # Surname (required)
                'givenName': [user_info['first_name'].encode('utf-8')],  # First name
                'mail': [user_info['email'].encode('utf-8')],
                'userPassword': [user_info['password'].encode('utf-8')],
            }
            
            # Add telephone number if provided
            if user_info['phone_number']:
                attrs['telephoneNumber'] = [user_info['phone_number'].encode('utf-8')]
            
            # Convert attributes to LDAP modlist format
            ldif = modlist.addModlist(attrs)
            
            # Add user to LDAP
            connection.add_s(user_dn, ldif)
            self.stdout.write(self.style.SUCCESS(f"✓ User '{username}' created in LDAP with all attributes"))
            
            connection.unbind()
            return True
            
        except ldap.ALREADY_EXISTS:
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists in LDAP"))
            connection.unbind()
            return True
        except Exception as e:
            self.stderr.write(f"✗ Error creating LDAP user: {e}")
            try:
                connection.unbind()
            except:
                pass
            return False
    
    def create_django_user(self, user_info):
        """Create superuser in Django database with all custom attributes"""
        User = get_user_model()
        username = user_info['username']
        
        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"User '{username}' already exists in Django"))
                
                # Update existing user with all attributes
                user = User.objects.get(username=username)
                user.email = user_info['email']
                user.first_name = user_info['first_name']
                user.last_name = user_info['last_name']
                user.phone_number = user_info['phone_number'] or ''  # Handle empty phone
                user.is_staff = True
                user.is_superuser = True
                user.set_password(user_info['password'])  # Local fallback password
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✓ Updated existing user '{username}' to superuser"))
                return True
            
            # Create new superuser with all attributes
            user = User.objects.create_superuser(
                username=username,
                email=user_info['email'],
                password=user_info['password'],
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
                phone_number=user_info['phone_number'] or '',  # Handle optional phone
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Superuser '{username}' created in Django with all attributes"))
            return True
            
        except Exception as e:
            self.stderr.write(f"✗ Error creating Django user: {e}")
            return False
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(self.style.MIGRATE_HEADING("LDAP Superuser Creation with Custom Attributes"))
        self.stdout.write("=" * 60)
        
        # Collect user information
        user_info = self.collect_user_info(options)
        
        # Validate inputs
        if not self.validate_user_info(user_info):
            return
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Collected Information:")
        self.stdout.write(f"  Username: {user_info['username']}")
        self.stdout.write(f"  Email: {user_info['email']}")
        self.stdout.write(f"  First Name: {user_info['first_name']}")
        self.stdout.write(f"  Last Name: {user_info['last_name']}")
        self.stdout.write(f"  Phone: {user_info['phone_number'] or 'Not provided'}")
        self.stdout.write("=" * 60)
        
        # Step 1: Create user in LDAP
        self.stdout.write("\nStep 1: Creating user in LDAP...")
        ldap_success = self.create_ldap_user(user_info)
        
        if not ldap_success:
            self.stderr.write("✗ Failed to create user in LDAP. Aborting.")
            return
        
        # Step 2: Create superuser in Django
        self.stdout.write("Step 2: Creating superuser in Django...")
        django_success = self.create_django_user(user_info)
        
        if not django_success:
            self.stderr.write("✗ Failed to create user in Django.")
            return
        
        # Success message
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SUPERUSER CREATION COMPLETED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS(f"Username: {user_info['username']}"))
        self.stdout.write(self.style.SUCCESS(f"Email: {user_info['email']}"))
        self.stdout.write(self.style.SUCCESS(f"Name: {user_info['first_name']} {user_info['last_name']}"))
        if user_info['phone_number']:
            self.stdout.write(self.style.SUCCESS(f"Phone: {user_info['phone_number']}"))
        self.stdout.write("\nYou can now login using LDAP authentication.")