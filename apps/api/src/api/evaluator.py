from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Dict, Iterable, List, Tuple

from slugify import slugify

from .assets import AssetCatalog
from .schemas import EvaluateResponse, LinkedAssetRefs, OverseasEvaluateRequest, WaterbaseEvaluateRequest


WATERBASE_LABELS = {
    "structure_type": {
        "clear_water_tank": ("清水池", "Clear Water Tank"),
        "sedimentation_tank": ("沉淀池", "Sedimentation Tank"),
        "water_plant_roof": ("水厂屋面", "Water Plant Roof"),
        "auxiliary_structure": ("附属结构", "Auxiliary Structure"),
    },
    "is_retrofit": {"yes": ("既有改造", "Retrofit"), "no": ("新建", "New Build")},
    "span_level": {"low": ("低", "Low"), "medium": ("中", "Medium"), "high": ("高", "High")},
    "wind_level": {"low": ("低", "Low"), "medium": ("中", "Medium"), "high": ("高", "High")},
    "corrosion_level": {"medium": ("中", "Medium"), "high": ("高", "High")},
    "interference_level": {"low": ("低", "Low"), "medium": ("中", "Medium"), "high": ("高", "High")},
    "om_requirement": {"low": ("低", "Low"), "medium": ("中", "Medium"), "high": ("高", "High")},
    "support_condition": {
        "roof_support_allowed": ("屋面支撑可用", "Roof Support Allowed"),
        "outer_support_only": ("仅外侧落柱", "Outer Support Only"),
        "limited_pool_wall_support": ("池壁支撑受限", "Limited Pool Wall Support"),
        "standard_support_allowed": ("常规支撑可用", "Standard Support Allowed"),
    },
    "target_market": {
        "CN": ("中国 CN", "China"),
        "EU": ("欧洲 EU", "Europe"),
        "US": ("美国 US", "United States"),
        "AU": ("澳洲 AU", "Australia"),
        "JP": ("日本 JP", "Japan"),
    },
}

OVERSEAS_LABELS = {
    "project_type": {
        "new_ground_station": ("新建地面电站", "New Ground Station"),
        "industrial_roof": ("工商业屋顶", "Industrial Roof"),
        "retrofit_roof": ("既有屋面改造", "Retrofit Roof"),
        "carport_walkway": ("车棚 / 连廊 / 附属构筑物", "Carport Walkway"),
    },
    "structure_scenario": {
        "standard_ground": ("常规地面阵列", "Standard Ground"),
        "color_steel_roof": ("彩钢瓦屋面", "Color Steel Roof"),
        "concrete_roof": ("混凝土屋面", "Concrete Roof"),
        "long_span_canopy": ("大跨棚架 / 车棚", "Long Span Canopy"),
        "complex_existing_structure": ("既有复杂构筑物", "Complex Existing Structure"),
    },
    "load_environment": {
        "normal": ("常规", "Normal"),
        "high_wind": ("高风", "High Wind"),
        "snow": ("积雪", "Snow"),
        "corrosion": ("腐蚀", "Corrosion"),
        "seismic": ("抗震控制", "Seismic"),
    },
    "foundation_condition": {
        "conventional": ("常规地基可用", "Conventional Foundation"),
        "restricted_foundation": ("基础布置受限", "Restricted Foundation"),
        "limited_anchor": ("锚固条件受限", "Limited Anchor"),
        "uncertain_geotech": ("地勘边界不清", "Uncertain Geotech"),
        "existing_structure_limited": ("既有结构承载受限", "Existing Structure Limited"),
    },
    "site_constraint": {
        "normal_window": ("常规施工窗口", "Normal Construction Window"),
        "keep_operation": ("生产不停线", "Keep Operation"),
        "short_window": ("短窗口施工", "Short Construction Window"),
        "no_weld": ("禁止动火 / 焊接", "No Welding"),
        "no_anchor_penetration": ("禁止穿透式锚固", "No Penetration Anchor"),
    },
    "target_market": WATERBASE_LABELS["target_market"],
}

WATERBASE_FALLBACK = {
    "recommended_path": "进入专项评审 / Non-standard Review",
    "standardization_level": "非标评审",
    "material_direction": "建议结合场景单独判断",
    "region_note": "当前规则表未完全覆盖该组合，请进入专项技术判断与区域适配评审。",
    "primary_risks": [
        "现有组合不在标准或参数化覆盖范围内",
        "需要进一步核查结构、运维与施工边界",
        "建议前置确认目标市场标准与资料要求",
    ],
    "summary": "该场景组合未命中现有标准化规则，建议进入专项评审，重新确认支撑条件、主要风险和目标市场适配要求。",
}

OVERSEAS_FALLBACK = {
    "review_conclusion": "进入专项技术评审",
    "review_signal": "当前组合未命中静态规则表",
    "technical_focus": [
        "复核项目类型和结构场景是否与现场一致",
        "确认荷载环境是否存在高风、积雪、腐蚀或抗震控制项",
        "核对基础边界、锚固条件和施工窗口限制",
    ],
    "load_foundation_focus": [
        "需专项校核荷载传递路径与基础布置边界",
        "需与地勘、结构和施工单位同步确认可施工条件",
    ],
    "design_institute_focus": [
        "要求设计院补充专项说明和审核结论",
        "必要时输出单独的荷载计算、节点构造和审图清单",
    ],
    "risk_alerts": [
        "现有输入未形成可直接复用的技术结论",
        "建议先进入专项技术评审，再做结构路径收敛",
        "如涉及外部市场，还需同步确认当地审图和资料要求",
    ],
    "summary": "该场景组合未命中现有静态规则，建议进入专项技术评审，重新确认项目边界、荷载与基础条件、设计院审核要点和施工约束。",
}


@dataclass
class Evaluator:
    assets: AssetCatalog

    def evaluate_waterbase(self, request: WaterbaseEvaluateRequest) -> EvaluateResponse:
        payload = sanitize_model(request.model_dump())
        rule = _find_best_match(
            self.assets.waterbase_rules,
            payload,
            field_names=[
                ("structureType", "structure_type", 2),
                ("isRetrofit", "is_retrofit", 1),
                ("spanLevel", "span_level", 1),
                ("windLevel", "wind_level", 1),
                ("corrosionLevel", "corrosion_level", 1),
                ("interferenceLevel", "interference_level", 1),
                ("omRequirement", "om_requirement", 1),
                ("supportCondition", "support_condition", 1),
                ("targetMarket", "target_market", 2),
            ],
            minimum_score=6,
        )

        labels_zh = _labels_for(payload, WATERBASE_LABELS, 0)
        labels_en = _labels_for(payload, WATERBASE_LABELS, 1)
        title_zh = f"WaterBase | {labels_zh['structure_type']} | {payload['target_market']}"
        title_en = f"WaterBase | {labels_en['structure_type']} | {payload['target_market']}"

        if rule is None:
            export_text = self._render_waterbase_text(labels_zh, WATERBASE_FALLBACK)
            return EvaluateResponse(
                state="manual_override",
                title_zh=title_zh,
                title_en=title_en,
                summary=WATERBASE_FALLBACK["summary"],
                export_markdown=_markdown_block(export_text),
                export_text=export_text,
                linked_asset_refs=LinkedAssetRefs(),
                workspace_specific_result=WATERBASE_FALLBACK,
            )

        result = {
            "recommended_path": rule["recommendedPathZh"],
            "standardization_level": rule["standardizationLevelZh"],
            "material_direction": rule["materialDirectionZh"],
            "region_note": rule["regionNoteZh"],
            "primary_risks": rule["primaryRisksZh"],
        }
        export_text = self._render_waterbase_text(
            labels_zh,
            {**result, "summary": rule["summaryZh"]},
        )
        return EvaluateResponse(
            state="ready",
            title_zh=title_zh,
            title_en=title_en,
            summary=rule["summaryZh"],
            export_markdown=_markdown_block(export_text),
            export_text=export_text,
            linked_asset_refs=LinkedAssetRefs(
                rule_ids=[rule["id"]],
                case_ids=_waterbase_case_refs(rule["id"]),
            ),
            workspace_specific_result=result,
        )

    def evaluate_overseas(self, request: OverseasEvaluateRequest) -> EvaluateResponse:
        payload = sanitize_model(request.model_dump())
        rule = _find_best_match(
            self.assets.overseas_rules,
            payload,
            field_names=[
                ("projectType", "project_type", 2),
                ("structureScenario", "structure_scenario", 2),
                ("loadEnvironment", "load_environment", 1),
                ("foundationCondition", "foundation_condition", 1),
                ("siteConstraint", "site_constraint", 1),
                ("targetMarket", "target_market", 2),
            ],
            minimum_score=7,
        )

        labels_zh = _labels_for(payload, OVERSEAS_LABELS, 0)
        labels_en = _labels_for(payload, OVERSEAS_LABELS, 1)
        title_zh = f"Technical Review | {labels_zh['project_type']} | {payload['target_market']}"
        title_en = f"Technical Review | {slugify(labels_en['project_type'])} | {payload['target_market']}"

        if rule is None:
            export_text = self._render_overseas_text(labels_zh, OVERSEAS_FALLBACK)
            return EvaluateResponse(
                state="manual_override",
                title_zh=title_zh,
                title_en=title_en,
                summary=OVERSEAS_FALLBACK["summary"],
                export_markdown=_markdown_block(export_text),
                export_text=export_text,
                linked_asset_refs=LinkedAssetRefs(
                    gate_ids=["project_lifecycle_control_gates"],
                    checklist_ids=["design_institute_audit_checklist"],
                ),
                workspace_specific_result=OVERSEAS_FALLBACK,
            )

        result = {
            "review_conclusion": rule["reviewConclusionZh"],
            "review_signal": rule["reviewSignalZh"],
            "technical_focus": rule["technicalFocusZh"],
            "load_foundation_focus": rule["loadFoundationFocusZh"],
            "design_institute_focus": rule["designInstituteFocusZh"],
            "risk_alerts": rule["riskAlertsZh"],
        }
        export_text = self._render_overseas_text(labels_zh, {**result, "summary": rule["summaryZh"]})
        return EvaluateResponse(
            state="ready",
            title_zh=title_zh,
            title_en=title_en,
            summary=rule["summaryZh"],
            export_markdown=_markdown_block(export_text),
            export_text=export_text,
            linked_asset_refs=LinkedAssetRefs(
                rule_ids=[rule["id"]],
                gate_ids=["project_lifecycle_control_gates"],
                checklist_ids=["design_institute_audit_checklist"],
            ),
            workspace_specific_result=result,
        )

    def _render_waterbase_text(self, labels: Dict[str, str], result: Dict[str, Any]) -> str:
        return (
            "【WaterBase Mount 产品摘要】\n"
            f"目标场景：{labels['structure_type']} / {labels['is_retrofit']} / {labels['target_market']}\n\n"
            "1. 场景判断\n"
            f"- 构筑物类型：{labels['structure_type']}\n"
            f"- 是否既有改造：{labels['is_retrofit']}\n"
            f"- 关键约束：跨度{labels['span_level']}、风环境{labels['wind_level']}、腐蚀{labels['corrosion_level']}、干扰{labels['interference_level']}、运维要求{labels['om_requirement']}、支撑条件{labels['support_condition']}\n\n"
            "2. 推荐路径\n"
            f"- 推荐方案路径：{result['recommended_path']}\n"
            f"- 标准化等级：{result['standardization_level']}\n"
            f"- 材料方向：{result['material_direction']}\n\n"
            "3. 关键风险\n"
            f"{_render_bullets(result['primary_risks'])}\n\n"
            "4. 区域适配提醒\n"
            f"- 目标市场：{labels['target_market']}\n"
            f"- 提醒：{result['region_note']}\n\n"
            "5. 客户可读摘要\n"
            f"{result['summary']}"
        )

    def _render_overseas_text(self, labels: Dict[str, str], result: Dict[str, Any]) -> str:
        return (
            "【Technical Review 摘要】\n"
            f"项目类型：{labels['project_type']}\n"
            f"结构场景：{labels['structure_scenario']}\n"
            f"目标市场：{labels['target_market']}\n"
            f"当前结论：{result['review_conclusion']}\n"
            f"匹配提示：{result['review_signal']}\n\n"
            "1. 前期技术关注点\n"
            f"{_render_bullets(result['technical_focus'])}\n\n"
            "2. 荷载 / 基础评审重点\n"
            f"{_render_bullets(result['load_foundation_focus'])}\n\n"
            "3. 设计院审核要点\n"
            f"{_render_bullets(result['design_institute_focus'])}\n\n"
            "4. 高风险提醒\n"
            f"{_render_bullets(result['risk_alerts'])}\n\n"
            "5. 技术评审摘要\n"
            f"{result['summary']}"
        )


def sanitize_model(payload: Dict[str, Any]) -> Dict[str, Any]:
    sanitized: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str):
            sanitized[key] = escape(value.strip())
        elif isinstance(value, dict):
            sanitized[key] = sanitize_model(value)
        elif isinstance(value, list):
            sanitized[key] = [escape(item.strip()) if isinstance(item, str) else item for item in value]
        else:
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError(f"{key} must be non-negative")
            sanitized[key] = value
    return sanitized


def _find_best_match(
    rules: Iterable[Dict[str, Any]],
    payload: Dict[str, Any],
    field_names: List[Tuple[str, str, int]],
    minimum_score: int,
) -> Dict[str, Any] | None:
    best_rule = None
    best_score = -1
    for rule in rules:
        score = 0
        for rule_key, payload_key, weight in field_names:
            if rule.get(rule_key) == payload.get(payload_key):
                score += weight
        if score > best_score:
            best_score = score
            best_rule = rule
    if best_score < minimum_score:
        return None
    return best_rule


def _labels_for(payload: Dict[str, Any], labels: Dict[str, Dict[str, Tuple[str, str]]], index: int) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for field, mapping in labels.items():
        pair = mapping.get(payload[field])
        result[field] = pair[index] if pair else payload[field]
    return result


def _waterbase_case_refs(rule_id: str) -> List[str]:
    mapping = {
        "WB-001": ["case_nanchang_water_plant"],
        "WB-003": ["case_xiamen_water_plant"],
    }
    return mapping.get(rule_id, [])


def _render_bullets(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _markdown_block(text: str) -> str:
    return "\n".join(f"- {line}" if not line.startswith(("【", "1.", "2.", "3.", "4.", "5.")) and line else line for line in text.splitlines())
