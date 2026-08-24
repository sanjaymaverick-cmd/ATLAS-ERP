# Native Frappe app on ERPNext

Atlas-1 ADR 0001 and Atlas-3 `docs/finance/ERPNEXT.md` treated Atlas as a sibling operations console that talked to ERPNext over REST and said “do not rebuild Atlas on Frappe.” ERPATLAS reverses that: the product is a custom app inside the ERPNext bench. ERPNext Accounts is the books of record; operations DocTypes live beside them in one site.

**Considered options:** keep the TanStack/Zustand sibling (Atlas-3); rebuild operations in Frappe while posting to a second ERPNext (two sources of truth). Both were rejected — the locked goal is one system and feature parity without a separate frontend.
