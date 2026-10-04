"""Schemas for module entitlements and tenant runtime configuration."""

import uuid

from pydantic import BaseModel, Field


class ModuleResponse(BaseModel):
    id: uuid.UUID
    key: str
    name: str
    description: str | None
    is_core: bool
    is_active: bool
    enabled: bool = False


class TenantModuleUpdateRequest(BaseModel):
    enabled: bool
    config: dict = Field(default_factory=dict)


class TenantBrandingResponse(BaseModel):
    name: str
    logo_url: str | None
    favicon_url: str | None
    primary_color: str | None
    secondary_color: str | None
    accent_color: str | None


class TenantRuntimeConfigResponse(BaseModel):
    tenant_id: uuid.UUID
    branding: TenantBrandingResponse
    modules: list[ModuleResponse]


class TenantBrandingUpdateRequest(BaseModel):
    display_name: str | None = Field(None, max_length=255)
    logo_url: str | None = Field(None, max_length=2048)
    favicon_url: str | None = Field(None, max_length=2048)
    primary_color: str | None = Field(None, max_length=20)
    secondary_color: str | None = Field(None, max_length=20)
    accent_color: str | None = Field(None, max_length=20)
