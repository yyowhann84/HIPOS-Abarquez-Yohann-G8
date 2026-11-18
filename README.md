# HIPOS - Holistic Institutional Post-event Output and Segregation

HIPOS is a web-based system for managing campus cleanup activities after events. It helps organizers assign cleanup areas, allows members to submit cleanup records with photo evidence, and lets reviewers check and approve completed work.

This project is being developed using Django and Supabase PostgreSQL for Project Development 1.

## Features

- User registration with input validation
- Login and logout using Django authentication
- Role-based dashboards for Event Organizers, Cleanup Members, and Reviewers
- User profile viewing and editing
- Event creation and management
- Cleanup area creation and member assignments
- Cleanup status tracking
- Waste category and quantity recording
- Photo evidence uploads
- Submission review and approval
- Django Admin for managing users, roles, events, and cleanup records

## Technologies Used

- Python
- Django
- HTML and CSS with Django templates
- Supabase PostgreSQL
- Git and GitHub

## Project Setup

### 1. Open the project

Open the `HIPOS-Abarquez-Yohann-G8` folder in VS Code.

Open the terminal and make sure you are in the folder containing `manage.py`.

### 2. Create a virtual environment

For Windows PowerShell, run:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
venv\Scripts\activate.bat
```

### 3. Configure the database

HIPOS uses Supabase PostgreSQL as its database.

My local `.env` file contains the connection settings for my Supabase project. This file is excluded from GitHub because it contains private database credentials.

If you are setting up the project on another computer, copy `.env.example` to `.env` and enter your own Supabase database credentials. The connection settings must use the correct host, port, username, database name, and SSL mode.

Never upload your `.env` file or database password to GitHub.

### 4. Set up the database tables

Run the following commands:

```powershell
python manage.py migrate
python manage.py seed_categories
```

These commands create the database tables using the existing migrations and add the default waste categories.

If you change the database models during development, create and commit the corresponding migration files:

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an administrator account

Run:

```powershell
python manage.py createsuperuser
```

Follow the prompts to create your username, email address, and password.

### 6. Run HIPOS

Start the development server:

```powershell
python manage.py runserver
```

Open the following addresses in your browser:

- Main website: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/

Keep the terminal open while using the website. If the computer restarts or the server stops, activate the virtual environment and run the server command again.

## User Roles

### Event Organizer
Creates events, manages cleanup areas, and assigns members to cleanup activities.

### Cleanup Member
Views assigned cleanup areas, records waste information, uploads photo evidence, and submits completed work for review.

### Reviewer
Checks cleanup submissions and either approves them or marks them as needing further cleanup.

Newly registered accounts receive the Cleanup Member role by default. An administrator can assign the other roles through Django Admin.

## Photo Uploads

During local development, uploaded photos are stored in the project's `media/` directory. The database stores the related photo information and file path. Remote image storage can be added later if needed.

## GitHub and Security

The repository is public, but private configuration files must not be uploaded.

The `.gitignore` file excludes the following:

- `.env`
- `venv/`
- `.venv/`
- `__pycache__/`
- Python cache files
- The local SQLite database file

The project uses Django's built-in authentication system for password hashing and account management.

## Development Notes

HIPOS is an ongoing academic project. Features may be improved as development continues, including the interface, validation, cleanup workflow, and deployment configuration.

For local coursework, Django's development settings can be used. Before deploying the application publicly, the secret key, debug settings, allowed hosts, and other security settings must be configured appropriately.