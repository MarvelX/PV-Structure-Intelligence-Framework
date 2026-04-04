import { useEffect, useRef, useState } from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { QueryClient, QueryClientProvider, useMutation, useQuery } from '@tanstack/react-query'
import { useForm, useWatch, type DefaultValues, type FieldPath } from 'react-hook-form'

import './App.css'
import { evaluateWorkspace, fetchRecentRecords, fetchRecord, saveRecord } from './lib/api'
import type { EvaluateResponse, RecordState } from './types'
import { overseasConfig, waterbaseConfig, type WorkspaceConfig } from './workspaces'

function AppShell() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">
          <span>PV Structure Intelligence Framework</span>
          <strong>V1 Working Tool</strong>
        </Link>
        <nav className="topnav">
          <Link to="/">Home</Link>
          <Link to={waterbaseConfig.route}>WaterBase</Link>
          <Link to={overseasConfig.route}>Technical Review</Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path={waterbaseConfig.route} element={<WorkspacePage config={waterbaseConfig} />} />
        <Route path={overseasConfig.route} element={<WorkspacePage config={overseasConfig} />} />
        <Route path="/records/:recordId" element={<RecordDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}


function HomePage() {
  const { data } = useQuery({
    queryKey: ['recent-records'],
    queryFn: () => fetchRecentRecords(6),
  })

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">Local Product + Technical Decision Workbench</p>
          <h1>从静态 Demo 升级为可工作的本地工具</h1>
          <p className="hero-copy">
            在同一个入口下，完成场景录入、实时推演、摘要导出、手动保存和记录回看。
          </p>
        </div>
        <aside className="hero-panel">
          <span>Current Scope</span>
          <strong>2 Workspaces / Local SQLite / Export-Ready</strong>
        </aside>
      </section>

      <section className="home-grid">
        <article className="workspace-card workspace-card-water">
          <p className="card-tag">WaterBase Mount</p>
          <h2>WaterBase Mount Workspace</h2>
          <p>面向水厂构筑物、既有改造和多市场适配的场景化预选型工作台。</p>
          <div className="card-actions">
            <Link className="action-button primary" to={waterbaseConfig.route}>
              Open Workspace
            </Link>
            <Link className="action-button secondary" to={waterbaseConfig.route}>
              New WaterBase Record
            </Link>
          </div>
        </article>

        <article className="workspace-card workspace-card-review">
          <p className="card-tag">Technical Review</p>
          <h2>Overseas PV Technical Review Workspace</h2>
          <p>面向海外结构技术评审、设计院审核和高风险闭环的前期工作台。</p>
          <div className="card-actions">
            <Link className="action-button primary" to={overseasConfig.route}>
              Open Workspace
            </Link>
            <Link className="action-button secondary" to={overseasConfig.route}>
              New Technical Review Record
            </Link>
          </div>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="section-tag">Record Center</p>
            <h2>Recent Records</h2>
          </div>
          <span className="section-note">默认展示最近 6 条</span>
        </div>
        <div className="recent-list">
          {data?.items.length ? (
            data.items.map((item) => (
              <article className="recent-card" key={item.id}>
                <p className="recent-meta">
                  <span>{item.workspace}</span>
                  <span>{item.status}</span>
                </p>
                <h3>{item.title_zh}</h3>
                <p>{item.summary}</p>
                <Link className="inline-link" to={`/records/${item.id}`}>
                  Open Record
                </Link>
              </article>
            ))
          ) : (
            <div className="empty-state">No saved records yet. Start from one of the two workspaces.</div>
          )}
        </div>
      </section>
    </main>
  )
}


function WorkspacePage<TValues extends Record<string, string>>({
  config,
}: {
  config: WorkspaceConfig<TValues>
}) {
  const navigate = useNavigate()
  const { register, control, getValues } = useForm<TValues>({
    defaultValues: config.defaultValues as DefaultValues<TValues>,
  })
  const values = useWatch({ control }) as TValues
  const valuesSignature = JSON.stringify(values)
  const [machineState, setMachineState] = useState<RecordState>('idle')
  const [result, setResult] = useState<EvaluateResponse | null>(null)
  const [error, setError] = useState('')
  const [manualConclusion, setManualConclusion] = useState('')
  const [manualNote, setManualNote] = useState('')
  const requestVersion = useRef(0)
  const isFirstRender = useRef(true)

  const saveMutation = useMutation({
    mutationFn: (payload: unknown) => saveRecord(payload),
    onSuccess: (savedRecord) => navigate(`/records/${savedRecord.id}`),
  })

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }

    const version = requestVersion.current + 1
    requestVersion.current = version

    const timer = window.setTimeout(() => {
      const nextValues = JSON.parse(valuesSignature) as TValues
      evaluateWorkspace(config.workspace, nextValues)
        .then((evaluation) => {
          if (requestVersion.current !== version) return
          setResult(evaluation)
          setMachineState(evaluation.state)
        })
        .catch((mutationError: Error) => {
          if (requestVersion.current !== version) return
          setResult(null)
          setMachineState('error')
          setError(mutationError.message)
        })
    }, 250)

    return () => window.clearTimeout(timer)
  }, [config.workspace, valuesSignature])

  const canSave = Boolean(
    result &&
      (machineState === 'ready' ||
        (machineState === 'manual_override' && manualConclusion.trim() && manualNote.trim())),
  )

  const canExport = Boolean(
    result &&
      (machineState === 'ready' ||
        (machineState === 'manual_override' && manualConclusion.trim() && manualNote.trim())),
  )

  const saveCurrentRecord = () => {
    if (!result) return

    saveMutation.mutate({
      workspace: config.workspace,
      title_zh: result.title_zh,
      title_en: result.title_en,
      status: machineState,
      summary: result.summary,
      tags: [config.workspace, String(getValues().target_market ?? '')].filter(Boolean),
      manual_override:
        machineState === 'manual_override'
          ? {
              conclusion: manualConclusion,
              note: manualNote,
            }
          : null,
      input: getValues(),
      output: result.workspace_specific_result,
      exports: {
        markdown: result.export_markdown,
        text: result.export_text,
      },
      links: result.linked_asset_refs,
    })
  }

  const exportSummary = () => {
    if (!result) return
    const blob = new Blob([result.export_text], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${result.title_en.replaceAll(' ', '-').toLowerCase()}.txt`
    link.click()
    URL.revokeObjectURL(url)
  }

  const resultRows = result ? Object.entries(result.workspace_specific_result) : []

  return (
    <main className="page">
      <section className="workspace-hero">
        <div>
          <p className="eyebrow">{config.title}</p>
          <h1>{config.headline}</h1>
          <p className="hero-copy">{config.description}</p>
        </div>
        <aside className="hero-panel">
          <span>Mode</span>
          <strong>{config.heroTag}</strong>
        </aside>
      </section>

      <section className="workspace-layout">
        <form className="panel form-panel">
          <div className="panel-heading">
            <div>
              <p className="section-tag">Input</p>
              <h2>分段表单区</h2>
            </div>
            <span className="status-chip">状态：{machineState}</span>
          </div>

          <div className="field-grid">
            {config.fields.map((field) => (
              <label key={field.name} className="field">
                <span>{field.label}</span>
                <select
                  {...register(field.name as FieldPath<TValues>, {
                    onChange: () => {
                      setMachineState('pending')
                      setError('')
                    },
                  })}
                >
                  {field.options.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            ))}
          </div>

          {machineState === 'manual_override' ? (
            <div className="manual-panel">
              <label className="field">
                <span>{config.manualConclusionLabel}</span>
                <textarea value={manualConclusion} onChange={(event) => setManualConclusion(event.target.value)} />
              </label>
              <label className="field">
                <span>{config.manualNoteLabel}</span>
                <textarea value={manualNote} onChange={(event) => setManualNote(event.target.value)} />
              </label>
            </div>
          ) : null}

          <div className="action-row">
            <button
              className="action-button primary"
              disabled={!canSave || saveMutation.isPending}
              onClick={(event) => {
                event.preventDefault()
                saveCurrentRecord()
              }}
              type="button"
            >
              Save Record
            </button>
            <button
              className="action-button secondary"
              disabled={!canExport}
              onClick={(event) => {
                event.preventDefault()
                exportSummary()
              }}
              type="button"
            >
              Export Summary
            </button>
          </div>
        </form>

        <aside className="panel result-panel">
          <div className="panel-heading">
            <div>
              <p className="section-tag">Result</p>
              <h2>粘性结果卡</h2>
            </div>
            <span className="section-note">{config.evaluateActionLabel}</span>
          </div>

          {machineState === 'idle' ? (
            <div className="empty-state">调整任意关键字段后，系统会自动进入实时推演。</div>
          ) : null}

          {machineState === 'error' ? <div className="error-banner">{error || 'Local backend error'}</div> : null}

          {result ? (
            <div className="result-content">
              <h3>{result.title_zh}</h3>
              <p className="summary">{result.summary}</p>
              <div className="result-grid">
                {resultRows.map(([key, value]) => (
                  <div className="metric" key={key}>
                    <span className="metric-label">{key}</span>
                    <span className="metric-value">{renderMetricValue(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </aside>
      </section>
    </main>
  )
}


function RecordDetailPage() {
  const { recordId = '' } = useParams()
  const { data } = useQuery({
    queryKey: ['record', recordId],
    queryFn: () => fetchRecord(recordId),
  })

  if (!data) {
    return (
      <main className="page">
        <section className="panel">
          <div className="empty-state">Loading record...</div>
        </section>
      </main>
    )
  }

  return (
    <main className="page">
      <section className="panel detail-hero">
        <div>
          <p className="section-tag">{data.workspace}</p>
          <h1>{data.title_zh}</h1>
          <p className="summary">{data.summary}</p>
        </div>
        <span className="status-chip">状态：{data.status}</span>
      </section>

      <section className="detail-grid">
        <DetailBlock title="输入快照" content={data.input} />
        <DetailBlock title="输出详情" content={data.output} />
        <DetailBlock title="导出内容" content={data.exports} />
        <DetailBlock title="关联资产" content={data.links} />
      </section>
    </main>
  )
}


function DetailBlock({ title, content }: { title: string; content: unknown }) {
  return (
    <section className="panel detail-block">
      <h2>{title}</h2>
      <pre>{JSON.stringify(content, null, 2)}</pre>
    </section>
  )
}


function renderMetricValue(value: unknown) {
  if (Array.isArray(value)) return value.join(' / ')
  if (typeof value === 'object' && value !== null) return JSON.stringify(value)
  return String(value)
}


export default function App() {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
