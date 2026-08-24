# Channel & Partner (this slice)

**Invariant:** Pink City never sees Desert Reach. Isolation is query conditions + User Permission on **Atlas Channel Company**, not ERPNext Company.

## This slice

- **Atlas Daily Report** — one per agent per calendar day. Channel hold is refused until today’s report exists (`atlas_has_today_report` → `channel.adapter.has_today_report`).
- **Role fixtures** — the eleven Atlas roles in `erpatlas/fixtures/role.json`. User Permission rows stay site data (invite agent), not production fixtures.

## Also in this module

- **Atlas Channel Agent** — roster (User + Channel Company). On save, a **User Permission** is created at runtime. That is site data, not a fixture.
- **Exclusive project lock** — Project `atlas_exclusive_channel_company`. Another Channel Company cannot hold. In-house (no channel) still can.

WhatsApp send stays out.
