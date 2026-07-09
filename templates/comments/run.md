<!-- loop-engineering:run v1 -->
Run: {{ run_id }}
Agent: {{ agent }}
Status: {{ status }}
Branch: {{ branch }}
Worktree: {{ worktree }}
PR: {{ pr }}
Started: {{ started }}
Updated: {{ updated }}
Repairs: local {{ local_repairs }}/{{ local_repair_limit }}, pr {{ pr_repairs }}/{{ pr_repair_limit }}

Plan:
{{ plan_items }}

Verification:
{{ verification_items }}

Blockers:
{{ blocker_items }}
<!-- /loop-engineering:run -->
