# ADR 0003: Preserve quantitative invariants

## Context

Portfolio and risk calculations must preserve mathematical invariants: prices
and weights must be valid, annualization must be consistent, risk ratios must
not invent values, optimizers must converge, and backtests must account for
open positions.

## Decision

Validate finite positive inputs, require unique assets and aligned weights,
return nullable ratios when their denominators are zero, use geometric
annualization and sample covariance consistently, enforce simplex constraints
and convergence for minimum variance, exclude a target asset from its own
factor matrix, and liquidate open positions at the final backtest price.

## Tradeoffs

| Alternative | Tradeoff |
| --- | --- |
| **Invariant-preserving calculations** | Some degenerate inputs return unavailable values or errors; results remain interpretable. |
| Silent clipping and default metrics | Convenient output, but materially misleading risk and performance numbers. |
| Delegate validation to callers | Less library code, but every caller must duplicate fragile rules. |

## Consequences

Consumers must handle nullable metrics and explicit validation errors. Sharpe,
Sortino, Calmar, benchmark statistics, and profit factor are unavailable rather
than fabricated when their required variance, drawdown, or loss denominator is
zero. Returned portfolio numbers are reproducible and bounded.
