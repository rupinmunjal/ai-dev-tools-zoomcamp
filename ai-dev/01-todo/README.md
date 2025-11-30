# Django TODO Application

A simple TODO application built with Django and managed with UV.

## Features

- ✅ Create, edit, and delete TODOs
- 📅 Assign due dates to TODOs
- ✔️ Mark TODOs as resolved/pending
- 📝 Add descriptions to TODOs
- 🎨 Clean Bootstrap UI

## Installation

This project uses UV for dependency management. Make sure you have UV installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Running the Application

1. Navigate to the project directory:
```bash
cd todo_project
```

2. Run migrations (already done):
```bash
uv run python manage.py migrate
```

3. Create a superuser (optional, for admin access):
```bash
uv run python manage.py createsuperuser
```

4. Start the development server:
```bash
uv run python manage.py runserver
```

5. Open your browser and visit:
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
todo_project/
├── config/           # Django project settings
├── todos/            # TODO app
│   ├── models.py     # Todo model
│   ├── views.py      # Views for CRUD operations
│   ├── forms.py      # TodoForm for input validation
│   ├── urls.py       # URL routing
│   ├── admin.py      # Admin configuration
│   └── templates/    # HTML templates
├── manage.py         # Django management script
└── pyproject.toml    # UV dependencies
```

## Usage

### Creating a TODO
1. Click "New TODO" button
2. Fill in the title (required)
3. Optionally add description and due date
4. Click "Save"

### Editing a TODO
1. Click "Edit" button on any TODO card
2. Modify the fields
3. Click "Save"

### Marking as Resolved
- Click "Mark Resolved" to mark a TODO as complete
- Click "Mark Pending" to mark it as incomplete again

### Deleting a TODO
1. Click "Delete" button
2. Confirm the deletion

## Technology Stack

- **Python**: 3.13
- **Django**: 5.2.8
- **UV**: Package manager
- **Bootstrap**: 5.3 (UI framework)
- **SQLite**: Database (default)
