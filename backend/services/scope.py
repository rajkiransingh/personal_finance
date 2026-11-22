"""Shared helpers for restricting ORM queries to the visible user ids.

`scope is None` means no restriction (used by startup/global jobs). An empty
list means the caller (the admin account) may see no personal data.
"""

OWNER_COLUMNS = ("user_id", "investor", "investor_id")


def owner_column(model):
    for name in OWNER_COLUMNS:
        column = getattr(model, name, None)
        if column is not None:
            return column
    return None


def apply_scope(query, model, scope):
    """Apply an owner filter to a query when a scope is supplied."""
    if scope is None:
        return query
    column = owner_column(model)
    if column is None:
        # A personal table with no owner cannot be shown in a scoped view.
        return query.filter(False)
    return query.filter(column.in_(scope))


def require_owner(owner_id: int, scope) -> None:
    """Reject requests for an owner outside the caller's visible scope."""
    from fastapi import HTTPException

    if scope is not None and owner_id not in scope:
        raise HTTPException(status_code=403, detail="Not allowed for this account")
