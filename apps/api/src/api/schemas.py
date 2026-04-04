from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


Workspace = Literal["waterbase", "overseas"]
RecordState = Literal["idle", "pending", "ready", "error", "manual_override"]


class ManualOverridePayload(BaseModel):
    conclusion: str = Field(min_length=1)
    note: str = Field(min_length=1)


class LinkedAssetRefs(BaseModel):
    rule_ids: List[str] = Field(default_factory=list)
    case_ids: List[str] = Field(default_factory=list)
    gate_ids: List[str] = Field(default_factory=list)
    checklist_ids: List[str] = Field(default_factory=list)


class ExportPayload(BaseModel):
    markdown: str = Field(min_length=1)
    text: str = Field(min_length=1)
    files: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class RecentRecordItem(BaseModel):
    id: str
    workspace: Workspace
    title_zh: str
    title_en: str
    status: RecordState
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    summary: str


class RecentRecordsResponse(BaseModel):
    items: List[RecentRecordItem]


class RecordResponse(RecentRecordItem):
    manual_override: Optional[ManualOverridePayload] = None
    input: Dict[str, Any]
    output: Dict[str, Any]
    exports: ExportPayload
    links: LinkedAssetRefs


class RecordCreateRequest(BaseModel):
    workspace: Workspace
    title_zh: str = Field(min_length=1)
    title_en: str = Field(min_length=1)
    status: RecordState
    summary: str = Field(min_length=1)
    tags: List[str] = Field(default_factory=list)
    manual_override: Optional[ManualOverridePayload] = None
    input: Dict[str, Any]
    output: Dict[str, Any]
    exports: ExportPayload
    links: LinkedAssetRefs = Field(default_factory=LinkedAssetRefs)

    @field_validator("status")
    @classmethod
    def validate_saveable_status(cls, value: RecordState) -> RecordState:
        if value not in {"ready", "manual_override"}:
            raise ValueError(f"Only ready/manual_override records can be saved, got {value}")
        return value

    @model_validator(mode="after")
    def validate_manual_override_requirements(self) -> "RecordCreateRequest":
        if self.status == "manual_override" and self.manual_override is None:
            raise ValueError("manual_override records require a manual_override payload")
        return self


class WaterbaseEvaluateRequest(BaseModel):
    structure_type: str
    is_retrofit: str
    span_level: str
    wind_level: str
    corrosion_level: str
    interference_level: str
    om_requirement: str
    support_condition: str
    target_market: str
    engineering_inputs: Dict[str, float] = Field(default_factory=dict)
    constraint_notes: str = ""


class OverseasEvaluateRequest(BaseModel):
    project_type: str
    structure_scenario: str
    load_environment: str
    foundation_condition: str
    site_constraint: str
    target_market: str
    engineering_inputs: Dict[str, float] = Field(default_factory=dict)
    compliance_notes: str = ""


class EvaluateResponse(BaseModel):
    state: RecordState
    title_zh: str
    title_en: str
    summary: str
    export_markdown: str
    export_text: str
    linked_asset_refs: LinkedAssetRefs
    workspace_specific_result: Dict[str, Any]
