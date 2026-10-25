from ..config import ROLE_ACCESS


def allowed_roles(role: str) -> list[str]:
    if role not in ROLE_ACCESS:
        raise ValueError(f"unknown role '{role}', expected one of {sorted(ROLE_ACCESS)}")
    return sorted(ROLE_ACCESS[role])
