# Site — diary and inspections

**Atlas-3:** one diary per device per day. Failed inspection raises an NCR (failed work report).

**Language:** Site is the physical place of work, not the Project.

## Atlas Site Diary

Sealed with unique `seal_key` = `{project}::{date}::{device_key}`. Second seal same device+date is refused.

## Atlas Inspection

Pending → Pass or Fail (once). Fail inserts **Atlas Change Item** kind `ncr` (Change Control). That is not an Approval and not a Payment Entry.

VO money and RFI flow stay for the Change Control slice.
