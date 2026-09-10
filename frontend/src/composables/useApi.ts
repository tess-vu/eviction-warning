import type { TractsResponse, EquityResponse, CampaignAccepted } from '@/types'

const BASE = ''

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init)
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`)
  }
  return res.json()
}

export function useApi() {
  return {
    fetchMonths: () => request<{ available_months: string[] }>('/api/months'),

    fetchTracts: (month: string, topN: number) =>
      request<TractsResponse>(`/api/tracts?month=${month}&top_n=${topN}`),

    fetchEquity: (month: string) =>
      request<EquityResponse>(`/api/equity?month=${month}`),

    downloadBrief: (month: string, topN: number) => {
      window.open(`/api/brief?month=${month}&top_n=${topN}`, '_blank')
    },

    sendCampaign: (month: string, topN: number) =>
      request<CampaignAccepted>('/api/campaign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ month, top_n: topN }),
      }),
  }
}
