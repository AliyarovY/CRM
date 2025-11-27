import pytest
from app.core.permissions import Role, Permission, has_permission, ROLE_PERMISSIONS


class TestPermissions:
    def test_role_enum_values(self):
        assert Role.OWNER.value == "owner"
        assert Role.ADMIN.value == "admin"
        assert Role.MANAGER.value == "manager"
        assert Role.SALES.value == "sales"
        assert Role.VIEWER.value == "viewer"

    def test_permission_enum_values(self):
        assert Permission.READ.value == "read"
        assert Permission.CREATE.value == "create"
        assert Permission.UPDATE.value == "update"
        assert Permission.DELETE.value == "delete"

    def test_owner_has_all_permissions(self):
        assert has_permission(Role.OWNER, Permission.READ)
        assert has_permission(Role.OWNER, Permission.CREATE)
        assert has_permission(Role.OWNER, Permission.UPDATE)
        assert has_permission(Role.OWNER, Permission.DELETE)

    def test_admin_has_most_permissions(self):
        assert has_permission(Role.ADMIN, Permission.READ)
        assert has_permission(Role.ADMIN, Permission.CREATE)
        assert has_permission(Role.ADMIN, Permission.UPDATE)
        assert has_permission(Role.ADMIN, Permission.DELETE)

    def test_manager_has_read_create_update(self):
        assert has_permission(Role.MANAGER, Permission.READ)
        assert has_permission(Role.MANAGER, Permission.CREATE)
        assert has_permission(Role.MANAGER, Permission.UPDATE)
        assert not has_permission(Role.MANAGER, Permission.DELETE)

    def test_sales_has_read_create_update(self):
        assert has_permission(Role.SALES, Permission.READ)
        assert has_permission(Role.SALES, Permission.CREATE)
        assert has_permission(Role.SALES, Permission.UPDATE)
        assert not has_permission(Role.SALES, Permission.DELETE)

    def test_viewer_has_only_read(self):
        assert has_permission(Role.VIEWER, Permission.READ)
        assert not has_permission(Role.VIEWER, Permission.CREATE)
        assert not has_permission(Role.VIEWER, Permission.UPDATE)
        assert not has_permission(Role.VIEWER, Permission.DELETE)

    def test_role_permissions_dict_structure(self):
        assert Role.OWNER in ROLE_PERMISSIONS
        assert Role.ADMIN in ROLE_PERMISSIONS
        assert Role.MANAGER in ROLE_PERMISSIONS
        assert Role.SALES in ROLE_PERMISSIONS
        assert Role.VIEWER in ROLE_PERMISSIONS

    def test_role_permissions_contain_permission_objects(self):
        for role, perms in ROLE_PERMISSIONS.items():
            assert isinstance(perms, set)
            for perm in perms:
                assert isinstance(perm, Permission)
