"""Department scope schemas."""

import uuid
from pydantic import BaseModel


class UserDepartmentCreateRequest(BaseModel):
    department_id: uuid.UUID
    is_primary: bool = False


class UserDepartmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    user_id: uuid.UUID
    department_id: uuid.UUID
    is_primary: bool

    model_config = {"from_attributes": True}
