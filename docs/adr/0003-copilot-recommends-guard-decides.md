# ADR 0003: The copilot recommends, the guard decides what the desk sees

**Status:** accepted

**Context.** A language model can misread eligibility, invent numbers, read out contact details or obey
an instruction typed into a note.

**Decision.** Every reply is checked in code before a desk agent sees it. Anything that fails is
replaced by the uplift model's offer with a neutral talk track and flagged for a supervisor. The raw
reply, the issues and the final offer are all stored.

**Consequences.** A wrong reply costs a supervisor a minute, not a refund. The raw failure rates stay
visible in the report, so the guard does not hide how often the model is wrong.
