# Epistemic Gravity Field wiring

Cognition/Governance owns the actual `Triple_Predicate_Cubed/Epistemic_Gravity_Field/space_field.py`
32³ CPU substrate. Communication posts an observation for each conversation,
including the voice input path, to loopback port 16524 `/field/observe`.
The four channels encode observation presence, normalized recall count, ASR
confidence and its complement. Text input has no ASR measurement and uses zero.
These input features are not semantic embeddings or truth measurements.

Signals enter the outer shell; four simulation ticks exercise the existing
shell cadences, diffusion, renewal and sampling. Intentional stochastic behavior
is preserved. `/field/status` exposes current diagnostics. State is volatile,
bounded to one field per Cognition process, with no private durable writer.
Conversation records include the returned advisory diagnostics through the
existing AIMS memory interface. No field output promotes claims or grants permits.
Core-4 remains independent of field output. Language generation does not treat
these diagnostics as factual evidence. Field unavailability is explicitly recorded
and does not prevent speech or conversation.

Run all three runtimes with the existing supervisor using the Communication
Python environment (which supplies torch and numpy). Restart the running runtimes
to load this wiring. Live microphone and native playback validation remains separate.
