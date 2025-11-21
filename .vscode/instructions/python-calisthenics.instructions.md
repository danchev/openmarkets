---
applyTo: '**/*.{py}'
description: Enforces Object Calisthenics principles for business domain code to ensure clean, maintainable, and robust code in Python
---
# Object Calisthenics Rules for Python

> ⚠️ **Warning:** This file contains the 9 original Object Calisthenics rules. No additional rules must be added, and none of these rules should be replaced or removed.
> Examples may be added later if needed.

## Objective
This rule enforces the principles of Object Calisthenics to ensure clean, maintainable, and robust code in Python, **primarily for business domain code**.

## Scope and Application
- **Primary focus**: Business domain classes (aggregates, entities, value objects, domain services)
- **Secondary focus**: Application layer services and use case handlers
- **Exemptions**:
  - DTOs (Data Transfer Objects)
  - API models/contracts
  - Configuration classes
  - Simple data containers without business logic
  - Infrastructure code where flexibility is needed

## Key Principles

### 1. One Level of Indentation per Method:
- Keep methods simple and limit the level of indentation to one.

```python
# Bad Example - multiple levels of indentation
def send_newsletter():
    for user in users:
        if user.is_active:
            # Do something
            mailer.send(user.email)

# Good Example - Extracted method to reduce indentation
def send_newsletter():
    for user in users:
        send_email(user)

def send_email(user):
    if user.is_active:
        mailer.send(user.email)
````

### 2. Don't Use the ELSE Keyword:

* Avoid using `else` to simplify control flow. Use early returns or fail fast.

```python
# Bad Example - Using else
def process_order(order):
    if order.is_valid:
        # Process order
    else:
        # Handle invalid order

# Good Example - Avoiding else
def process_order(order):
    if not order.is_valid:
        return  # early return to handle invalid case
    # Process order
```

* Fail Fast principle example:

```python
def process_order(order):
    if order is None:
        raise ValueError("Order cannot be None")
    if not order.is_valid:
        raise ValueError("Invalid order")
    # Process order
```

### 3. Wrapping All Primitives and Strings:

* Avoid using primitive types directly. Wrap them in classes to provide context and behavior.

```python
# Bad Example - Using primitive types directly
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# Good Example - Wrapping primitives
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = Age(age)

class Age:
    def __init__(self, value):
        if value < 0:
            raise ValueError("Age cannot be negative")
        self.value = value
```

### 4. First Class Collections:

* Encapsulate collections in classes that also provide behavior.

```python
# Bad Example - Exposing raw collection
class Group:
    def __init__(self, id, name, users):
        self.id = id
        self.name = name
        self.users = users

    def count_active_users(self):
        return sum(1 for user in self.users if user.is_active)

# Good Example - Encapsulating collection behavior
class Group:
    def __init__(self, id, name, user_collection):
        self.id = id
        self.name = name
        self.user_collection = user_collection

    def count_active_users(self):
        return self.user_collection.count_active()

class UserCollection:
    def __init__(self, users):
        self.users = users

    def count_active(self):
        return sum(1 for user in self.users if user.is_active)
```

### 5. One Dot per Line:

* Limit the number of method calls on a single line.

```python
# Bad Example - Multiple dots in a single line
def process_order(order):
    user_email = order.user.get_email().upper().strip()

# Good Example - One dot per line
def process_order(order):
    user = order.user
    email = user.get_email()
    user_email = email.upper().strip()
```

### 6. Don't Abbreviate:

* Use clear and descriptive names for classes, methods, and variables. Avoid abbreviations that may confuse others.

```python
# Bad Example - Abbreviated names
class U:
    def __init__(self, n):
        self.n = n

# Good Example - Meaningful names
class User:
    def __init__(self, name):
        self.name = name
```

### 7. Keep Entities Small:

* Limit class and method size to improve readability and maintainability.

  * Max 10 methods per class
  * Max 50 lines per class
  * Max 10 classes per module

```python
# Bad Example - Large class with multiple responsibilities
class UserManager:
    def create_user(self, name): pass
    def delete_user(self, id): pass
    def send_email(self, email): pass

# Good Example - Small classes with single responsibility
class UserCreator:
    def create_user(self, name): pass

class UserDeleter:
    def delete_user(self, id): pass

class EmailSender:
    def send_email(self, email): pass
```

### 8. No Classes with More Than Two Instance Variables:

* Keep classes simple by limiting instance variables to two.

```python
# Bad Example - Class with too many instance variables
class UserCreateHandler:
    def __init__(self, user_repo, email_service, logger, sms_service):
        self.user_repo = user_repo
        self.email_service = email_service
        self.logger = logger
        self.sms_service = sms_service

# Good Example - Class with two instance variables
class UserCreateHandler:
    def __init__(self, user_repo, notification_service):
        self.user_repo = user_repo
        self.notification_service = notification_service
```

### 9. No Getters/Setters in Domain Classes:

* Avoid using getters and setters. Use private attributes and static methods for object creation.

```python
# Bad Example - Domain class with getters and setters
class User:
    def __init__(self, name):
        self.name = name

# Good Example - Domain class with encapsulation
class User:
    def __init__(self, name):
        self._name = name

    @classmethod
    def create(cls, name):
        return cls(name)
```

## Implementation Guidelines

* **Domain Classes**:

  * Use private constructors and static factory methods for creating instances.
  * Avoid exposing setters for properties.
  * Apply all 9 rules strictly for business domain code.

* **Application Layer**:

  * Apply these rules to use case handlers and application services.
  * Focus on maintaining single responsibility and clean abstractions.

* **DTOs and Data Objects**:

  * Rules 3 (wrapping primitives), 8 (two instance variables), and 9 (no getters/setters) may be relaxed for DTOs.
  * Public properties with getters/setters are acceptable for data transfer objects.

* **Testing**:

  * Ensure tests validate the behavior of objects rather than their state.
  * Test classes may have relaxed rules for readability and maintainability.

* **Code Reviews**:

  * Enforce these rules during code reviews for domain and application code.
  * Be pragmatic about infrastructure and DTO code.

## References

* [Object Calisthenics - Original 9 Rules by Jeff Bay](https://www.cs.helsinki.fi/u/luontola/tdd-2009/ext/ObjectCalisthenics.pdf)
* [ThoughtWorks - Object Calisthenics](https://www.thoughtworks.com/insights/blog/object-calisthenics)
* [Clean Code: A Handbook of Agile Software Craftsmanship - Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
