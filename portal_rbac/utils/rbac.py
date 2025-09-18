
ROLES = ("admin","manager","player","auditor")

def can_sync_plugins(role: str) -> bool:
    return role in ("admin",)

def can_review(role: str) -> bool:
    return role in ("admin","manager")

def can_play(role: str) -> bool:
    return role in ("admin","manager","player")

def can_view_reports(role: str) -> bool:
    return role in ("admin","manager","auditor")
