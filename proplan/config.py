import os
JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/proplan")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
SMTP_HOST = os.getenv("SMTP_HOST") or ""
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER") or ""
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or ""
SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"
MAIL_FROM = os.getenv("MAIL_FROM", "proplan@example.com")
