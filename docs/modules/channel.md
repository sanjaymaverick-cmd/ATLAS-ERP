# Channel & Partner (this slice)

**Invariant:** Pink City never sees Desert Reach. Isolation is query conditions + User Permission on **Atlas Channel Company**, not ERPNext Company.

## This slice

- **Atlas Daily Report** — one per agent per calendar day. Channel hold is refused until today’s report exists (`atlas_has_today_report` → `channel.adapter.has_today_report`).
- **Role fixtures** — the eleven Atlas roles in `erpatlas/fixtures/role.json`. User Permission rows stay site data (invite agent), not production fixtures.

## Not in this slice

Agent roster UI, exclusive project lock, leads isolation (needs `channel_company` on Lead), WhatsApp.
