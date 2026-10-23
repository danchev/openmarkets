# ADR 0007: Require Python 3.11 or newer

## Context

The locked documentation imaging dependency, Pillow 12.3.0, has known security advisories. Pillow 13.0.0 fixes them but requires Python 3.11 or newer. The project already runs its CI matrix on Python 3.11 through 3.14, while package metadata still advertised Python 3.10.

## Decision

Set Python 3.11 as the minimum supported version, remove the Python 3.10 classifier, and lock the documentation imaging stack to the secure Pillow release. Keep the CI matrix aligned with the declared minimum.

## Tradeoffs

| Alternative | Tradeoff |
| --- | --- |
| **Require Python 3.11 or newer** | Removes Python 3.10 compatibility while allowing the full docs imaging stack and its secure Pillow version. |
| Keep Python 3.10 and omit docs imaging there | Preserves the runtime floor but leaves documentation features inconsistent by Python version. |
| Keep Python 3.10 and retain Pillow 12.3.0 | Preserves compatibility while retaining known vulnerabilities. |

## Consequences

The package no longer installs on Python 3.10. Users and deployment environments must use Python 3.11 or newer. The supported floor now matches the existing CI coverage, and the lockfile can use Pillow 13.0.0 without a vulnerable Python 3.10-only resolution.
