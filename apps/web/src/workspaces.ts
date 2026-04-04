import type { Workspace } from './types'

export interface SelectOption {
  value: string
  label: string
}

export interface WorkspaceField {
  name: string
  label: string
  options: SelectOption[]
}

export interface WorkspaceConfig<TValues extends Record<string, string>> {
  workspace: Workspace
  route: string
  title: string
  headline: string
  description: string
  heroTag: string
  evaluateActionLabel: string
  manualConclusionLabel: string
  manualNoteLabel: string
  fields: WorkspaceField[]
  defaultValues: TValues
}

export interface WaterbaseFormValues {
  [key: string]: string
  structure_type: string
  is_retrofit: string
  span_level: string
  wind_level: string
  corrosion_level: string
  interference_level: string
  om_requirement: string
  support_condition: string
  target_market: string
}

export interface OverseasFormValues {
  [key: string]: string
  project_type: string
  structure_scenario: string
  load_environment: string
  foundation_condition: string
  site_constraint: string
  target_market: string
}

export const waterbaseConfig: WorkspaceConfig<WaterbaseFormValues> = {
  workspace: 'waterbase',
  route: '/workspaces/waterbase',
  title: 'WaterBase Mount Workspace',
  headline: 'WaterBase Mount 场景化预选型工作台',
  description: '面向水厂既有构筑物场景，快速判断标准化边界、推荐路径和客户可读摘要。',
  heroTag: 'Decision Guidance',
  evaluateActionLabel: '实时推演中',
  manualConclusionLabel: '人工结论',
  manualNoteLabel: '复核备注',
  defaultValues: {
    structure_type: 'water_plant_roof',
    is_retrofit: 'yes',
    span_level: 'high',
    wind_level: 'high',
    corrosion_level: 'high',
    interference_level: 'high',
    om_requirement: 'high',
    support_condition: 'roof_support_allowed',
    target_market: 'CN',
  },
  fields: [
    {
      name: 'structure_type',
      label: '构筑物类型',
      options: [
        { value: 'clear_water_tank', label: '清水池' },
        { value: 'sedimentation_tank', label: '沉淀池' },
        { value: 'water_plant_roof', label: '水厂屋面' },
        { value: 'auxiliary_structure', label: '附属结构' },
      ],
    },
    {
      name: 'is_retrofit',
      label: '是否既有改造',
      options: [
        { value: 'yes', label: '是' },
        { value: 'no', label: '否' },
      ],
    },
    {
      name: 'span_level',
      label: '跨度等级',
      options: [
        { value: 'low', label: '低' },
        { value: 'medium', label: '中' },
        { value: 'high', label: '高' },
      ],
    },
    {
      name: 'wind_level',
      label: '风环境等级',
      options: [
        { value: 'low', label: '低' },
        { value: 'medium', label: '中' },
        { value: 'high', label: '高' },
      ],
    },
    {
      name: 'corrosion_level',
      label: '腐蚀环境等级',
      options: [
        { value: 'medium', label: '中' },
        { value: 'high', label: '高' },
      ],
    },
    {
      name: 'interference_level',
      label: '干扰等级',
      options: [
        { value: 'low', label: '低' },
        { value: 'medium', label: '中' },
        { value: 'high', label: '高' },
      ],
    },
    {
      name: 'om_requirement',
      label: '运维通道要求',
      options: [
        { value: 'low', label: '低' },
        { value: 'medium', label: '中' },
        { value: 'high', label: '高' },
      ],
    },
    {
      name: 'support_condition',
      label: '支撑条件',
      options: [
        { value: 'roof_support_allowed', label: '屋面支撑可用' },
        { value: 'outer_support_only', label: '仅外侧落柱' },
        { value: 'limited_pool_wall_support', label: '池壁支撑受限' },
        { value: 'standard_support_allowed', label: '常规支撑可用' },
      ],
    },
    {
      name: 'target_market',
      label: '目标市场',
      options: [
        { value: 'CN', label: '中国 CN' },
        { value: 'EU', label: '欧洲 EU' },
        { value: 'US', label: '美国 US' },
        { value: 'AU', label: '澳洲 AU' },
        { value: 'JP', label: '日本 JP' },
      ],
    },
  ],
}

export const overseasConfig: WorkspaceConfig<OverseasFormValues> = {
  workspace: 'overseas',
  route: '/workspaces/overseas',
  title: 'Overseas PV Technical Review Workspace',
  headline: 'Overseas PV Structural Technical Framework Workspace',
  description: '把前期技术评审、设计院审核要点和风险闭环收敛到一个实时工作台。',
  heroTag: 'Technical Review',
  evaluateActionLabel: '评审推演中',
  manualConclusionLabel: '人工结论',
  manualNoteLabel: '复核备注',
  defaultValues: {
    project_type: 'carport_walkway',
    structure_scenario: 'standard_ground',
    load_environment: 'normal',
    foundation_condition: 'restricted_foundation',
    site_constraint: 'normal_window',
    target_market: 'EU',
  },
  fields: [
    {
      name: 'project_type',
      label: '项目类型',
      options: [
        { value: 'new_ground_station', label: '新建地面电站' },
        { value: 'industrial_roof', label: '工商业屋顶' },
        { value: 'retrofit_roof', label: '既有屋面改造' },
        { value: 'carport_walkway', label: '车棚 / 连廊 / 附属构筑物' },
      ],
    },
    {
      name: 'structure_scenario',
      label: '结构场景',
      options: [
        { value: 'standard_ground', label: '常规地面阵列' },
        { value: 'color_steel_roof', label: '彩钢瓦屋面' },
        { value: 'concrete_roof', label: '混凝土屋面' },
        { value: 'long_span_canopy', label: '大跨棚架 / 车棚' },
        { value: 'complex_existing_structure', label: '既有复杂构筑物' },
      ],
    },
    {
      name: 'load_environment',
      label: '荷载环境',
      options: [
        { value: 'normal', label: '常规' },
        { value: 'high_wind', label: '高风' },
        { value: 'snow', label: '积雪' },
        { value: 'corrosion', label: '腐蚀' },
        { value: 'seismic', label: '抗震控制' },
      ],
    },
    {
      name: 'foundation_condition',
      label: '地基 / 基础条件',
      options: [
        { value: 'conventional', label: '常规地基可用' },
        { value: 'restricted_foundation', label: '基础布置受限' },
        { value: 'limited_anchor', label: '锚固条件受限' },
        { value: 'uncertain_geotech', label: '地勘边界不清' },
        { value: 'existing_structure_limited', label: '既有结构承载受限' },
      ],
    },
    {
      name: 'site_constraint',
      label: '现场施工约束',
      options: [
        { value: 'normal_window', label: '常规施工窗口' },
        { value: 'keep_operation', label: '生产不停线' },
        { value: 'short_window', label: '短窗口施工' },
        { value: 'no_weld', label: '禁止动火 / 焊接' },
        { value: 'no_anchor_penetration', label: '禁止穿透式锚固' },
      ],
    },
    {
      name: 'target_market',
      label: '目标市场',
      options: [
        { value: 'CN', label: '中国 CN' },
        { value: 'EU', label: '欧洲 EU' },
        { value: 'US', label: '美国 US' },
        { value: 'AU', label: '澳洲 AU' },
        { value: 'JP', label: '日本 JP' },
      ],
    },
  ],
}
