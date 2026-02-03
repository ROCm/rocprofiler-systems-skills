---
name: testing/pytest
description: Pytest testing skill with modern patterns - use for writing Python tests with fixtures, parametrization, and modular design
---

# Pytest Testing Skill

Use this skill when writing Python tests with pytest framework.

<IMPORTANT>
Follow pytest best practices for modern, modular, and reusable test design.

**Pytest is the standard.** Use pytest for all Python testing.

**Tests MUST be isolated.** Each test should be independent and not rely on execution order or state from other tests.

**Fixtures over setup/teardown.** Use pytest fixtures for test dependencies and resource management, not setUp/tearDown methods.

**Parametrize for data-driven tests.** Use `@pytest.mark.parametrize` instead of writing multiple similar test functions.

**Organize tests logically.** Mirror the source code structure in your test directory. Group related tests in classes when appropriate.

**Test behavior, not implementation.** Focus on testing what the code does, not how it does it. This makes tests resilient to refactoring.
</IMPORTANT>

## Pytest Basics

### Test Discovery and Naming

Pytest automatically discovers tests following these conventions:

```python
# File naming: test_*.py or *_test.py
test_user.py       # ✓ Discovered
user_test.py       # ✓ Discovered
test_models.py     # ✓ Discovered
models.py          # ✗ Not discovered

# Function naming: test_*
def test_user_creation():      # ✓ Discovered
    pass

def test_invalid_email():      # ✓ Discovered
    pass

def helper_function():         # ✗ Not a test (no test_ prefix)
    pass

# Class naming: Test* (no __init__)
class TestUser:                # ✓ Discovered
    def test_creation(self):
        pass

class TestUserValidation:      # ✓ Discovered
    def test_email(self):
        pass

class UserHelper:              # ✗ Not a test class
    pass
```

### Basic Test Structure

```python
from myapp.models import User

def test_user_creation():
    """Test that a user can be created with valid data."""
    # Arrange
    username = "alice"
    email = "alice@example.com"

    # Act
    user = User(username=username, email=email)

    # Assert
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.is_active is True  # Default value


def test_user_invalid_email():
    """Test that invalid email raises ValueError."""
    with pytest.raises(ValueError, match="Invalid email"):
        User(username="bob", email="not-an-email")
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_user.py

# Run specific test
pytest tests/test_user.py::test_user_creation

# Run tests matching pattern
pytest -k "user and not invalid"

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=myapp --cov-report=html

# Run and stop at first failure
pytest -x

# Run last failed tests
pytest --lf

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

## Assertions

### Basic Assertions

```python
import pytest

def test_assertions():
    """Demonstrate pytest assertion introspection."""
    # Equality
    assert result == expected
    assert user.name == "Alice"

    # Identity
    assert value is None
    assert obj is not None

    # Membership
    assert "admin" in user.roles
    assert item not in processed_items

    # Comparison
    assert age >= 18
    assert count < MAX_COUNT

    # Boolean
    assert user.is_active
    assert not user.is_deleted

    # Type checking
    assert isinstance(result, dict)
    assert isinstance(user, User)


def test_approximate_equality():
    """Test floating point with tolerance."""
    import math
    result = math.sqrt(2) ** 2
    assert result == pytest.approx(2.0, rel=1e-9)


def test_assertion_messages():
    """Add custom messages to assertions."""
    assert user.age >= 18, f"User {user.name} is underage: {user.age}"
```

### Exception Testing

```python
import pytest

def test_exception_raised():
    """Test that exception is raised."""
    with pytest.raises(ValueError):
        process_invalid_data()


def test_exception_with_message():
    """Test exception message matches pattern."""
    with pytest.raises(ValueError, match="Invalid email format"):
        User(email="not-an-email")


def test_exception_details():
    """Test exception attributes."""
    with pytest.raises(APIError) as exc_info:
        call_api_with_invalid_token()

    assert exc_info.value.status_code == 401
    assert "authentication" in str(exc_info.value).lower()


def test_no_exception():
    """Test that no exception is raised."""
    # Just call the function - if it raises, test fails
    result = process_valid_data()
    assert result is not None
```

### Warnings Testing

```python
import pytest
import warnings

def test_deprecated_function():
    """Test that deprecated function shows warning."""
    with pytest.warns(DeprecationWarning, match="deprecated"):
        old_function()


def test_warning_details():
    """Test warning details."""
    with pytest.warns(UserWarning) as warning_list:
        trigger_warning()

    assert len(warning_list) == 1
    assert "careful" in str(warning_list[0].message)
```

## Fixtures

### Basic Fixtures

```python
import pytest
from myapp.database import Database
from myapp.models import User

@pytest.fixture
def database():
    """Provide a database connection for tests."""
    db = Database(":memory:")
    db.create_tables()
    yield db  # Provide to test
    db.close()  # Cleanup after test


@pytest.fixture
def sample_user():
    """Provide a sample user for tests."""
    return User(username="alice", email="alice@example.com")


def test_user_save(database, sample_user):
    """Test saving user to database."""
    # Fixtures are automatically injected by name
    database.save(sample_user)
    retrieved = database.get_user(sample_user.id)
    assert retrieved.username == "alice"
```

### Fixture Scopes

```python
import pytest

# Function scope (default): Run once per test function
@pytest.fixture
def temp_file():
    """Create temp file for each test."""
    file = create_temp_file()
    yield file
    file.delete()


# Class scope: Run once per test class
@pytest.fixture(scope="class")
def database_connection():
    """Create database connection for test class."""
    conn = Database.connect()
    yield conn
    conn.close()


# Module scope: Run once per test module
@pytest.fixture(scope="module")
def api_client():
    """Create API client for entire module."""
    client = APIClient()
    client.authenticate()
    yield client
    client.logout()


# Session scope: Run once per test session
@pytest.fixture(scope="session")
def docker_container():
    """Start Docker container for entire test session."""
    container = start_docker_postgres()
    yield container
    container.stop()
```

### Fixture Dependencies

```python
import pytest

@pytest.fixture
def database():
    """Provide database connection."""
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()


@pytest.fixture
def user_repository(database):
    """Provide user repository (depends on database fixture)."""
    return UserRepository(database)


@pytest.fixture
def sample_users(user_repository):
    """Create sample users (depends on user_repository)."""
    users = [
        User(username="alice", email="alice@example.com"),
        User(username="bob", email="bob@example.com"),
    ]
    for user in users:
        user_repository.save(user)
    return users


def test_find_user(user_repository, sample_users):
    """Test finding user by username."""
    # Both fixtures are injected automatically
    user = user_repository.find_by_username("alice")
    assert user is not None
    assert user.email == "alice@example.com"
```

### Autouse Fixtures

```python
import pytest

@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test (runs automatically)."""
    clear_cache()
    reset_counters()
    yield
    # Cleanup after test


@pytest.fixture(autouse=True, scope="module")
def setup_logging():
    """Configure logging for all tests in module."""
    configure_test_logging()
```

### Factory Fixtures

```python
import pytest

@pytest.fixture
def user_factory(database):
    """Fixture that returns a factory function for creating users."""
    def _create_user(username: str, **kwargs):
        user = User(username=username, **kwargs)
        database.save(user)
        return user
    return _create_user


def test_multiple_users(user_factory):
    """Test with multiple users created by factory."""
    alice = user_factory("alice", email="alice@example.com")
    bob = user_factory("bob", email="bob@example.com", admin=True)

    assert alice.username == "alice"
    assert bob.is_admin is True
```

## Parametrization

### Basic Parametrization

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_square(input, expected):
    """Test square function with multiple inputs."""
    assert square(input) == expected


@pytest.mark.parametrize("email", [
    "user@example.com",
    "test+tag@domain.org",
    "name.surname@company.co.uk",
])
def test_valid_emails(email):
    """Test that valid emails are accepted."""
    assert is_valid_email(email) is True


@pytest.mark.parametrize("invalid_email", [
    "not-an-email",
    "@example.com",
    "user@",
    "user name@example.com",
])
def test_invalid_emails(invalid_email):
    """Test that invalid emails are rejected."""
    assert is_valid_email(invalid_email) is False
```

### Multiple Parameters

```python
import pytest

@pytest.mark.parametrize("username,email,expected_valid", [
    ("alice", "alice@example.com", True),
    ("bob", "bob@example.com", True),
    ("", "test@example.com", False),  # Empty username
    ("alice", "not-an-email", False),  # Invalid email
    ("a" * 100, "test@example.com", False),  # Username too long
])
def test_user_validation(username, email, expected_valid):
    """Test user validation with various inputs."""
    user = User(username=username, email=email)
    assert user.is_valid() == expected_valid
```

### Parametrize with IDs

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    pytest.param(2, 4, id="two"),
    pytest.param(3, 9, id="three"),
    pytest.param(10, 100, id="ten"),
])
def test_square_with_ids(input, expected):
    """Test square with readable test IDs."""
    assert square(input) == expected


# Alternative: ids as list
@pytest.mark.parametrize("value,result", [
    (0, "zero"),
    (1, "one"),
    (5, "many"),
], ids=["zero", "one", "many"])
def test_number_name(value, result):
    assert get_name(value) == result
```

### Combining Parametrize

```python
import pytest

@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [3, 4])
def test_add(x, y):
    """Test all combinations: (1,3), (1,4), (2,3), (2,4)."""
    result = x + y
    assert result > 0
```

### Parametrizing Fixtures

```python
import pytest

@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Parametrized fixture - runs tests with each database."""
    db_type = request.param
    db = Database.create(db_type)
    db.connect()
    yield db
    db.close()


def test_user_operations(database):
    """This test runs 3 times (once per database type)."""
    user = User(username="test")
    database.save(user)
    retrieved = database.get_user(user.id)
    assert retrieved.username == "test"
```

## Test Organization with conftest.py

### Project Structure

```
myproject/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       └── services.py
└── tests/
    ├── conftest.py              # Shared fixtures for all tests
    ├── test_models.py
    ├── test_services.py
    └── integration/
        ├── conftest.py          # Fixtures specific to integration tests
        └── test_api.py
```

### Root conftest.py

```python
# tests/conftest.py
"""Shared fixtures for all tests."""
import pytest
from myapp.database import Database
from myapp.models import User

@pytest.fixture(scope="session")
def database_engine():
    """Create database engine for entire test session."""
    engine = Database.create_engine("sqlite:///:memory:")
    Database.create_all_tables(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def database(database_engine):
    """Provide clean database for each test."""
    connection = database_engine.connect()
    transaction = connection.begin()
    session = Database.create_session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user_factory(database):
    """Factory for creating test users."""
    def _create_user(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "active": True,
        }
        user = User(**{**defaults, **kwargs})
        database.add(user)
        database.commit()
        return user
    return _create_user
```

### Subdirectory conftest.py

```python
# tests/integration/conftest.py
"""Fixtures specific to integration tests."""
import pytest
from myapp.api import create_app

@pytest.fixture(scope="module")
def app():
    """Create Flask/FastAPI app for integration testing."""
    app = create_app(testing=True)
    yield app


@pytest.fixture
def client(app):
    """Provide test client for API testing."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client, user_factory):
    """Provide authenticated test client."""
    user = user_factory(username="testuser")
    token = generate_token(user)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

## Mocking and Patching

### Using unittest.mock

```python
import pytest
from unittest.mock import Mock, MagicMock, patch, call

def test_mock_basic():
    """Basic mock usage."""
    mock = Mock()
    mock.method.return_value = 42

    result = mock.method()

    assert result == 42
    mock.method.assert_called_once()


def test_mock_with_side_effect():
    """Mock with side effects."""
    mock = Mock()
    mock.method.side_effect = [1, 2, 3]

    assert mock.method() == 1
    assert mock.method() == 2
    assert mock.method() == 3


def test_mock_exception():
    """Mock that raises exception."""
    mock = Mock()
    mock.method.side_effect = ValueError("Invalid input")

    with pytest.raises(ValueError):
        mock.method()
```

### Patching

```python
import pytest
from unittest.mock import patch

@patch("myapp.services.EmailService")
def test_order_processor_with_patch(mock_email_service):
    """Test using @patch decorator."""
    mock_instance = mock_email_service.return_value
    mock_instance.send.return_value = True

    processor = OrderProcessor()
    processor.process(order)

    mock_instance.send.assert_called_once()


def test_with_patch_context():
    """Test using patch as context manager."""
    with patch("myapp.services.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"data": "value"}

        result = fetch_api_data()

        assert result["data"] == "value"
        mock_get.assert_called_once()


@patch("myapp.services.datetime")
def test_with_mocked_datetime(mock_datetime):
    """Mock datetime.now() for deterministic tests."""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_time

    result = create_timestamp()

    assert result == fixed_time
```

### pytest-mock Plugin

```python
import pytest

def test_with_mocker(mocker):
    """Test using pytest-mock plugin (cleaner than unittest.mock)."""
    mock_service = mocker.patch("myapp.services.EmailService")
    mock_service.return_value.send.return_value = True

    processor = OrderProcessor()
    processor.process(order)

    mock_service.return_value.send.assert_called_once()


def test_spy(mocker):
    """Spy on real method calls."""
    spy = mocker.spy(UserRepository, "find_by_id")

    service = UserService()
    user = service.get_user(123)

    spy.assert_called_once_with(123)
```

## Markers

### Built-in Markers

```python
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Skip this test."""
    pass


@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_specific():
    """Skip on Windows."""
    pass


@pytest.mark.xfail(reason="Known bug #123")
def test_with_known_bug():
    """Expected to fail until bug is fixed."""
    assert buggy_function() == expected


@pytest.mark.xfail(strict=True)
def test_strict_xfail():
    """Must fail, otherwise test fails."""
    pass
```

### Custom Markers

```python
# pytest.ini or pyproject.toml
# [tool.pytest.ini_options]
# markers =
#     slow: marks tests as slow
#     integration: marks tests as integration tests
#     unit: marks tests as unit tests

import pytest

@pytest.mark.slow
def test_large_dataset():
    """Slow test that processes large dataset."""
    process_million_records()


@pytest.mark.integration
def test_api_endpoint():
    """Integration test for API."""
    response = client.get("/users")
    assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.parametrize("input,expected", [(1, 2), (2, 4)])
def test_double(input, expected):
    """Unit test with multiple markers."""
    assert double(input) == expected


# Run only marked tests
# pytest -m slow
# pytest -m "not slow"
# pytest -m "integration and not slow"
```

## Modular Test Patterns

### Test Classes for Grouping

```python
import pytest

class TestUserCreation:
    """Group tests related to user creation."""

    def test_valid_user(self, database):
        """Test creating valid user."""
        user = User(username="alice", email="alice@example.com")
        database.save(user)
        assert user.id is not None

    def test_duplicate_username(self, database, user_factory):
        """Test that duplicate username raises error."""
        user_factory(username="alice")
        with pytest.raises(ValueError):
            user_factory(username="alice")

    def test_invalid_email(self):
        """Test that invalid email raises error."""
        with pytest.raises(ValueError):
            User(username="bob", email="not-an-email")


class TestUserAuthentication:
    """Group tests related to authentication."""

    def test_valid_credentials(self, user_factory):
        """Test authentication with valid credentials."""
        user = user_factory(username="alice")
        user.set_password("secret123")

        assert user.check_password("secret123") is True

    def test_invalid_password(self, user_factory):
        """Test authentication with invalid password."""
        user = user_factory(username="alice")
        user.set_password("secret123")

        assert user.check_password("wrong") is False
```

### Shared Setup with Class Fixtures

```python
import pytest

class TestDatabaseOperations:
    """Tests that share setup via class-scoped fixture."""

    @pytest.fixture(scope="class")
    def populated_database(self, database):
        """Populate database once for all tests in class."""
        users = [
            User(username=f"user{i}", email=f"user{i}@example.com")
            for i in range(100)
        ]
        for user in users:
            database.save(user)
        return database

    def test_count_users(self, populated_database):
        """Test counting users."""
        count = populated_database.count_users()
        assert count == 100

    def test_find_user(self, populated_database):
        """Test finding specific user."""
        user = populated_database.find_by_username("user42")
        assert user.email == "user42@example.com"
```

### Helper Functions

```python
# tests/helpers.py
"""Test helper functions."""
from typing import Any
from myapp.models import User

def assert_user_equal(actual: User, expected: User) -> None:
    """Assert that two users are equal."""
    assert actual.username == expected.username
    assert actual.email == expected.email
    assert actual.is_active == expected.is_active


def create_test_user(**kwargs: Any) -> User:
    """Create a test user with default values."""
    defaults = {
        "username": "testuser",
        "email": "test@example.com",
        "active": True,
    }
    return User(**{**defaults, **kwargs})


# Use in tests
from tests.helpers import assert_user_equal, create_test_user

def test_user_copy(database):
    """Test user copying."""
    original = create_test_user(username="alice")
    copy = original.copy()

    assert_user_equal(copy, original)
    assert copy is not original
```

## Best Practices

### Test Isolation

```python
# GOOD: Tests are independent
def test_create_user(database):
    """Each test gets fresh database."""
    user = User(username="alice")
    database.save(user)
    assert database.count() == 1


def test_delete_user(database, user_factory):
    """Independent - doesn't rely on previous test."""
    user = user_factory(username="bob")
    database.delete(user)
    assert database.count() == 0


# BAD: Tests depend on each other
class TestUserFlow:
    user_id = None

    def test_1_create(self, database):
        user = User(username="alice")
        database.save(user)
        TestUserFlow.user_id = user.id  # Shared state!

    def test_2_update(self, database):
        user = database.get(TestUserFlow.user_id)  # Depends on test_1!
        user.email = "new@example.com"
```

### Arrange-Act-Assert Pattern

```python
def test_user_creation():
    """Test following AAA pattern."""
    # Arrange: Set up test data and dependencies
    username = "alice"
    email = "alice@example.com"

    # Act: Execute the code under test
    user = User(username=username, email=email)

    # Assert: Verify the results
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.is_active is True
```

### Test Naming

```python
# GOOD: Descriptive test names
def test_user_creation_with_valid_data_succeeds():
    pass

def test_user_creation_with_invalid_email_raises_value_error():
    pass

def test_order_total_includes_tax_and_shipping():
    pass

# Pattern: test_[unit]_[scenario]_[expected_behavior]
def test_calculate_discount_when_vip_user_returns_20_percent():
    pass
```

### Fixture Reusability

```python
# conftest.py - Reusable fixtures
@pytest.fixture
def api_client():
    """Reusable API client fixture."""
    return APIClient(base_url="http://localhost:8000")


@pytest.fixture
def admin_token(user_factory):
    """Reusable admin authentication fixture."""
    admin = user_factory(username="admin", is_admin=True)
    return generate_token(admin)


# Multiple tests can use these fixtures
def test_get_users(api_client, admin_token):
    response = api_client.get("/users", headers={"Authorization": admin_token})
    assert response.status_code == 200


def test_create_user(api_client, admin_token):
    response = api_client.post(
        "/users",
        json={"username": "newuser"},
        headers={"Authorization": admin_token}
    )
    assert response.status_code == 201
```

## Testing Anti-Patterns to Avoid

### Don't Test Implementation Details

```python
# BAD: Testing private methods
def test_internal_validation():
    """Don't test private methods directly."""
    user = User(username="alice")
    assert user._validate_username() is True  # Testing internals


# GOOD: Test public interface
def test_user_creation_validates_username():
    """Test behavior through public interface."""
    with pytest.raises(ValueError):
        User(username="")  # Validation happens implicitly
```

### Don't Use Too Many Mocks

```python
# BAD: Too many mocks - test is brittle and tests nothing
def test_process_order_too_many_mocks(mocker):
    mock_db = mocker.Mock()
    mock_email = mocker.Mock()
    mock_payment = mocker.Mock()
    mock_inventory = mocker.Mock()
    mock_shipping = mocker.Mock()
    # ... testing implementation, not behavior


# GOOD: Mock only external dependencies
def test_process_order_integration(database, mocker):
    mock_email = mocker.patch("myapp.services.EmailService")

    processor = OrderProcessor(database=database)
    processor.process(order)

    # Real database interaction, mocked email
    assert database.get_order(order.id).status == "processed"
    mock_email.send_confirmation.assert_called_once()
```

### Don't Test Third-Party Code

```python
# BAD: Testing Django/Flask/FastAPI internals
def test_django_orm():
    """Don't test that Django ORM works."""
    user = User.objects.create(username="alice")
    retrieved = User.objects.get(id=user.id)
    assert retrieved.username == "alice"  # Testing Django, not your code


# GOOD: Test your business logic
def test_user_service_creates_with_default_role():
    """Test your logic using Django."""
    service = UserService()
    user = service.create_user(username="alice")

    assert user.role == "member"  # Testing YOUR default logic
```

## Test Checklist

Before submitting tests:

### Structure & Organization

- [ ] Tests mirror source code structure
- [ ] Related tests grouped in classes
- [ ] Fixtures in conftest.py for reusability
- [ ] Test names clearly describe scenario and expected behavior

### Fixtures

- [ ] Appropriate fixture scope (function/class/module/session)
- [ ] Fixtures are isolated and don't share state
- [ ] Use factory fixtures for creating multiple instances
- [ ] Autouse fixtures only when necessary

### Parametrization

- [ ] Data-driven tests use `@pytest.mark.parametrize`
- [ ] Parametrize includes readable IDs
- [ ] Edge cases covered in parameters

### Assertions

- [ ] Each test has clear assertions
- [ ] Assertions include helpful messages where needed
- [ ] Exceptions tested with `pytest.raises`
- [ ] Floating point comparisons use `pytest.approx`

### Isolation & Independence

- [ ] Tests don't depend on execution order
- [ ] Each test can run independently
- [ ] No shared state between tests
- [ ] Database/files cleaned up after each test

### Mocking

- [ ] Only external dependencies are mocked
- [ ] Internal logic uses real implementations
- [ ] Mocks verify correct interactions
- [ ] Not over-mocking

### Coverage

- [ ] Happy path tested
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Test behavior, not implementation

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Good Practices](https://docs.pytest.org/en/latest/explanation/goodpractices.html)
- [Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)
- [Python Testing with pytest by Brian Okken](https://pragprog.com/titles/bopytest/python-testing-with-pytest/)
