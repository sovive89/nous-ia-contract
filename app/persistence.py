"""Contract persistence foundation. Lifecycle operations will be added separately."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, JSON, String, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_contract_tenant_key"),
        UniqueConstraint("tenant_id", "id", name="uq_contract_tenant_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    source_system: Mapped[str] = mapped_column(String(128), nullable=False)
    destination_system: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    versions: Mapped[list["ContractVersion"]] = relationship(back_populates="contract")
    __mapper_args__ = {}
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        UniqueConstraint("tenant_id", "key", name="uq_contract_tenant_key"),
        UniqueConstraint("tenant_id", "id", name="uq_contract_tenant_id"),
    )


class ContractVersion(Base):
    __tablename__ = "contract_versions"
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id", "contract_id"], ["contracts.tenant_id", "contracts.id"]),
        UniqueConstraint("contract_id", "version", name="uq_contract_version"),
        UniqueConstraint("tenant_id", "id", name="uq_version_tenant_id"),
        UniqueConstraint("tenant_id", "contract_id", "id", name="uq_version_contract_id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    contract_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="DRAFT", nullable=False)
    definition_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    definition_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    contract: Mapped[Contract] = relationship(back_populates="versions")


class ContractApproval(Base):
    __tablename__ = "contract_approvals"
    __table_args__ = (ForeignKeyConstraint(["tenant_id", "version_id"], ["contract_versions.tenant_id", "contract_versions.id"]),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(2048))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ContractActivation(Base):
    __tablename__ = "contract_activations"
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id", "contract_id", "version_id"], ["contract_versions.tenant_id", "contract_versions.contract_id", "contract_versions.id"]),
        Index("uq_current_activation", "tenant_id", "contract_id", "environment", unique=True, postgresql_where=__import__("sqlalchemy").text("deactivated_at IS NULL"), sqlite_where=__import__("sqlalchemy").text("deactivated_at IS NULL")),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    contract_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    environment: Mapped[str] = mapped_column(String(64), nullable=False)
    activated_by: Mapped[str] = mapped_column(String(128), nullable=False)
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


def make_engine(url: str | None = None):
    resolved = url or os.environ["DATABASE_URL"]
    return create_engine(resolved, pool_pre_ping=True)


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
