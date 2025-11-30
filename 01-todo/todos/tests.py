from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.utils import timezone
from datetime import date, timedelta
from .models import Todo
from .forms import TodoForm
from . import views


# ==================== MODEL TESTS ====================
class TodoModelTest(TestCase):
    """Test cases for the Todo model"""

    def setUp(self):
        """Set up test data"""
        self.todo_data = {
            'title': 'Test TODO',
            'description': 'Test description',
            'due_date': date.today() + timedelta(days=7),
            'is_resolved': False
        }

    def test_create_todo_with_all_fields(self):
        """Test creating a TODO with all fields"""
        todo = Todo.objects.create(**self.todo_data)
        self.assertEqual(todo.title, 'Test TODO')
        self.assertEqual(todo.description, 'Test description')
        self.assertEqual(todo.due_date, date.today() + timedelta(days=7))
        self.assertFalse(todo.is_resolved)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)

    def test_create_todo_with_only_title(self):
        """Test creating a TODO with only required field"""
        todo = Todo.objects.create(title='Minimal TODO')
        self.assertEqual(todo.title, 'Minimal TODO')
        self.assertEqual(todo.description, '')
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.is_resolved)

    def test_todo_default_values(self):
        """Test default values for TODO fields"""
        todo = Todo.objects.create(title='Default Values Test')
        self.assertFalse(todo.is_resolved)
        self.assertEqual(todo.description, '')

    def test_todo_string_representation(self):
        """Test __str__ method returns title"""
        todo = Todo.objects.create(title='String Test')
        self.assertEqual(str(todo), 'String Test')

    def test_todo_ordering(self):
        """Test TODOs are ordered by newest first"""
        todo1 = Todo.objects.create(title='First')
        todo2 = Todo.objects.create(title='Second')
        todo3 = Todo.objects.create(title='Third')
        
        todos = Todo.objects.all()
        self.assertEqual(todos[0].title, 'Third')
        self.assertEqual(todos[1].title, 'Second')
        self.assertEqual(todos[2].title, 'First')

    def test_todo_timestamps(self):
        """Test auto-generated timestamps"""
        todo = Todo.objects.create(title='Timestamp Test')
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)
        
        # Update and verify updated_at changes
        original_updated = todo.updated_at
        todo.title = 'Updated Title'
        todo.save()
        self.assertGreater(todo.updated_at, original_updated)


# ==================== FORM TESTS ====================
class TodoFormTest(TestCase):
    """Test cases for the TodoForm"""

    def test_valid_form_with_all_fields(self):
        """Test form is valid with all fields"""
        form_data = {
            'title': 'Form Test TODO',
            'description': 'Test description',
            'due_date': date.today() + timedelta(days=5),
            'is_resolved': True
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_form_with_only_title(self):
        """Test form is valid with only title"""
        form_data = {'title': 'Minimal Form TODO'}
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_title(self):
        """Test form is invalid without title"""
        form_data = {'description': 'No title'}
        form = TodoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_with_empty_description(self):
        """Test form is valid with empty description"""
        form_data = {
            'title': 'No Description TODO',
            'description': ''
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_valid_due_date(self):
        """Test form accepts valid due date"""
        form_data = {
            'title': 'Date Test',
            'due_date': date.today() + timedelta(days=10)
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_widgets(self):
        """Test form widgets have correct CSS classes"""
        form = TodoForm()
        self.assertIn('form-control', form.fields['title'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['description'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['due_date'].widget.attrs['class'])
        self.assertIn('form-check-input', form.fields['is_resolved'].widget.attrs['class'])


# ==================== VIEW TESTS ====================
class TodoViewTest(TestCase):
    """Test cases for TODO views"""

    def setUp(self):
        """Set up test client and sample data"""
        self.client = Client()
        self.todo = Todo.objects.create(
            title='Test TODO',
            description='Test description',
            due_date=date.today() + timedelta(days=7)
        )

    # List View Tests
    def test_todo_list_view_status(self):
        """Test list view returns 200 status"""
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)

    def test_todo_list_view_template(self):
        """Test list view uses correct template"""
        response = self.client.get(reverse('todo_list'))
        self.assertTemplateUsed(response, 'todos/todo_list.html')

    def test_todo_list_view_context(self):
        """Test list view displays all TODOs"""
        response = self.client.get(reverse('todo_list'))
        self.assertIn('todos', response.context)
        self.assertEqual(len(response.context['todos']), 1)
        self.assertEqual(response.context['todos'][0].title, 'Test TODO')

    def test_todo_list_view_empty(self):
        """Test list view with no TODOs"""
        Todo.objects.all().delete()
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['todos']), 0)

    # Create View Tests
    def test_todo_create_view_get(self):
        """Test create view GET request renders form"""
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['action'], 'Create')

    def test_todo_create_view_post_valid(self):
        """Test create view POST with valid data"""
        data = {
            'title': 'New TODO',
            'description': 'New description',
            'due_date': date.today() + timedelta(days=3)
        }
        response = self.client.post(reverse('todo_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Todo.objects.count(), 2)
        new_todo = Todo.objects.get(title='New TODO')
        self.assertEqual(new_todo.description, 'New description')

    def test_todo_create_view_post_invalid(self):
        """Test create view POST with invalid data"""
        data = {'description': 'Missing title'}
        response = self.client.post(reverse('todo_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    # Edit View Tests
    def test_todo_edit_view_get(self):
        """Test edit view GET request renders form with data"""
        response = self.client.get(reverse('todo_edit', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
        self.assertEqual(response.context['action'], 'Edit')
        self.assertEqual(response.context['form'].instance, self.todo)

    def test_todo_edit_view_post_valid(self):
        """Test edit view POST with valid data"""
        data = {
            'title': 'Updated TODO',
            'description': 'Updated description',
            'due_date': date.today() + timedelta(days=5),
            'is_resolved': True
        }
        response = self.client.post(reverse('todo_edit', args=[self.todo.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated TODO')
        self.assertEqual(self.todo.description, 'Updated description')
        self.assertTrue(self.todo.is_resolved)

    def test_todo_edit_view_not_found(self):
        """Test edit view returns 404 for non-existent TODO"""
        response = self.client.get(reverse('todo_edit', args=[9999]))
        self.assertEqual(response.status_code, 404)

    # Delete View Tests
    def test_todo_delete_view_get(self):
        """Test delete view GET shows confirmation page"""
        response = self.client.get(reverse('todo_delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_confirm_delete.html')
        self.assertEqual(response.context['todo'], self.todo)

    def test_todo_delete_view_post(self):
        """Test delete view POST deletes TODO"""
        response = self.client.post(reverse('todo_delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 0)

    def test_todo_delete_view_not_found(self):
        """Test delete view returns 404 for non-existent TODO"""
        response = self.client.get(reverse('todo_delete', args=[9999]))
        self.assertEqual(response.status_code, 404)

    # Toggle Resolved View Tests
    def test_todo_toggle_resolved_false_to_true(self):
        """Test toggling is_resolved from False to True"""
        self.assertFalse(self.todo.is_resolved)
        response = self.client.get(reverse('todo_toggle_resolved', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_resolved)

    def test_todo_toggle_resolved_true_to_false(self):
        """Test toggling is_resolved from True to False"""
        self.todo.is_resolved = True
        self.todo.save()
        response = self.client.get(reverse('todo_toggle_resolved', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.is_resolved)

    def test_todo_toggle_resolved_not_found(self):
        """Test toggle view returns 404 for non-existent TODO"""
        response = self.client.get(reverse('todo_toggle_resolved', args=[9999]))
        self.assertEqual(response.status_code, 404)


# ==================== URL TESTS ====================
class TodoURLTest(TestCase):
    """Test cases for URL routing"""

    def test_list_url_resolves(self):
        """Test list URL resolves to correct view"""
        url = reverse('todo_list')
        self.assertEqual(resolve(url).func, views.todo_list)

    def test_create_url_resolves(self):
        """Test create URL resolves to correct view"""
        url = reverse('todo_create')
        self.assertEqual(resolve(url).func, views.todo_create)

    def test_edit_url_resolves(self):
        """Test edit URL resolves to correct view"""
        url = reverse('todo_edit', args=[1])
        self.assertEqual(resolve(url).func, views.todo_edit)

    def test_delete_url_resolves(self):
        """Test delete URL resolves to correct view"""
        url = reverse('todo_delete', args=[1])
        self.assertEqual(resolve(url).func, views.todo_delete)

    def test_toggle_url_resolves(self):
        """Test toggle URL resolves to correct view"""
        url = reverse('todo_toggle_resolved', args=[1])
        self.assertEqual(resolve(url).func, views.todo_toggle_resolved)
