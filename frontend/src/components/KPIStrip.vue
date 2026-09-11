<script setup lang="ts">
import { useForecastStore } from '@/stores/forecast'

const store = useForecastStore()
</script>

<template>
  <section id="kpi-strip" aria-label="Key performance indicators" v-if="store.kpi">
    <div class="kpi-card" data-kpi="critical">
      <div class="kpi-label">Critical-Risk Tracts</div>
      <div class="kpi-value" :class="{ 'kpi-critical-high': store.kpi.critical_tracts > 0 }">
        {{ store.kpi.critical_tracts }}
      </div>
      <div class="kpi-sub">(Predicted &gt; 12)</div>
    </div>
    <div class="kpi-card" data-kpi="filings">
      <div class="kpi-label">Predicted Filings (Top {{ store.kpi.top_n }})</div>
      <div class="kpi-value">{{ store.kpi.predicted_filings_top_n }}</div>
    </div>
    <div class="kpi-card" data-kpi="mae">
      <div class="kpi-label">Model MAE</div>
      <div class="kpi-value">{{ store.kpi.model_mae }}</div>
    </div>
    <div class="kpi-card" data-kpi="equity">
      <div class="kpi-label">Equity Check</div>
      <div class="kpi-value" :class="store.kpi.equity_passed ? 'kpi-equity-passed' : 'kpi-equity-failed'">
        {{ store.kpi.equity_label }}
      </div>
      <div class="kpi-sub" v-if="store.kpi.equity_passed">No systematic under‑prediction detected.</div>
    </div>
  </section>
</template>

<style scoped>
#kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi-card {
  background: var(--philly-white);
  border: 1px solid var(--philly-border);
  border-radius: 2px;
  padding: 12px 16px;
}

.kpi-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--philly-mid);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.kpi-value { font-size: 28px; font-weight: 700; color: var(--philly-dark); line-height: 1.2; }
.kpi-sub { font-size: 11px; color: var(--philly-mid); margin-top: 2px; }
.kpi-critical-high { color: var(--philly-red); }
.kpi-equity-passed { color: var(--philly-green); }
.kpi-equity-failed { color: var(--philly-red); }

@media (max-width: 1024px) {
  #kpi-strip { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  #kpi-strip { grid-template-columns: 1fr 1fr; gap: 10px; }
  .kpi-card { padding: 10px 12px; }
  .kpi-value { font-size: 22px; }
}
</style>
