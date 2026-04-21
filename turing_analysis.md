# Turing Completeness Analysis of Clockwork

The Clockwork language is Turing complete because it can simulate an arbitrary **Counter Machine (Minsky Machine)**, which is a well-known Turing-complete model of computation. 

A standard 2-counter Minsky machine requires:
1. Arbitrarily large non-negative integer counters.
2. The ability to increment a counter (`INC`).
3. The ability to decrement a counter and conditionally branch if it is zero (`DEC_JZ`).

### How Clockwork implements this:
1. **Unbounded Counters:** Markers on the rings carry a `value` which is a non-negative integer. As integers are theoretically unbounded in the formal description, they serve as our infinite tape/counters.
2. **Increment (`INC`):** We can use the `gen` operation (inner += 1, outer += 1) or `give` (outer -= 1, inner += 1) to add to a stationary counter marker on Ring 2 by passing a head marker on Ring 1 over it.
3. **Decrement and Branch-on-Zero (`DEC_JZ`):** The `ifzflip` operation changes the global rotation direction if `inner.val == 0`. By keeping our "head" (instruction pointer) on the inner rotating ring (Ring 1) and our "counters" on the outer stationary ring (Ring 2), we can copy a counter's value to the head, decrement it using `take` or `drop`, and use `ifzflip` to branch (bounce) to a different sequence of instructions if the counter was 0. 

Because we can place `ifzflip` "doors" at specific angles, we can create multiple bounded bouncing regions around the 360-degree circle. These regions act as the **states** of a state machine. When a counter is zero, `ifzflip` triggers and the head reverses direction, transitioning to a different state (or executing a loop). When it is non-zero, it passes through the door, transitioning to the next state.

Since Clockwork can simulate unbounded counters and conditional branching via rotational bouncing, it can simulate any Minsky Machine, and is therefore strictly **Turing Complete** (ignoring the practical 256 marker limit and tick limit).
