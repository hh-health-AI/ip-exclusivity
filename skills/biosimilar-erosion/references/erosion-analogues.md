# Choosing erosion analogues

The curve is an empirical question, so the method is: pick analogues that match on
mechanism, not on therapeutic area. Match on these four attributes, in priority order.

1. **Route and site of care.** Pharmacy-dispensed self-injectable behaves very
   differently from clinic-infused buy-and-bill. This matters more than the molecule.
2. **Interchangeability status** at the time of entry, and whether the state
   substitution laws in the major states permitted pharmacy-level switching.
3. **Number of launched (not approved) entrants in year one**, and whether any is a
   large diversified player with existing payer contracts.
4. **Payer channel concentration** — a product whose volume sits with three PBMs
   erodes in steps at contract dates; one spread across many small payers drifts.

## Questions the analogue must answer

- What share of the erosion in year one was price versus volume?
- Did the reference sponsor launch an authorised biosimilar, and what share did it hold?
- Was there a next-generation formulation switch, and what proportion of patients moved
  before entry? (A successful switch can make the erosion curve nearly irrelevant.)
- Where did net price settle at 24 and 36 months, as a percentage of pre-entry net?
- Did the erosion stop? Biologic erosion frequently plateaus well above zero, unlike
  small molecules — the plateau level is usually the most valuable number in the model.

## Common modelling errors

- Applying a small-molecule cliff to a physician-administered biologic.
- Assuming approval equals launch.
- Ignoring the *rebate reset*: the reference sponsor often cuts net price ahead of
  entry to lock multi-year contracts, so revenue falls **before** the LOE date. Check
  gross-to-net trends in the two years pre-entry via `rx-utilization` → gross-to-net-bridge.
- Forgetting ex-US. European biosimilar erosion typically runs faster and started
  earlier; a global model needs two curves. `global-access` owns the ex-US calendar.
