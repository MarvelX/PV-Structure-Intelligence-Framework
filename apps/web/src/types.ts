export type RecordState = 'idle' | 'pending' | 'ready' | 'error' | 'manual_override'
export type Workspace = 'waterbase' | 'overseas'

export interface LinkedAssetRefs {
  rule_ids: string[]
  case_ids: string[]
  gate_ids: string[]
  checklist_ids: string[]
}

export interface EvaluateResponse {
  state: RecordState
  title_zh: string
  title_en: string
  summary: string
  export_markdown: string
  export_text: string
  linked_asset_refs: LinkedAssetRefs
  workspace_specific_result: Record<string, unknown>
}

export interface RecentRecordItem {
  id: string
  workspace: Workspace
  title_zh: string
  title_en: string
  status: RecordState
  tags: string[]
  created_at: string
  updated_at: string
  summary: string
}

export interface RecordDetail extends RecentRecordItem {
  manual_override: null | {
    conclusion: string
    note: string
  }
  input: Record<string, unknown>
  output: Record<string, unknown>
  exports: {
    markdown: string
    text: string
    files: string[]
    errors: string[]
  }
  links: LinkedAssetRefs
}

export interface RecordUpdatePayload {
  summary: string
  tags: string[]
  manual_override: null | {
    conclusion: string
    note: string
  }
  expected_updated_at: string
}
