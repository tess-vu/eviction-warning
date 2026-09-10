import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'
import type { TractRecord, KPISummary, EquityResponse } from '@/types'

export const useForecastStore = defineStore('forecast', () => {
  const api = useApi()

  const months = ref<string[]>([])
  const selectedMonth = ref('')
  const topN = ref(50)
  const loading = ref(false)

  const tracts = ref<TractRecord[]>([])
  const kpi = ref<KPISummary | null>(null)
  const equity = ref<EquityResponse | null>(null)

  async function loadMonths() {
    const data = await api.fetchMonths()
    months.value = data.available_months
    if (months.value.length && !selectedMonth.value) {
      selectedMonth.value = months.value[0]
    }
  }

  async function loadForecast() {
    if (!selectedMonth.value) return
    loading.value = true
    try {
      const [tractsRes, equityRes] = await Promise.all([
        api.fetchTracts(selectedMonth.value, topN.value),
        api.fetchEquity(selectedMonth.value),
      ])
      tracts.value = tractsRes.tracts
      kpi.value = tractsRes.kpi
      equity.value = equityRes
    } finally {
      loading.value = false
    }
  }

  return { months, selectedMonth, topN, loading, tracts, kpi, equity, loadMonths, loadForecast }
})
