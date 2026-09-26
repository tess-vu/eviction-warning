<script setup lang="ts">
import { onMounted } from 'vue'
import { useForecastStore } from '@/stores/forecast'
import Sidebar from '@/components/Sidebar.vue'
import KPIStrip from '@/components/KPIStrip.vue'
import MapPanel from '@/components/MapPanel.vue'
import TractTable from '@/components/TractTable.vue'
import EquityPanel from '@/components/EquityPanel.vue'
import Footer from '@/components/Footer.vue'

const store = useForecastStore()
const baseUrl = import.meta.env.BASE_URL

onMounted(async () => {
  await store.loadMonths()
  if (store.selectedMonth) {
    await store.loadForecast()
  }
})
</script>

<template>
  <header role="banner" aria-label="City of Philadelphia header">
    <div class="header-inner">
      <div class="header-left">
        <svg role="img" aria-label="City of Philadelphia" width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <image :href="`${baseUrl}favicon.ico`" width="32" height="32" />
        </svg>
        <span class="wordmark">City of Philadelphia</span>
      </div>
      <div class="header-center">
        <span class="app-title">Eviction Early Warning System</span>
      </div>
      <div class="header-right">
        Forecast: <span id="header-month-text">{{ store.selectedMonth }}</span>
      </div>
    </div>
  </header>

  <div class="app-layout">
    <Sidebar />

    <main role="main" class="main-panel">
      <KPIStrip />
      <MapPanel />
      <TractTable />
      <EquityPanel />

      <div class="safeguard-notice" role="note" aria-label="Ethical safeguard">
        <span class="safeguard-icon">⚠️</span>
        <span class="safeguard-text">
          This tool is FOR PROACTIVE RESOURCE ALLOCATION ONLY. It MUST NOT BE USED FOR ENFORCEMENT,
          PUNITIVE ACTION, OR AUTOMATED DECISION-MAKING OF ANY KIND. Any use outside resource
          allocation requires prior review by the Fair Housing Commission.
        </span>
      </div>

      <Footer />
    </main>
  </div>
</template>

<style scoped>
header[role="banner"] {
  background: var(--philly-blue-dark);
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
}

.header-inner {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left svg { display: block; width: 32px; height: 32px; }

.wordmark {
  color: var(--philly-white);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.header-center .app-title { color: var(--philly-white); font-size: 14px; font-weight: 400; }
.header-right { color: var(--philly-white); font-size: 13px; }
#header-month-text { font-weight: 600; }

.app-layout {
  display: flex;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  background: var(--philly-white);
}

.main-panel {
  flex: 1;
  padding: 20px 24px 0 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.safeguard-notice {
  background: #FEF5E4;
  border-left: 4px solid var(--philly-yellow);
  padding: 12px 16px;
  font-size: 13px;
  color: var(--philly-dark);
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 12px 0 8px 0;
  border-radius: 0;
}

.safeguard-icon { font-size: 18px; line-height: 2; }
.safeguard-text { flex: 1; }

@media (max-width: 1024px) {
  .app-layout { flex-direction: column; }
  .main-panel { padding: 16px; }
}

@media (max-width: 768px) {
  .header-inner { flex-wrap: wrap; height: auto; padding: 8px 0; }
  header[role="banner"] { height: auto; min-height: 56px; padding: 4px 16px; }
  .header-center { order: 3; width: 100%; text-align: center; margin-top: 2px; }
  .header-right { font-size: 12px; }
}
</style>
