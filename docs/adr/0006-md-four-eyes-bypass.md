# MD four-eyes bypass stays on until product flips it

Atlas-3 lets Atlas Developer Admin act on any pending Approval, including items waiting on another seat. That is a four-eyes hole (the MD can originate and then approve). It is deliberate in Atlas-3 (`docs/decisions/four-eyes.md`) and **not silently turned off**.

ERPATLAS copies the default: `md_bypass_four_eyes` on Atlas Settings is checked. Uncheck to scope the MD like every other waiter. Do not flip the default without updating this file.

**Status:** recorded, not changed.
