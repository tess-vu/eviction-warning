<script setup lang="ts">
import { ref } from 'vue'
import { useForecastStore } from '@/stores/forecast'
import { useApi, STATIC_MODE } from '@/composables/useApi'

const store = useForecastStore()
const api = useApi()

const campaignSending = ref(false)
const campaignStatus = ref('')
const campaignError = ref(false)

function downloadPdf() {
  api.downloadBrief(store.selectedMonth, store.topN)
}

async function sendCampaign() {
  campaignSending.value = true
  campaignStatus.value = 'Starting mock campaign …'
  campaignError.value = false
  try {
    await api.sendCampaign(store.selectedMonth, store.topN)
    campaignStatus.value =
      `✅ Campaign Started: Check outputs/campaign_report_${store.selectedMonth.replace('-', '_')}.json`
  } catch (e: unknown) {
    campaignStatus.value = e instanceof Error ? e.message : 'Campaign Request Failed'
    campaignError.value = true
  } finally {
    campaignSending.value = false
  }
}
</script>

<template>
  <footer role="contentinfo">
    <div class="footer-inner">
      <div class="footer-left">
        Office of Homeless Services · Fair Housing Commission
      </div>
      <div v-if="!STATIC_MODE" class="footer-right">
        <button id="generate-pdf-btn" class="btn-outline" @click="downloadPdf">
          Generate PDF Brief
        </button>
        <button
          id="send-campaign-btn"
          class="btn-outline"
          :disabled="campaignSending"
          @click="sendCampaign"
        >
          {{ campaignSending ? 'Sending …' : 'Send Monthly Campaign (Mock)' }}
        </button>
      </div>
      <div v-else class="footer-right footer-note">
        Static Demo. PDF briefs and mail campaigns require the FastAPI backend.
      </div>
    </div>
    <div
      id="campaign-status"
      aria-live="polite"
      :class="{ success: campaignStatus && !campaignError, error: campaignError }"
    >
      {{ campaignStatus }}
    </div>
    <div class="footer-attribution">
      Data Sources: Eviction Lab, OpenDataPhilly, U.S. Census Bureau ACS
    </div>
  </footer>
</template>

<style scoped>
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
  font-family: inherit;
}

.btn-outline:hover { background: rgba(255, 255, 255, 0.1); }
.btn-outline:disabled { opacity: 0.6; cursor: not-allowed; }

.footer-note { font-size: 12px; opacity: 0.75; }

#campaign-status {
  max-width: 1200px;
  margin: 4px auto 0;
  padding: 0 24px;
  font-size: 12px;
  opacity: 0.9;
  min-height: 18px;
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

@media (max-width: 1024px) {
  .footer-inner { flex-direction: column; align-items: flex-start; }
  .footer-right { width: 100%; justify-content: flex-start; }
}

@media (max-width: 768px) {
  .footer-left { font-size: 12px; }
}
</style>
