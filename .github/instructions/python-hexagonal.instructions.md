---
applyTo: '**/*.{py}'
description: Enforces Hexagonal Architecture (Ports & Adapters) to ensure a clear separation between domain logic and infrastructure concerns in Python systems
---


# Hexagonal Architecture (Ports & Adapters) Instructions for Python

> ⚠️ **Warning:**
> This file defines **non-negotiable architectural rules**.
> Violations create tight coupling, reduce testability, and compromise domain integrity.

---

## Objective

Ensure all code adheres to **Hexagonal Architecture** by:

* Placing the **domain at the center**
* Isolating business logic from frameworks and infrastructure
* Defining all external interactions through **explicit ports**
* Treating infrastructure as **replaceable adapters**
* Enabling deterministic, fast, and framework-free domain testing

---

## Architectural Overview

```
            ┌──────────────────────┐
            │      Adapters         │
            │  (DB, HTTP, MQ, CLI)  │
            └─────────▲────────────┘
                      │
                Outbound Ports
                      │
        ┌─────────────┴─────────────┐
        │          Domain            │
        │  Entities, VOs, Services   │
        │  Policies, Events          │
        └─────────────▲─────────────┘
                      │
                 Inbound Ports
                      │
            ┌─────────┴────────────┐
            │   Application Layer   │
            │   (Use Cases)         │
            └──────────────────────┘
```

**Dependency Rule:**
Dependencies **always point inward**.
Outer layers may depend on inner layers—never the reverse.

---

## Layer Responsibilities

### 1. Domain Layer (Core)

**Contains:**

* Entities
* Value Objects
* Aggregates
* Domain Services
* Domain Events
* Domain Exceptions
* Business Policies

**Must NOT:**

* Import infrastructure libraries
* Know about persistence, transport, or frameworks
* Perform I/O

```python
# ✅ Allowed
from domain.money import Money

# ❌ Forbidden
import sqlalchemy
import fastapi
```

---

### 2. Application Layer (Use Cases)

**Contains:**

* Use case classes
* Command / Query handlers
* Transaction orchestration
* Port coordination

**Responsibilities:**

* Load domain objects via ports
* Invoke domain behavior
* Persist changes via ports
* Publish domain events

**Must NOT:**

* Contain business rules
* Validate domain invariants
* Manipulate domain internals

```python
class PayOrder:
    def execute(self, command):
        order = self.orders.get(command.order_id)
        order.pay()
        self.unit_of_work.commit()
```

---

### 3. Ports

Ports define **what the system needs**, not **how it is done**.

#### Inbound Ports

* Define how the application is driven
* Represent use cases
* Implemented by application services

```python
class PayOrderUseCase(Protocol):
    def execute(self, command: PayOrderCommand) -> None: ...
```

#### Outbound Ports

* Define dependencies on external systems
* Declared as interfaces (Protocols / ABCs)
* Implemented by adapters

```python
class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order: ...
    def add(self, order: Order) -> None: ...
```

---

## Adapters

### 4. Adapters Are Replaceable Details

Adapters:

* Implement ports
* Translate between domain types and external representations
* Contain all framework-specific code

Examples:

* SQLAlchemy repositories
* REST controllers
* Message queue publishers
* CLI handlers

```python
class SqlAlchemyOrderRepository:
    def get(self, order_id): ...
```

Adapters **may depend on**:

* Frameworks
* ORMs
* Serialization libraries

Adapters **must not leak** these details inward.

---

## Dependency Rules (Strict)

### 5. No Inward Knowledge of Adapters

* Domain must not know adapters exist
* Application must not import concrete adapter implementations
* Wiring occurs only at composition roots

```python
# ❌ Bad - application depends on concrete adapter
from infrastructure.db.order_repo import SqlOrderRepository

# ✅ Good - depends on port
from ports.repositories import OrderRepository
```

---

### 6. Composition Root Is the Only Place for Wiring

* Dependency injection occurs only in:

  * `main.py`
  * `bootstrap.py`
  * framework startup files

```python
order_repo = SqlOrderRepository(session)
pay_order = PayOrder(order_repo, uow)
```

No other layer may perform wiring.

---

## Data Flow Rules

### 7. Domain Objects Must Never Cross Boundaries Unmapped

* Adapters translate:

  * HTTP → Commands
  * ORM rows → Domain entities
* Framework models must not leak into the domain

```python
# ❌ Bad
def create_user(request: FastAPIRequest):
    user = User(**request.json())


# ✅ Good
command = CreateUserCommand(...)
use_case.execute(command)
```

---

### 8. Commands and Queries Are Explicit

* Use explicit command/query objects
* Avoid passing primitives across boundaries

```python
@dataclass(frozen=True)
class PayOrderCommand:
    order_id: OrderId
```

---

## Testing Rules

### 9. Domain Tests Are Framework-Free

* Domain tests:

  * Use no mocks for domain behavior
  * Do not touch DB, HTTP, or queues
* Application tests:

  * Use fake or in-memory adapters
* Adapter tests:

  * Test integration with real frameworks

```python
def test_order_payment():
    order.pay()
    assert order.is_paid()
```

---

## Anti-Patterns Copilot Must Avoid

❌ “Service” classes that mix domain + infrastructure
❌ ORMs used as domain entities
❌ Business rules in controllers
❌ Framework annotations in domain classes
❌ Repositories with business logic
❌ Passing dictionaries instead of domain types

---

## Summary for Copilot

When generating code:

1. **Identify the hexagon center (domain)**
2. **Define ports before adapters**
3. **Keep business rules framework-free**
4. **Push complexity to the edges**
5. **Wire dependencies only at startup**
6. **Assume infrastructure will change**

---

## References

* *Architecture Patterns with Python* (Cosmic Python)
* *Hexagonal Architecture* – Alistair Cockburn
* *Clean Architecture* – Robert C. Martin
* *Implementing Domain-Driven Design* – Vaughn Vernon
