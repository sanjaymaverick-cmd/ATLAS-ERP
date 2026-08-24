# Unit is a custom DocType; status changes are compare-and-swap

ERPNext Item / Warehouse cannot express Available → Held → Booked → Sold with a refused concurrent hold. **Atlas Unit** owns status. A hold is `UPDATE … WHERE status = 'Available'`; zero rows means refuse. A live hold is unique per unit (generated `live_unit` column, NULL when not Held).

Callers never assign `status` from a form except Dispute (in-house overflow). Hold, book, release, expire, cancel, and possession go through `property_inventory.lock`.

**Consequence:** tests of the lock are pure functions; the MariaDB compare-and-swap is the only adapter that talks to the database.
