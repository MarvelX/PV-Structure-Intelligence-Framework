import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import App from './App'


function mockFetch(
  routes: Record<
    string,
    unknown | ((input: RequestInfo | URL, init?: RequestInit) => unknown | Promise<unknown>)
  >,
) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const method = init?.method ?? 'GET'
    const url = typeof input === 'string' ? input : input.toString()
    const key = `${method} ${url}`
    const resolver = routes[key]
    const payload = typeof resolver === 'function' ? await resolver(input, init) : resolver

    if (payload === undefined) {
      if (method === 'DELETE') {
        return new Response(null, { status: 204 })
      }

      return new Response(JSON.stringify({ message: `Unhandled route: ${key}` }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (method === 'DELETE') {
      return new Response(null, { status: 204 })
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
    vi.restoreAllMocks()
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

  it('deletes a recent record from the home page', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const fetchMock = mockFetch({
      'GET /api/home/recent-records?limit=6': { items: [] },
      'DELETE /api/records/rec-1': null,
    })

    fetchMock.mockImplementationOnce(async () =>
      new Response(
        JSON.stringify({
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
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        },
      ),
    )

    window.history.pushState({}, '', '/')
    render(<App />)

    expect(await screen.findByText('南昌清水池高难场景')).toBeInTheDocument()

    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: '删除记录 南昌清水池高难场景' }))

    await waitFor(() =>
      expect(screen.getByText('No saved records yet. Start from one of the two workspaces.')).toBeInTheDocument(),
    )
  })

  it('does not delete a recent record when confirmation is cancelled', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    const fetchMock = mockFetch({
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
      'DELETE /api/records/rec-1': null,
    })

    window.history.pushState({}, '', '/')
    render(<App />)

    expect(await screen.findByText('南昌清水池高难场景')).toBeInTheDocument()

    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: '删除记录 南昌清水池高难场景' }))

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(screen.getByText('南昌清水池高难场景')).toBeInTheDocument()
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

  it('updates editable fields on the record detail page', async () => {
    let patchBody: Record<string, unknown> | null = null

    mockFetch({
      'GET /api/home/recent-records?limit=6': { items: [] },
      'GET /api/records/rec-1': {
        id: 'rec-1',
        workspace: 'overseas',
        title_zh: '日本既有屋面抗震评审',
        title_en: 'JP Retrofit Roof Seismic Review',
        status: 'manual_override',
        tags: ['JP', 'retrofit'],
        created_at: '2026-04-04T08:00:00Z',
        updated_at: '2026-04-04T08:00:00Z',
        summary: 'Need manual conclusion before final sign-off.',
        manual_override: {
          conclusion: '人工复核后建议专项评审',
          note: 'Need local institute confirmation',
        },
        input: { project_type: 'retrofit_roof' },
        output: { review_conclusion: '进入专项技术评审' },
        exports: {
          markdown: '# JP Retrofit Roof Seismic Review',
          text: 'JP Retrofit Roof Seismic Review',
          files: [],
          errors: [],
        },
        links: {
          rule_ids: ['TR-003'],
          case_ids: [],
          gate_ids: ['project_lifecycle_control_gates'],
          checklist_ids: ['design_institute_audit_checklist'],
        },
      },
      'PATCH /api/records/rec-1': async (_input: RequestInfo | URL, init?: RequestInit) => {
        patchBody = JSON.parse(String(init?.body ?? '{}')) as Record<string, unknown>
        return {
          id: 'rec-1',
          workspace: 'overseas',
          title_zh: '日本既有屋面抗震评审',
          title_en: 'JP Retrofit Roof Seismic Review',
          status: 'manual_override',
          tags: ['JP', 'retrofit', 'edited'],
          created_at: '2026-04-04T08:00:00Z',
          updated_at: '2026-04-05T08:00:00Z',
          summary: '人工复核后，建议带条件进入专项技术评审。',
          manual_override: {
            conclusion: '人工复核后建议带条件专项评审',
            note: 'Need local institute seismic memo',
          },
          input: { project_type: 'retrofit_roof' },
          output: { review_conclusion: '进入专项技术评审' },
          exports: {
            markdown: '# JP Retrofit Roof Seismic Review',
            text: 'JP Retrofit Roof Seismic Review',
            files: [],
            errors: [],
          },
          links: {
            rule_ids: ['TR-003'],
            case_ids: [],
            gate_ids: ['project_lifecycle_control_gates'],
            checklist_ids: ['design_institute_audit_checklist'],
          },
        }
      },
    })

    window.history.pushState({}, '', '/records/rec-1')
    render(<App />)

    const user = userEvent.setup()
    const summaryField = await screen.findByLabelText('摘要')
    const tagsField = screen.getByLabelText('标签')
    const conclusionField = screen.getByLabelText('人工结论')
    const noteField = screen.getByLabelText('复核备注')

    await user.clear(summaryField)
    await user.type(summaryField, '人工复核后，建议带条件进入专项技术评审。')
    await user.clear(tagsField)
    await user.type(tagsField, 'JP, retrofit, edited')
    await user.clear(conclusionField)
    await user.type(conclusionField, '人工复核后建议带条件专项评审')
    await user.clear(noteField)
    await user.type(noteField, 'Need local institute seismic memo')
    await user.click(screen.getByRole('button', { name: /save changes/i }))

    await waitFor(() => expect(screen.getByText('保存成功')).toBeInTheDocument())
    expect(screen.getByDisplayValue('人工复核后，建议带条件进入专项技术评审。')).toBeInTheDocument()
    expect(patchBody).toMatchObject({
      summary: '人工复核后，建议带条件进入专项技术评审。',
      tags: ['JP', 'retrofit', 'edited'],
      expected_updated_at: '2026-04-04T08:00:00Z',
      manual_override: {
        conclusion: '人工复核后建议带条件专项评审',
        note: 'Need local institute seismic memo',
      },
    })
  })

  it('renders export text without escaped newline gibberish on the record detail page', async () => {
    mockFetch({
      'GET /api/home/recent-records?limit=6': { items: [] },
      'GET /api/records/rec-1': {
        id: 'rec-1',
        workspace: 'waterbase',
        title_zh: '南昌清水池高难场景',
        title_en: 'Nanchang High Complexity Water Tank',
        status: 'ready',
        tags: ['CN'],
        created_at: '2026-04-04T08:00:00Z',
        updated_at: '2026-04-04T08:00:00Z',
        summary: '优先评估柔性支架路径。',
        manual_override: null,
        input: { structure_type: 'clear_water_tank' },
        output: { recommended_path: '优先评估柔性支架路径' },
        exports: {
          markdown: '# Heading\nLine 2',
          text: '第一行\n第二行',
          files: [],
          errors: [],
        },
        links: {
          rule_ids: ['WB-001'],
          case_ids: ['case_nanchang_water_plant'],
          gate_ids: [],
          checklist_ids: [],
        },
      },
    })

    window.history.pushState({}, '', '/records/rec-1')
    render(<App />)

    expect(await screen.findByText((content) => content.includes('第一行') && content.includes('第二行'))).toBeInTheDocument()
    expect(screen.queryByText(/\\n第二行/)).not.toBeInTheDocument()
  })
})
