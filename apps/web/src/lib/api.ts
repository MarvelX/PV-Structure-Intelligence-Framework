import type { EvaluateResponse, RecordDetail, RecentRecordItem, Workspace } from '../types'

async function request<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function fetchRecentRecords(limit = 6) {
  return request<{ items: RecentRecordItem[] }>(`/api/home/recent-records?limit=${limit}`)
}

export function fetchRecord(recordId: string) {
  return request<RecordDetail>(`/api/records/${recordId}`)
}

export function evaluateWorkspace<TValues>(workspace: Workspace, payload: TValues) {
  return request<EvaluateResponse>(`/api/workspaces/${workspace}/evaluate`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function saveRecord(payload: unknown) {
  return request<RecordDetail>('/api/records', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
