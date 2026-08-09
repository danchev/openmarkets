---
applyTo: '**/*.{py}'
description: This file defines instructions for an autonomous agent to analyze a Python codebase, evaluate it against refactoring and design pattern principles, and propose improvements aligned with Clean Architecture.
---

# Refactoring and Design Pattern Analysis Instructions for Python Codebases

## Overview

This document defines the responsibilities, constraints, and execution strategy for an autonomous agent tasked with analyzing a codebase, evaluating it against established refactoring and design-pattern principles, and proposing improvements aligned with Clean Architecture.

---

## Objective

The agent must:

1. **Ingest and understand the entire codebase** provided.
2. **Reference canonical refactoring and design pattern catalogs**:

   * Refactoring Catalogue — [https://refactoring.guru/refactoring/catalog](https://refactoring.guru/refactoring/catalog)
   * Design Patterns Catalogue — [https://refactoring.guru/design-patterns/catalog](https://refactoring.guru/design-patterns/catalog)
   * Code Smell Catalogue - [https://refactoring.guru/smells/catalog](https://refactoring.guru/smells/catalog)
3. **Assess the codebase** for:

   * Structural deficiencies
   * Abstraction misalignments
   * Domain model issues
   * Architectural boundaries
4. **Propose a detailed technical improvement plan** emphasizing Clean Architecture and professional software engineering principles.

---

## Scope

The agent’s output must include:

* Current state analysis
* Identified issues and anti-patterns
* Proposed architecture and module structure
* Recommended refactorings and design patterns
* Improved data models
* API and boundary definitions
* Transition plan (incremental, non-disruptive)

---

## Ingestion Instructions

When analyzing the codebase:

1. **Parse source files recursively**, including:

   * Language syntax trees
   * Build configurations
   * Dependency manifests
2. **Generate internal representations** for:

   * Modules/Packages
   * Classes/Interfaces
   * Functions/Methods
   * Data models/entities
3. **Identify code smells and anti-patterns**:

   * Long functions or classes
   * Duplicate code
   * Tight coupling
   * Weak cohesion
   * Improper layering

---

## Reference Integration

The agent must **actively use** concepts from:

### Refactoring Catalogue

* Recognize refactoring opportunities
* Map code issues to refactoring patterns
* Prioritize refactorings by risk and impact

### Design Patterns Catalogue

* Identify appropriate object-oriented or architectural patterns
* Recommend patterns where applicable
* Avoid overuse or misapplication

---

## Clean Architecture Principles

Improvements must reflect:

* **Separation of concerns**
* **Explicit boundaries**
* **Dependency inversion**
* **Testability**
* **Loose coupling and high cohesion**

Specifically:

* Entities → Business rules
* Use Cases → Application logic
* Interface Adapters → Controllers/Presenters/Gateways
* Frameworks & Drivers → UI, DB, External APIs

---

## Analysis Tasks

For each component or layer:

1. **Structure Evaluation**

   * Is the layering explicit?
   * Are dependencies inverted correctly?
   * Are modules self-contained?

2. **Abstraction Evaluation**

   * Are interfaces defined for boundaries?
   * Are implementations hidden behind abstractions?

3. **Data Model Evaluation**

   * Are domain models expressive?
   * Do DTOs/VOs reflect consistent invariants?
   * Is persistence leaking into business logic?

---

## Output Requirements

The agent should produce a structured report with:

### 1) Executive Summary

* High-level findings
* Strategic recommendations

### 2) Codebase Map

* Module and layer diagram
* Dependency graph

### 3) Issue Catalogue

For each finding:

* Description
* Location (files/classes/methods)
* Severity
* Impact analysis

### 4) Improvement Plan

For each recommendation:

* What to do (refactor/design pattern/architecture)
* Why (principle, pattern rationale)
* How (detailed steps)
* Example diff/prototype snippets

---

## Recommended Refactorings & Patterns

Examples (the agent must derive from catalogs):

* Encapsulate Collection
* Replace Conditional with Polymorphism
* Extract Interface / Strategy
* Adapter for external dependencies
* Facade for subsystem boundaries
* Repository for persistence abstraction
* State, Observer, Command, Factory, Decorator where appropriate
* Modularization by Bounded Context

---

## Validation and Metrics

Agent must suggest:

* **Automated tests additions**
* **Code quality metrics**

  * Cyclomatic complexity
  * Cohesion metrics
  * Coupling metrics
* **Architectural validation**

  * Layer penetration tests
  * Interface conformance

---

## Delivery Format

Output should be machine-readable and easy to navigate:

* Structured Markdown (tables, sections)
* Optional JSON/DSL for automated tools
* Visual diagrams (ASCII or embed links)

---

## Constraints

* Do not change business semantics without explicit justification
* Preserve API contracts unless otherwise stated
* Prioritize low-risk, high-value improvements
* Maintain buildability and tests pass

---

## Agent Evaluation

Success is measured by:

* Completeness of analysis
* Technical quality of proposals
* Alignment with refactoring/design catalogs
* Clean Architecture compliance
