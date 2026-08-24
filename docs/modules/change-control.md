# Change Control — RFI, NCR, VO

**Atlas-3:** questions to design, failed work, and paid extra work are separate. Paid extra work waits for a yes.

| Kind | Open action | Close rule |
|---|---|---|
| RFI | Respond (text required) | Response closes |
| NCR | Close after re-inspection | Pass re-inspection required |
| VO / Change | Send for approval | Status follows Atlas Approval kind `Change` |

VO amount is required on the Approval card. The Change handler never creates a Payment Entry.

SLA hours on an RFI are informational (overdue when aging ≥ SLA).
