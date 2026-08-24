# Tally is migration-only

Tally is no longer a live backend. Opening balances and historical vouchers enter through XML import once. After cutover, Journal Entry and Payment Entry in ERPNext are the books. No Atlas code posts to Tally; `/api/tally`-style transports stay retired.

**Consequence:** finance desks reconcile against ERPNext, never Tally. A Tally XML importer may exist under Settings & Integrations as a one-shot tool.
