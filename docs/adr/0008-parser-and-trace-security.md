# ADR 0008: Enforce secure parser and trace dependencies

## Context

Soup Sieve 2.9.1 has four denial-of-service advisories. All fixes require version 4.0.0 or newer, whose Python minimum is 3.11.5. OpenTelemetry API 1.45.1 also has a traceparent parsing denial-of-service advisory, fixed in 1.45.2. Lockfile changes alone do not protect library consumers or lowest-direct resolution.

## Decision

Require Python >=3.11.5 and explicit security floors of soupsieve>=4.0.0 and opentelemetry-api>=1.45.2. Regenerate the lockfile with CI's uv 0.12.2. Keep the Python 3.11–3.14 CI matrix, which installs current patch releases.

## Tradeoffs

| Alternative | Tradeoff |
| --- | --- |
| **Raise the Python patch floor and enforce dependency floors** | Protects locked and fresh installs; excludes Python 3.11.0–3.11.4. |
| Update only the lockfile | Fresh and lowest-direct installs can remain vulnerable. |
| Suppress advisories | Preserves old environments but retains denial-of-service paths. |

## Consequences

Users on Python 3.11.0–3.11.4 must upgrade. Two indirect dependencies become explicit security constraints; revisit when parent packages enforce equivalent minimums. No application classes or persisted entities change.
