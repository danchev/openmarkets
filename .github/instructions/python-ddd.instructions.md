---
applyTo: '**/*.{py}'
description: Enforces Domain-Driven Design (DDD) principles for Python business domain code, emphasizing explicit domain models, rich behavior, and clear architectural boundaries
---

# Domain-Driven Design (DDD) Instructions for Python

> ⚠️ **Warning:**
> This file defines **core DDD rules and patterns**. These rules must not be weakened, replaced, or contradicted.
> Infrastructure and framework concerns must never leak into the domain model.

---

## Objective

Ensure all business-critical code follows **Domain-Driven Design** principles by:

* Making the **domain model explicit and central**
* Encoding business rules in **behavior-rich objects**
* Enforcing **clear architectural boundaries**
* Preventing anemic domain models
* Supporting long-term evolvability and correctness

---

## Scope and Application

### Primary Scope (Strictly Enforced)

* Aggregates
* Entities
* Value Objects
* Domain Services
* Domain Events
* Domain Policies / Specifications

### Secondary Scope (Partially Enforced)

* Application services / use-case handlers
* Command handlers
* Unit-of-work orchestration

### Explicit Exemptions

* DTOs
* ORM mappings
* API schemas
* Serialization models
* Infrastructure adapters (DB, queues, HTTP, caches)
* Framework glue code

---

## Architectural Boundaries

### 1. The Domain Must Be Pure

* Domain code **must not**:

  * Import infrastructure libraries
  * Depend on frameworks (ORMs, web frameworks, message brokers)
  * Perform I/O (DB, network, filesystem)
* Domain code **may only depend on**:

  * Python standard library
  * Other domain modules

```python
# ❌ Bad - infrastructure leak
class Order:
    def save(self, session):
        session.add(self)


# ✅ Good - pure domain
class Order:
    def mark_paid(self):
        self._status = OrderStatus.PAID
```

---

## Tactical DDD Patterns

### 2. Aggregates Are Consistency Boundaries

* Each aggregate has:

  * A single **Aggregate Root**
  * Full control over its invariants
* External code **must not** mutate entities inside an aggregate directly

```python
# ❌ Bad - bypassing aggregate root
order.line_items.append(item)

# ✅ Good - aggregate enforces invariants
order.add_line_item(item)
```

---

### 3. Entities Have Identity, Value Objects Do Not

**Entities**

* Identified by identity, not attributes
* Equality is based on identity

**Value Objects**

* Immutable
* Equality is based on value
* No identity

```python
# Value Object
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency
```

---

### 4. All Business Logic Lives in the Domain

* No business rules in:

  * Controllers
  * Application services
  * Repositories
* Application services **orchestrate**, they do not decide

```python
# ❌ Bad - business logic in application layer
if order.total > 10_000:
    raise Exception("Limit exceeded")

# ✅ Good - business logic in domain
order.ensure_limit_not_exceeded()
```

---

## Domain Modeling Rules

### 5. Use Ubiquitous Language Everywhere

* Class names, methods, and variables **must reflect domain language**
* Avoid technical or generic names (`data`, `manager`, `handler`, `utils`)

```python
# ❌ Bad
class Processor:
    def handle(self): ...


# ✅ Good
class OrderApprovalPolicy:
    def approve(self, order): ...
```

Copilot must **never invent generic abstractions** when a domain concept exists.

---

### 6. Prefer Explicit Types Over Primitives

* All meaningful domain concepts must be modeled explicitly
* Primitive obsession is forbidden in domain code

```python
# ❌ Bad
def charge(amount: int, currency: str): ...


# ✅ Good
def charge(money: Money): ...
```

---

### 7. Domain Services Only When Behavior Does Not Belong to an Entity

* Domain services:

  * Are stateless
  * Express domain operations spanning multiple aggregates or concepts
* If behavior fits naturally on an entity or value object, it must live there

```python
class ExchangeRateService:
    def convert(self, money: Money, target_currency: Currency) -> Money: ...
```

---

## Application Layer Rules

### 8. Application Services Orchestrate, Never Contain Logic

* Application services:

  * Load aggregates
  * Call domain behavior
  * Persist results
* They must not:

  * Validate business rules
  * Compute domain decisions

```python
class PlaceOrder:
    def execute(self, command):
        order = self.orders.get(command.order_id)
        order.place()
        self.uow.commit()
```

---

### 9. Repositories Are Collection-Like Interfaces

* Repositories:

  * Hide persistence details
  * Act like in-memory collections
* No query logic in domain code

```python
class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order: ...
    def add(self, order: Order) -> None: ...
```

---

## Domain Events

### 10. Use Domain Events to Signal Important State Changes

* Domain events:

  * Are immutable
  * Represent facts that already happened
  * Are raised inside domain objects

```python
class Order:
    def mark_paid(self):
        self._status = OrderStatus.PAID
        self._events.append(OrderPaid(self.id))
```

---

## Modeling Constraints

### 11. Avoid Anemic Domain Models

Copilot must **never** generate:

* Entities with only fields and getters
* Domain models where logic lives in services instead of entities

If a class has no behavior, it is likely:

* A Value Object
* Or not a domain concept at all

---

### 12. Explicit Invariants Over Implicit Assumptions

* Invariants must be:

  * Enforced at construction time
  * Enforced on state transitions
* Invalid states must be unrepresentable

```python
class Quantity:
    def __init__(self, value: int):
        if value <= 0:
            raise ValueError("Quantity must be positive")
        self._value = value
```

---

## Testing Guidance (For Copilot)

* Prefer **behavioral tests**
* Test through public domain APIs
* Avoid asserting internal state unless unavoidable

```python
def test_order_cannot_be_paid_twice():
    order.mark_paid()
    with pytest.raises(InvalidState):
        order.mark_paid()
```

---

## Summary for Copilot

When generating code:

1. **Model the domain first**
2. **Use rich domain objects**
3. **Push logic inward**
4. **Keep boundaries explicit**
5. **Prefer clarity over cleverness**
6. **Reflect the business language exactly**

---

## References

* *Architecture Patterns with Python* (Cosmic Python) – Percival & Gregory
* *Domain-Driven Design* – Eric Evans
* *Implementing Domain-Driven Design* – Vaughn Vernon
* *Clean Architecture* – Robert C. Martin
