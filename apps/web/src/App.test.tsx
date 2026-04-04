import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import App from './App'


function mockFetch(routes: Record<string, unknown>) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const method = init?.method ?? 'GET'
    const url = typeof input === 'string' ? input : input.toString()
    const key = `${method} ${url}`
    const payload = routes[key]

    if (payload === undefined) {
      return new Response(JSON.stringify({ message: `Unhandled route: ${key}` }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    return new Response(JSON.stringify(payload), {
      status: method === 'POST' && url === '/api/records' ? 201 : 200,
      headers: { 'Content-Type': 'application/json' },
    })
  })

  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}


describe('V1 Working Tool App', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders recent records on the home page', async () => {
    mockFetch({
      'GET /api/home/recent-records?limit=6': {
        items: [
          {
            id: 'rec-1',
            workspace: 'waterbase',
            title_zh: '南昌清水池高难场景',
            title_en: 'Nanchang High Complexity Water Tank',
            status: 'ready',
            tags: ['CN'],
            created_at: '2026-04-04T08:00:00Z',
            updated_at: '2026-04-04T08:00:00Z',
            summary: '优先评估柔性支架路径。',
          },
        ],
      },
    })

    window.history.pushState({}, '', '/')
    render(<App />)

    expect(await screen.findByText('Recent Records')).toBeInTheDocument()
    expect(await screen.findByText('南昌清水池高难场景')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /open record/i })).toHaveAttribute('href', '/records/rec-1')
  })

  it('keeps save and export disabled while pending and enables them when ready', async () => {
    mockFetch({
      'GET /api/home/recent-records?limit=6': { items: [] },
      'POST /api/workspaces/waterbase/evaluate': {
        state: 'ready',
        title_zh: 'WaterBase | 清水池 | CN',
        title_en: 'WaterBase | Clear Water Tank | CN',
        summary: '该场景适合优先评估柔性支架路径。',
        export_markdown: '# markdown',
        export_text: 'WaterBase Mount export',
        linked_asset_refs: { rule_ids: ['WB-001'], case_ids: ['case_nanchang_water_plant'], gate_ids: [], checklist_ids: [] },
        workspace_specific_result: {
          recommended_path: '优先评估柔性支架路径',
          standardization_level: '非标评审',
          material_direction: '优先采用高防腐等级材料与连接策略',
          region_note: '以国内基线校核为基础。',
          primary_risks: ['高风环境下整体稳定与受力路径风险'],
        },
      },
    })

    window.history.pushState({}, '', '/workspaces/waterbase')
    render(<App />)

    const saveButton = await screen.findByRole('button', { name: /save record/i })
    const exportButton = screen.getByRole('button', { name: /export summary/i })
    expect(saveButton).toBeDisabled()
    expect(exportButton).toBeDisabled()

    const user = userEvent.setup()
    await user.selectOptions(screen.getByLabelText('构筑物类型'), 'clear_water_tank')
    await user.selectOptions(screen.getByLabelText('支撑条件'), 'outer_support_only')

    await waitFor(() => expect(screen.getByText('状态：pending')).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText('优先评估柔性支架路径')).toBeInTheDocument())

    expect(saveButton).toBeEnabled()
    expect(exportButton).toBeEnabled()
  })

  it('requires manual override fields before enabling save', async () => {
    mockFetch({
      'GET /api/home/recent-records?limit=6': { items: [] },
      'POST /api/workspaces/overseas/evaluate': {
        state: 'manual_override',
        title_zh: 'Technical Review | 车棚 / 连廊 / 附属构筑物 | EU',
        title_en: 'Technical Review | Carport Walkway | EU',
        summary: '建议进入专项技术评审。',
        export_markdown: '# markdown',
        export_text: 'Technical Review export',
        linked_asset_refs: {
          rule_ids: [],
          case_ids: [],
          gate_ids: ['project_lifecycle_control_gates'],
          checklist_ids: ['design_institute_audit_checklist'],
        },
        workspace_specific_result: {
          review_conclusion: '进入专项技术评审',
          review_signal: '当前组合未命中静态规则表',
          technical_focus: ['复核项目类型和结构场景是否与现场一致'],
          load_foundation_focus: ['需专项校核荷载传递路径与基础布置边界'],
          design_institute_focus: ['要求设计院补充专项说明和审核结论'],
          risk_alerts: ['现有输入未形成可直接复用的技术结论'],
        },
      },
    })

    window.history.pushState({}, '', '/workspaces/overseas')
    render(<App />)

    const user = userEvent.setup()
    await user.selectOptions(screen.getByLabelText('结构场景'), 'complex_existing_structure')
    await user.selectOptions(screen.getByLabelText('荷载环境'), 'snow')

    const saveButton = await screen.findByRole('button', { name: /save record/i })

    await waitFor(() => expect(screen.getByText('状态：manual_override')).toBeInTheDocument())
    expect(saveButton).toBeDisabled()

    await user.type(screen.getByLabelText('人工结论'), '人工复核后建议专项评审')
    await user.type(screen.getByLabelText('复核备注'), 'Need local institute confirmation')

    await waitFor(() => expect(saveButton).toBeEnabled())
  })
})
