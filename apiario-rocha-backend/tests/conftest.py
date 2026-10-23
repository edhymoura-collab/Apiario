import os


os.environ.setdefault("SECRET_KEY", "test-only-signing-secret-with-more-than-32-characters")
os.environ.setdefault("ADMIN_USERNAME", "test-admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-only-admin-password")
