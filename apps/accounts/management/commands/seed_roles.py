from django.core.management.base import BaseCommand
from accounts.models import Permission, Role


PERMISSIONS_DATA = [
    # Church & Settings
    ("churches.manage_settings", "Manage Church Profile & Settings", "churches"),
    ("accounts.manage_users", "Manage Users & Roles", "accounts"),
    ("accounts.view_audit_logs", "View System Audit Logs", "accounts"),
    # Members
    ("members.view", "View Member Registry", "members"),
    ("members.add", "Register New Members", "members"),
    ("members.change", "Edit Member Profiles", "members"),
    ("members.deactivate", "Soft-Delete / Deactivate Members", "members"),
    ("members.export", "Export Member Rosters", "members"),
    # Baptism & Certificates
    ("baptism.view", "View Baptism Records", "baptism"),
    ("baptism.manage", "Register & Edit Baptism Records", "baptism"),
    ("baptism.generate_certificate", "Generate Official PDF Certificates", "baptism"),
    # Departments & Ministries
    ("departments.view", "View Departments & Ministries", "departments"),
    ("departments.manage", "Create & Manage Departments/Ministries", "departments"),
    ("departments.manage_own", "Manage Assigned Department/Ministry Roster", "departments"),
    # Events & Attendance
    ("events.view", "View Church Events", "events"),
    ("events.manage", "Create & Schedule Church Events", "events"),
    ("attendance.record", "Record Service & Event Attendance", "attendance"),
    # Visitors & Pastoral Care
    ("visitors.view", "View Visitors & Follow-ups", "visitors"),
    ("visitors.manage", "Register & Assign Visitor Follow-ups", "visitors"),
    ("pastoral.view_confidential", "View Confidential Pastoral Care Logs", "pastoral"),
    ("pastoral.manage_confidential", "Create & Edit Confidential Pastoral Care Logs", "pastoral"),
    # Reports & Announcements
    ("reports.view_dashboard", "View Executive Dashboard & Analytics", "reports"),
    ("reports.export", "Export Analytical Reports", "reports"),
    ("announcements.view", "View Internal Announcements", "announcements"),
    ("announcements.manage", "Publish & Manage Announcements", "announcements"),
]

ROLES_MATRIX = {
    "System Administrator": {
        "slug": "system-administrator",
        "description": "Full system configuration, user administration, and audit oversight.",
        "perms": [p[0] for p in PERMISSIONS_DATA],
    },
    "Senior Pastor / Clergy": {
        "slug": "senior-pastor-clergy",
        "description": "Church-wide oversight, analytics, and confidential pastoral care management.",
        "perms": [
            "members.view", "baptism.view", "departments.view", "events.view",
            "visitors.view", "visitors.manage", "pastoral.view_confidential",
            "pastoral.manage_confidential", "reports.view_dashboard", "reports.export",
            "announcements.view", "announcements.manage",
        ],
    },
    "Church Secretary / Administrator": {
        "slug": "church-secretary",
        "description": "Membership registry, event scheduling, certificates, and administrative records.",
        "perms": [
            "members.view", "members.add", "members.change", "members.deactivate", "members.export",
            "baptism.view", "baptism.manage", "baptism.generate_certificate",
            "departments.view", "departments.manage", "events.view", "events.manage",
            "attendance.record", "visitors.view", "visitors.manage",
            "reports.view_dashboard", "announcements.view", "announcements.manage",
        ],
    },
    "Department / Ministry Leader": {
        "slug": "department-leader",
        "description": "Manages assigned department/ministry roster, activities, and attendance.",
        "perms": [
            "members.view", "departments.view", "departments.manage_own",
            "events.view", "attendance.record", "announcements.view",
        ],
    },
    "Records Officer": {
        "slug": "records-officer",
        "description": "Manages approved member and baptism certificate records.",
        "perms": [
            "members.view", "members.add", "members.change",
            "baptism.view", "baptism.manage", "baptism.generate_certificate",
            "announcements.view",
        ],
    },
    "Attendance Officer": {
        "slug": "attendance-officer",
        "description": "Records service attendance and registers first-time visitors.",
        "perms": [
            "members.view", "events.view", "attendance.record",
            "visitors.view", "visitors.manage", "announcements.view",
        ],
    },
    "Church Member": {
        "slug": "church-member",
        "description": "Standard congregant access to public announcements and self-service requests.",
        "perms": ["events.view", "announcements.view"],
    },
}


class Command(BaseCommand):
    help = "Seeds default ChurchHub RBAC permissions and configurable role templates."

    def handle(self, *args, **options):
        perm_objs = {}
        for code, name, module in PERMISSIONS_DATA:
            perm, _ = Permission.objects.update_or_create(
                code=code,
                defaults={"name": name, "module": module},
            )
            perm_objs[code] = perm

        for role_name, config in ROLES_MATRIX.items():
            role, _ = Role.objects.update_or_create(
                slug=config["slug"],
                defaults={
                    "name": role_name,
                    "description": config["description"],
                    "is_system_role": True,
                },
            )
            role.permissions.set([perm_objs[c] for c in config["perms"]])

        self.stdout.write(self.style.SUCCESS("Successfully seeded 25 permissions and 7 role templates."))