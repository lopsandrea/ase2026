# Limitations and Threats to Validity

> The paper enumerates these limitations in §5 and §6.4. We restate them
> here next to the code so reviewers can map each limitation to a concrete
> module rather than a vague disclaimer.

## Hard limitations of the framework

### 1. Authentication paths beyond username + password

Doc2Test runs the login as the *first task* of every workflow, with the
test credentials carried inside the UAT and the session maintained by
the `WebDriver` instance.

- **Out of scope:** CAPTCHAs, 2FA, OAuth redirect flows, single sign-on
  with MFA, magic-link emails. These need out-of-band handling outside
  the document-driven paradigm. The framework will not silently bypass
  them — it will surface a Phase-3 timeout and the Coordinator will
  abort with a clear error rather than retry.

### 2. Shadow DOM and Canvas rendering

The Phase-2 DOM Reader extracts `document.documentElement.outerHTML`,
which crosses light-DOM boundaries but **not** Shadow DOM roots, and
ignores anything painted on `<canvas>`.

- **Practical consequence:** components implemented with Shadow DOM
  (e.g., some Lit / Stencil libraries) and canvas-rendered elements
  (e.g., maps, charts) are invisible to the Selenium Generator.

### 3. Document quality is the bottleneck (Lesson L1)

Vague requirements yield coarse-grained tasks. The Phase-1 chain
mitigates this through the Atomicity Enforcer and Context Enricher, but
ultimately a UAT that says ``complete the booking process'' carries
strictly less information than one that says ``select the cabin of type
X, click Continue, fill the personal-data form''.

- **Practical consequence:** organisations without structured UAT
  documentation will need a bootstrapping effort. We treat this as an
  adoption prerequisite, not a framework defect.

## Threats to validity (paper §5, "Threats to validity")

### LLM probabilism

The framework relies on probabilistic models. Long-term stability under
model updates requires further analysis. We mitigate this in the
replication package with a deterministic disk cache so the published
numbers are reproducible bit-for-bit; live re-runs may diverge.

### Three-month deployment, single industrial partner

The §5 impact figures (`–2.6 person-days/sprint`, `flaky rate 11.4 % →
4.6 %`, `time-to-first-run 3.5 h → 12 min`) are deployment data from a
single partner. They should be read as a deployment report, not a
controlled experiment.

### NDA on the industrial subject

Five of six evaluation subjects originate from Wideverse, which may
implicitly bias the prompt templates towards in-house conventions. The
external RealWorld subject and the four open-sourced internal apps are
our partial mitigations.

- **What reviewers can verify directly:** the 5 OSS subjects + RealWorld
  (50 RQ1 runs + 150 RQ2 mutants).
- **What reviewers cannot verify directly:** the 4 industrial scenarios
  (40 RQ1 runs + 30 RQ2 mutants), which appear as redacted JSON traces
  under `traces/industrial_redacted/`.

## Out of scope for this paper (future work)

- Automatic suite re-generation triggered by frontend pull requests.
- On-premise LLM deployment for data-residency constraints.
- Shadow DOM and Canvas rendering support.
- Cross-browser parity beyond Chrome.
