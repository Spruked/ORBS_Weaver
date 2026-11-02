# ral_core

Reference implementation of the Orbot **TTI / RAL control gate**.

The package implements the authority path between a probabilistic proposer and the execution fabric:

```text
WorldState -> RAL proposal -> Core-4 -> Hard Admission -> Execution Permit -> Async Execution Fabric
```

Core-4 does not actuate. A Core-4 `ADMISSIBLE` disposition is necessary but not sufficient for execution. The deterministic Hard Admission Gate must pass and issue a short-lived `ExecutionPermit`.

Absolute rule: **no valid permit, no execution**.

Run:

```bash
python -m ral_core.demo
python -m unittest discover -s tests -v
```
