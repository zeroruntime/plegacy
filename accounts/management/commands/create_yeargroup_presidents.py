import os
import random
import string
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create default accounts for year group presidents (1971-2015 + special variants)'

    def handle(self, *args, **options):
        # Define all year groups: regular years (1971-2015) + special variants
        year_groups = []
        
        # Add regular years from 1971 to 2015
        for year in range(1971, 2016):
            year_groups.append(str(year))
        
        # Add special variants
        special_variants = ['1993_shs', '1993_olevel', '1994_shs', '1994_olevel']
        year_groups.extend(special_variants)
        
        # Generate credentials and store them
        credentials = []
        created_count = 0
        skipped_count = 0
        
        for year_group in year_groups:
            username = f'pres_{year_group}'
            password = self.generate_password(year_group)
            
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    year_group=year_group,
                    role='president',
                    is_active=True,
                    first_name='',
                    last_name=''
                )
                credentials.append({
                    'year_group': year_group,
                    'username': username,
                    'password': password
                })
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {username}')
                )
            except IntegrityError:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⊘ Skipped (exists): {username}')
                )
        
        # Write credentials to MD file
        md_file_path = self.write_credentials_file(credentials)
        
        # Summary output
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'Total created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total skipped: {skipped_count}'))
        self.stdout.write(
            self.style.SUCCESS(f'Credentials file: {md_file_path}')
        )
        self.stdout.write(self.style.SUCCESS('='*60))

    def generate_password(self, year_group):
        """
        Generate a secure password with format: year_prefix + 8 random secure chars.
        For special variants like '1993_shs', extract the year part.
        """
        # Extract year (first 4 characters)
        year_prefix = year_group[:4]
        
        # Generate 8 random secure characters (letters, numbers, symbols)
        chars = string.ascii_letters + string.digits + '-_!@#$'
        random_part = ''.join(random.choice(chars) for _ in range(8))
        
        return year_prefix + random_part

    def write_credentials_file(self, credentials):
        """
        Write credentials to a markdown file in the project root.
        """
        from pathlib import Path
        from django.conf import settings
        
        project_root = settings.BASE_DIR
        md_file_path = project_root / 'presec_admissions_credentials.md'
        
        # Group credentials by regular and special years
        regular_creds = [c for c in credentials if len(c['year_group']) <= 4]
        special_creds = [c for c in credentials if len(c['year_group']) > 4]
        
        # Sort for readability
        regular_creds.sort(key=lambda x: int(x['year_group']))
        special_creds.sort(key=lambda x: x['year_group'])
        
        # Generate markdown content
        content = """# PRESEC Year Group Presidents - Default Accounts

**Generated on:** {date}

**Important:** Keep this file secure and distribute credentials via secure channels.

---

## Regular Year Groups (1971-2015)

| Year Group | Username | Password |
|-----------|----------|----------|
""".format(date=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        for cred in regular_creds:
            content += f"| {cred['year_group']} | `{cred['username']}` | `{cred['password']}` |\n"
        
        content += """
---

## Special Year Groups

| Year Group | Username | Password |
|-----------|----------|----------|
"""
        
        for cred in special_creds:
            content += f"| {cred['year_group']} | `{cred['username']}` | `{cred['password']}` |\n"
        
        content += """
---

## Default Credentials Format

- **Username:** `pres_<yeargroup>` (e.g., `pres_1971`, `pres_1993_shs`)
- **Password:** Year prefix + 8 random secure characters (e.g., `1971xK9$mL2pQ`)
- **Role:** Year Group President
- **Status:** Active

---

## Next Steps

1. Distribute credentials securely to respective year group presidents
2. Instruct each president to change their password on first login
3. Keep this file in a secure location

---

*Generated by: create_yeargroup_presidents management command*
"""
        
        # Write to file
        with open(md_file_path, 'w') as f:
            f.write(content)
        
        return str(md_file_path)
