import type { EvaluateResponse, RecordDetail, RecentRecordItem, Workspace } from '../types'

const REQUEST_TIMEOUT_MS = 10_000

async function request<T>(input: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => {
    controller.abort()
  }, REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(input, {
      ...init,
      signal: controller.signal,
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
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error(`Request timed out after ${REQUEST_TIMEOUT_MS / 1000} seconds`)
    }

    throw error
  } finally {
    window.clearTimeout(timeoutId)
  }
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
