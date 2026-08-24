# Three different “companies”

| Word | Thing | Isolation |
|---|---|---|
| Legal Entity | ERPNext Company (developer GSTIN) | In-house entity switch |
| Channel Company | Atlas Channel Company (agency) | User Permission + query conditions |
| ERPNext Company | Same as Legal Entity in this app | Books of record |

Channel isolation is never done by swapping ERPNext Company. Pink City and Desert Reach are Channel Companies; they must not see each other’s holds, reports, leads, agents, or commissions. Available units are shared stock.

Atlas-3 enforced this only in the UI (L14). ERPATLAS enforces it in `permission_query_conditions` / `has_permission`.
