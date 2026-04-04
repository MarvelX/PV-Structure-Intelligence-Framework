import { evaluateWorkspace } from './api'


describe('api request timeout', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it(
    'rejects evaluate requests that exceed the timeout budget',
    async () => {
    vi.useFakeTimers()

    vi.stubGlobal(
      'fetch',
      vi.fn((_input: RequestInfo | URL, init?: RequestInit) => {
        return new Promise((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () => {
            reject(new DOMException('The operation was aborted.', 'AbortError'))
          })
        })
      }),
    )

    const promise = evaluateWorkspace('waterbase', {
      structure_type: 'clear_water_tank',
    })
    const expectation = expect(promise).rejects.toThrow('Request timed out after 10 seconds')

    await vi.advanceTimersByTimeAsync(10000)

    await expectation
    },
    15000,
  )
})
