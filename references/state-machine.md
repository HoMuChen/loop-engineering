# State Machine

Normal flow:

```text
open issue -> loop:ready -> loop:claimed -> loop:in-progress -> loop:pr-open -> loop:done -> closed
```

Repair flow:

```text
loop:pr-open -> loop:repairing -> loop:pr-open
```

Blocked flow:

```text
active state -> loop:blocked + loop:needs-human -> loop:ready
```

Recovery flow:

```text
active state -> run:stale -> resume, reassign, or block
```
