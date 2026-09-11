<script setup lang="ts">
import { onMounted } from 'vue'
import { useForecastStore } from '@/stores/forecast'
import Sidebar from '@/components/Sidebar.vue'
import KPIStrip from '@/components/KPIStrip.vue'
import MapPanel from '@/components/MapPanel.vue'
import TractTable from '@/components/TractTable.vue'
import EquityPanel from '@/components/EquityPanel.vue'
import { useApi } from '@/composables/useApi'
import { ref } from 'vue'

const store = useForecastStore()
const api = useApi()

const campaignSending = ref(false)
const campaignStatus = ref('')
const campaignError = ref(false)

onMounted(async () => {
  await store.loadMonths()
  if (store.selectedMonth) {
    await store.loadForecast()
  }
})

function downloadPdf() {
  api.downloadBrief(store.selectedMonth, store.topN)
}

async function sendCampaign() {
  campaignSending.value = true
  campaignStatus.value = ''
  campaignError.value = false
  try {
    const res = await api.sendCampaign(store.selectedMonth, store.topN)
    campaignStatus.value = `Campaign started. Check outputs/campaign_report_${store.selectedMonth.replace('-', '_')}.json`
  } catch (e: any) {
    campaignStatus.value = e.message || 'Campaign request failed'
    campaignError.value = true
  } finally {
    campaignSending.value = false
  }
}
</script>

<template>
  <header role="banner" aria-label="City of Philadelphia header">
    <div class="header-inner">
      <div class="header-left">
        <svg role="img" aria-label="City of Philadelphia" width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <image href="/public/favicon.ico" width="32" height="32" />
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

      <footer role="contentinfo">
        <div class="footer-inner">
          <div class="footer-left">
            Office of Homeless Services · Fair Housing Commission
          </div>
          <div class="footer-right">
            <button id="generate-pdf-btn" class="btn-outline" @click="downloadPdf">
              Generate PDF Brief
            </button>
            <button
              id="send-campaign-btn"
              class="btn-outline"
              :disabled="campaignSending"
              @click="sendCampaign"
            >
              {{ campaignSending ? 'Sending…' : 'Send Monthly Campaign (Mock)' }}
            </button>
          </div>
        </div>
        <div
          id="campaign-status"
          aria-live="polite"
          :class="{ success: !campaignError && campaignStatus, error: campaignError }"
        >
          {{ campaignStatus }}
        </div>
        <div class="footer-attribution">
          Data Sources: Eviction Lab, OpenDataPhilly, U.S. Census Bureau ACS
        </div>
      </footer>
    </main>
  </div>
</template>

<style>
/* ===== DESIGN TOKENS ===== */
:root {
  --philly-blue:        #2176D2;
  --philly-blue-dark:   #0F4D90;
  --philly-blue-light:  #DAEDFE;
  --philly-yellow:      #F3A738;
  --philly-green:       #58A618;
  --philly-red:         #BF2600;
  --philly-dark:        #0F1A2E;
  --philly-mid:         #444B55;
  --philly-light:       #F0F7FF;
  --philly-white:       #FFFFFF;
  --philly-border:      #C3CFD9;

  --font-primary: 'Ben Franklin', 'Source Sans Pro', sans-serif;

  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 40px;
}

/* ===== GLOBAL RESET ===== */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-primary);
  background: #F8FAFC;
  color: var(--philly-dark);
  font-size: 14px;
  line-height: 1.5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

*:focus-visible {
  outline: 2px solid var(--philly-blue);
  outline-offset: 1px;
}

/* ===== HEADER ===== */
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
.wordmark { color: var(--philly-white); font-size: 16px; font-weight: 600; letter-spacing: 0.02em; }
.header-center .app-title { color: var(--philly-white); font-size: 14px; font-weight: 400; }
.header-right { color: var(--philly-white); font-size: 13px; }
#header-month-text { font-weight: 600; }

/* ===== LAYOUT ===== */
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

/* ===== SAFEGUARD ===== */
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
}

.safeguard-icon { font-size: 18px; line-height: 1.4; }
.safeguard-text { flex: 1; }

.safeguard-notice-top {
  background: #FEF5E4;
  border-left: 4px solid var(--philly-yellow);
  padding: 12px 16px;
  font-size: 13px;
  color: var(--philly-dark);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  margin: 12px 0 8px 0;
}

.safeguard-top-icon {
  font-size: 18px;
  line-height: 1;
}

/* ===== FOOTER ===== */
footer[role="contentinfo"] {
  background: var(--philly-blue-dark);
  color: var(--philly-white);
  padding: 12px 0 8px 0;
  margin-top: auto;
  width: 100%;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.footer-left { font-size: 13px; }

.footer-right {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--philly-white);
  color: var(--philly-white);
  padding: 6px 16px;
  font-size: 13px;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 400;
}

.btn-outline:hover { background: rgba(255,255,255,0.1); }
.btn-outline:disabled { opacity: 0.6; cursor: not-allowed; }

#campaign-status {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 4px;
  padding: 4px 24px;
}

#campaign-status.success { color: #A8E6CF; }
#campaign-status.error { color: #FF8A80; }

.footer-attribution {
  max-width: 1200px;
  margin: 6px auto 0;
  padding: 0 24px 8px;
  font-size: 11px;
  opacity: 0.7;
  text-align: left;
}

/* ===== BADGES ===== */
.badge {
  display: inline-block;
  padding: 0 8px;
  border-radius: 2px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  line-height: 20px;
}

.badge-red { background: #FDECEA; color: var(--philly-red); }
.badge-yellow { background: #FEF5E4; color: #7A4F00; }
.badge-blue { background: var(--philly-blue-light); color: var(--philly-blue-dark); }
.badge-gray { background: #F4F4F4; color: var(--philly-mid); }

.tax-yes { color: var(--philly-red); font-weight: 600; }
.tax-no { color: var(--philly-mid); }

.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
  .app-layout { flex-direction: column; }
  .main-panel { padding: 16px; }
  .footer-inner { flex-direction: column; align-items: flex-start; }
  .footer-right { width: 100%; justify-content: flex-start; }
}

@media (max-width: 768px) {
  .header-inner { flex-wrap: wrap; height: auto; padding: 8px 0; }
  header[role="banner"] { height: auto; min-height: 56px; padding: 4px 16px; }
  .header-center { order: 3; width: 100%; text-align: center; margin-top: 2px; }
  .header-right { font-size: 12px; }
  .footer-left { font-size: 12px; }
}
</style>
