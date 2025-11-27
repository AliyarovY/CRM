from enum import Enum
from typing import List


class Permission(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_ORGANIZATION = "manage_organization"
    VIEW_REPORTS = "view_reports"


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    SALES = "sales"
    VIEWER = "viewer"


ROLE_PERMISSIONS = {
    Role.OWNER: {
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
        Permission.DELETE,
        Permission.MANAGE_MEMBERS,
        Permission.MANAGE_ORGANIZATION,
        Permission.VIEW_REPORTS,
    },
    Role.ADMIN: {
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
        Permission.DELETE,
        Permission.MANAGE_MEMBERS,
        Permission.VIEW_REPORTS,
    },
    Role.MANAGER: {
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
        Permission.VIEW_REPORTS,
    },
    Role.SALES: {
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
    },
    Role.VIEWER: {
        Permission.READ,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def get_role_permissions(role: Role) -> List[Permission]:
    return list(ROLE_PERMISSIONS.get(role, set()))
