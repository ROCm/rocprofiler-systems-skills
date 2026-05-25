---
name: architecture-tradeoff
description: >-
  Use when architectural decisions involve competing quality attributes
  (performance vs modifiability, availability vs consistency, security vs
  usability), when the user says "tradeoff analysis", "ATAM", "quality
  attributes", "what are we giving up", or when a design choice affects
  multiple non-functional requirements in tension.
---

# Architecture Tradeoff Analysis

Structured method to expose how architectural decisions affect quality attributes in tension. Based on ATAM (Architecture Tradeoff Analysis Method). Produces a decision matrix with sensitivity points, tradeoff points, and risk catalog.

**Complements:** `architecture` (broad modes), `design-review` (component interface options). This skill operates at system/subsystem level analyzing quality attribute tensions.

## When to Use

- Choosing between architectural approaches with competing concerns
- Evaluating an existing architecture against quality requirements
- Stakeholders disagree on priorities (speed vs safety, flexibility vs simplicity)
- Migration decisions with multiple valid paths
- Any "it depends" answer that needs structured decomposition

## When NOT to Use

- Single quality attribute dominance (no tension)
- Component-level interface design (use `design-review`)
- Code-level refactoring (use `code-quality`)

## Process

### 1. Establish Quality Attribute Utility Tree

Elicit and prioritize quality attributes relevant to the system. Each leaf is a concrete, testable scenario.

```
Performance
├── Latency: API response < 50ms p99 under 1k RPS        (H,H)
├── Throughput: Handle 10k concurrent connections          (H,M)
└── Startup: Cold start < 3s                               (M,L)
Modifiability
├── Add new output format in < 1 dev-day                   (H,H)
└── Swap storage backend without API changes               (M,M)
Availability
├── Survive single-node failure without data loss          (H,H)
└── Graceful degradation under 10x load spike              (H,M)
Security
└── Zero trust between internal services                   (M,H)
```

**(importance, difficulty)** — H/M/L for each. Focus analysis on (H,H) and (H,M) scenarios.

**Ask:** "What quality attributes matter most? For each, give me a concrete scenario with measurable criteria."

### 2. Map Architectural Approaches

For each major decision point, identify 2-4 candidate approaches. Keep descriptions factual — no advocacy yet.

| Decision Point | Approach A | Approach B | Approach C |
|----------------|-----------|-----------|-----------|
| Communication  | Sync REST  | Async messaging | gRPC streaming |
| Data storage   | Single SQL DB | Event sourcing | Polyglot persistence |
| Deployment     | Monolith   | Microservices | Modular monolith |

### 3. Analyze Each Approach Against Scenarios

For every (approach, scenario) pair, assess impact:

| Scenario | Approach A | Approach B | Approach C |
|----------|-----------|-----------|-----------|
| API < 50ms p99 | ++ direct call path | -- queue latency | + streaming amortizes |
| Add output format < 1d | - coupled transform | ++ isolated handler | + plugin interface |
| Survive node failure | -- single point | ++ replicated consumers | + reconnect semantics |

Use `++` (strongly supports), `+` (supports), `o` (neutral), `-` (hinders), `--` (strongly hinders).

### 4. Identify Sensitivity and Tradeoff Points

**Sensitivity point:** A property of one approach where a small change in the architecture significantly affects one quality attribute.

> "If we add connection pooling to Approach A, latency drops from '-' to '++'."

**Tradeoff point:** A property that affects two or more quality attributes in opposite directions.

> "Async messaging improves availability (++) but hinders latency (--). These are in direct tension."

Document each explicitly:

```markdown
### Sensitivity Points
- S1: Connection pool size in Approach A — small change flips latency from fail to pass
- S2: Message batch size in Approach B — affects both throughput and consistency

### Tradeoff Points
- T1: Sync vs async communication — latency ↔ availability
- T2: Schema coupling — modifiability ↔ type safety
- T3: Replication factor — availability ↔ consistency ↔ cost
```

### 5. Catalog Risks

A **risk** is an architecturally significant decision that may cause problems. A **non-risk** is a good decision worth documenting.

| ID | Description | Affected Scenarios | Severity |
|----|------------|-------------------|----------|
| R1 | Single DB = SPOF for all services | Availability scenarios | HIGH |
| R2 | Async retry storm under failure | Throughput, availability | MEDIUM |
| NR1 | Circuit breakers on all external calls | Availability | — |
| NR2 | Schema versioning from day one | Modifiability | — |

### 6. Decision Matrix

Weight quality attributes, score approaches, produce recommendation.

```markdown
| Quality Attribute | Weight | Approach A | Approach B | Approach C |
|-------------------|--------|-----------|-----------|-----------|
| Latency (p99)     | 0.30   | 8         | 3         | 7         |
| Modifiability     | 0.25   | 4         | 9         | 7         |
| Availability      | 0.25   | 3         | 8         | 6         |
| Security          | 0.10   | 6         | 6         | 6         |
| Ops complexity    | 0.10   | 9         | 4         | 6         |
| **Weighted Total**|        | **5.65**  | **6.15**  | **6.60**  |
```

Scores 1-10. Weights must sum to 1.0. **Ask user to validate weights before scoring.**

### 7. Recommend with Caveats

State recommendation clearly. Include:

- Which tradeoff points the recommendation accepts
- Which risks it carries and how to mitigate
- Under what changed assumptions the recommendation would flip
- Sensitivity points to monitor post-implementation

**Template:**
> "Recommend **Approach C** (weighted 6.60). Accepts T1 tradeoff (moderate latency for availability). Carries R2 risk — mitigate with backpressure. If latency weight increases to 0.40+, Approach A wins. Monitor S1 (pool sizing) in production."

## Quick Reference

| Step | Output | Key Question |
|------|--------|-------------|
| Utility tree | Prioritized scenarios | "What matters and how much?" |
| Approach map | Candidate table | "What are our options?" |
| Impact analysis | Scenario × approach matrix | "How does each option affect each concern?" |
| Sensitivity/tradeoff | S and T point catalog | "Where are the tensions?" |
| Risk catalog | Risk/non-risk table | "What could go wrong?" |
| Decision matrix | Weighted scores | "Which approach wins given our priorities?" |
| Recommendation | Decision + caveats | "What do we accept and what do we watch?" |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping utility tree — jumping to solutions | Quality scenarios must exist before evaluating approaches |
| Equal weights on everything | Force ranking — if everything matters equally, nothing does |
| Missing tradeoff points | Every `++` paired with a `--` elsewhere is a tradeoff — find them |
| Scoring without scenarios | Scores must trace to specific quality attribute scenarios |
| Ignoring sensitivity points | These are where small implementation choices swing outcomes |
| Presenting matrix without recommendation | Be opinionated — state which approach and why |
| Forgetting reversal conditions | Always state when the recommendation would change |
