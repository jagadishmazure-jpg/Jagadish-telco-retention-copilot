# ADR 0004: Gemma 4 E2B, 4-bit, on CPU

**Status:** accepted

**Context.** The copilot answers while the customer is on the line, many times a day, and customer data
should not leave the operator's network.

**Decision.** Gemma 4 E2B in the official quantization-aware Q4_0 GGUF, through llama-cpp-python on 8
CPU threads, greedy decoding, pinned by revision and SHA-256. One call per customer.

**Consequences.** About ten seconds per reply on a shared 8-core CPU. Larger models may read notes
better; none are measured here.
