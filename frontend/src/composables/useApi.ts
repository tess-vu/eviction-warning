import type { TractsResponse, EquityResponse, CampaignAccepted } from '@/types'

// Static mode reads pre-exported JSON (GitHub Pages) otherwise FastAPI serves the routes.
export const STATIC_MODE = import.meta.env.VITE_STATIC === 'true'

const BASE = import.meta.env.BASE_URL.replace(/\/$/, '')

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init)
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`)
  }
  return res.json()
}

export function useApi() {
  return {
    fetchMonths: () =>
      request<{ available_months: string[] }>(
        STATIC_MODE ? '/api/months.json' : '/api/months',
      ),

    fetchTracts: (month: string, topN: number) =>
      request<TractsResponse>(
        STATIC_MODE
          ? `/api/tracts/${month}/${topN}.json`
          : `/api/tracts?month=${month}&top_n=${topN}`,
      ),

    fetchEquity: (month: string) =>
      request<EquityResponse>(
        STATIC_MODE ? `/api/equity/${month}.json` : `/api/equity?month=${month}`,
      ),

    downloadBrief: (month: string, topN: number) => {
      window.open(`${BASE}/api/brief?month=${month}&top_n=${topN}`, '_blank')
    },

    sendCampaign: (month: string, topN: number) =>
      request<CampaignAccepted>('/api/campaign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ month, top_n: topN }),
      }),
  }
}
