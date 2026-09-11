<script setup lang="ts">
import { useForecastStore } from '@/stores/forecast'

const store = useForecastStore()
</script>

<template>
  <aside class="sidebar" role="complementary" aria-label="Controls and filters">
    <div class="sidebar-section">
      <label for="month-select" class="sidebar-label">Forecast month</label>
      <select id="month-select" v-model="store.selectedMonth" aria-describedby="month-help">
        <option v-for="m in store.months" :key="m" :value="m">{{ m }}</option>
      </select>
      <span id="month-help" class="help-text">Select a Month to Load Data</span>
    </div>

    <div class="sidebar-section">
      <label for="top-n-select" class="sidebar-label">Top N Tracts</label>
      <select id="top-n-select" v-model.number="store.topN">
        <option :value="10">10</option>
        <option :value="25">25</option>
        <option :value="50">50</option>
        <option :value="100">100</option>
      </select>
    </div>

    <button class="btn-primary" :disabled="store.loading" @click="store.loadForecast()">
      {{ store.loading ? 'Loading…' : 'Run Forecast' }}
    </button>

    <div class="sidebar-divider"></div>

    <div class="sidebar-section">
      <div class="sidebar-label">Data Status</div>
      <div id="data-status" class="status-text">
        {{ store.kpi ? '✅ Loaded' : '—' }}
      </div>

      <div class="safeguard-notice-top" role="note" aria-label="Ethical safeguard">
        <span class="safeguard-top-icon">⚠️</span>
        <span class="safeguard-text">
          This tool is FOR PROACTIVE RESOURCE ALLOCATION ONLY. It MUST NOT BE USED FOR ENFORCEMENT,
          PUNITIVE ACTION, OR AUTOMATED DECISION-MAKING OF ANY KIND. Any use outside resource
          allocation requires prior review by the Fair Housing Commission.
        </span>
      </div>

    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--philly-white);
  border-right: 1px solid var(--philly-border);
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 600px;
}

.sidebar-section { display: flex; flex-direction: column; gap: 4px; }

.sidebar-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--philly-mid);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.sidebar select {
  border: 1px solid var(--philly-border);
  border-radius: 2px;
  height: 36px;
  padding: 0 8px;
  font-size: 14px;
  color: var(--philly-dark);
  background: var(--philly-white);
  width: 100%;
}

.sidebar select:focus { outline: 2px solid var(--philly-blue); outline-offset: 0; }
.help-text { font-size: 11px; color: var(--philly-mid); margin-top: 2px; }

.btn-primary {
  background: var(--philly-blue);
  color: var(--philly-white);
  border: none;
  border-radius: 2px;
  height: 40px;
  font-size: 14px;
  font-weight: 600;
  width: 100%;
  cursor: pointer;
  margin-top: 4px;
}

.btn-primary:hover { background: var(--philly-blue-dark); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.sidebar-divider { border-top: 1px solid var(--philly-border); margin: 4px 0; }
.status-text { font-size: 13px; color: var(--philly-mid); }

@media (max-width: 1024px) {
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--philly-border);
    flex-direction: row;
    flex-wrap: wrap;
    padding: 12px 16px;
    min-height: auto;
    gap: 12px;
  }
  .sidebar-section { flex: 1 1 120px; min-width: 100px; }
  .btn-primary { width: auto; padding: 0 20px; flex: 0 0 auto; }
  .sidebar-divider { display: none; }
}

@media (max-width: 768px) {
  .sidebar { flex-direction: column; }
  .sidebar-section { flex: 1 1 auto; }
  .btn-primary { width: 100%; }
}
</style>
