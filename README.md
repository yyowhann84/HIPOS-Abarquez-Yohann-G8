# HIPOS — Holistic Institutional Post-event Output and Segregation

A Django + PostgreSQL starter system for tracking campus post-event cleanup, waste records, photo evidence, and reviewer decisions.

## Included features

- Registration with required fields, email validation, unique username/email checks, and matching passwords.
- Django password hashing, login/logout, flash messages, and login-protected pages.
- Role-protected dashboards: Event Organizer, Cleanup Member, and Reviewer.
- Users can only edit their own profile. Public registration always creates a Cleanup Member account; privileged roles are assigned by an administrator.
- Event creation and editing, cleanup area creation, and member assignment.
- Cleanup workflow: In Progress → Submitted for Review → Completed or Needs Cleanup.
- Waste category/quantity records and photo evidence uploads.
- Reviewer decisions and review history.
- Django admin for managing users, roles, events, areas, categories, and records.
- Supabase PostgreSQL connection settings prepared from the connection details supplied for this project.

## 1. Open in VS Code

1. Extract this ZIP into a folder named `HIPOS-Abarquez-Yohann-G8`.
2. Open that folder in VS Code (`File → Open Folder`).
3. Open the integrated terminal (`Terminal → New Terminal`).
4. Confirm the terminal is at the project root — the same folder where `manage.py` is located.

## 2. Create and activate a virtual environment (Windows PowerShell)

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
py -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Set your Supabase database password

The `.env` file is already included locally and has the Supabase host, port, database name, and username prefilled. Open `.env` and set `DB_PASSWORD` to the database password you created for the Supabase project.

- Do not use your Supabase account login password unless it is also the database password you explicitly created.
- Never commit `.env` or share your database password.
- The connection requires SSL and uses the Session Pooler details you provided.

If `.env` is missing, copy `.env.example` to `.env` and fill in `DB_PASSWORD`.

## 4. Create the database tables

Run these commands in order:

```powershell
python manage.py makemigrations accounts core
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
```

`makemigrations` creates the initial migration files from the models. Keep those migration files in Git so other developers can set up the same schema.

If the database connection fails, double-check the password, host, port, and username in `.env`. Do not paste your password into a chat or commit it to source control.

## 5. Start the development server

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## 6. First-time role setup

1. Create your administrator account with `python manage.py createsuperuser`.
2. Open `http://127.0.0.1:8000/admin/` and sign in.
3. Register test accounts through `/accounts/register/`; they receive the Cleanup Member role by default.
4. In the admin site, open **User profiles** and change selected accounts to **Event Organizer** or **Reviewer**.
5. Log in as an Event Organizer to create an event, add cleanup areas, and assign Cleanup Member users.
6. Log in as an assigned Cleanup Member to start cleanup, add waste details/photo evidence, and submit for review.
7. Log in as a Reviewer to approve a submission or mark it as needing cleanup.

## Important implementation notes

- Supabase stores the relational data. Uploaded photo files are stored locally under `media/` during local development; only the file metadata/path is in PostgreSQL. Supabase Storage can be added later if remote photo storage is needed.
- `DEBUG=True` and the development `SECRET_KEY` placeholder are for local coursework only. Replace the secret key and set `DEBUG=False` before deploying anywhere public.
- This project is a functional starter to polish, not a claim that every possible production/deployment concern has been completed.
