<script setup lang="ts">
import { useForecastStore } from '@/stores/forecast'

const store = useForecastStore()
</script>

<template>
  <section id="equity-panel" aria-labelledby="equity-heading" v-if="store.equity">
    <div class="equity-header">
      <h2 id="equity-heading">Equity Monitoring</h2>
    </div>
    <div
      id="equity-status-banner"
      :class="store.equity.passed ? 'passed' : 'failed'"
      role="status"
      aria-live="polite"
    >
      <template v-if="store.equity.passed">
        ✅ EQUITY CHECK PASSED: No systematic under‑prediction detected.
      </template>
      <template v-else>
        ⚠️ EQUITY REVIEW REQUIRED: See flagged groups below.
      </template>
    </div>
    <div id="equity-table-wrapper">
      <table id="equity-table">
        <caption>Equity metrics by racial majority group.</caption>
        <thead>
          <tr>
            <th scope="col">Group</th>
            <th scope="col">MAE</th>
            <th scope="col">Bias</th>
            <th scope="col">Mean Observed</th>
            <th scope="col">Mean Predicted</th>
            <th scope="col">Equity Flag</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in store.equity.groups" :key="g.group">
            <td>{{ g.group }}</td>
            <td>{{ g.mae }}</td>
            <td>{{ g.bias }}</td>
            <td>{{ g.mean_observed }}</td>
            <td>{{ g.mean_predicted }}</td>
            <td>
              <span class="equity-flag-icon" :class="{ pass: g.equity_flag === '✓' }">
                {{ g.equity_flag }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="equity-narrative">{{ store.equity.narrative }}</div>
  </section>
</template>

<style scoped>
#equity-panel {
  border: 1px solid var(--philly-border);
  border-radius: 2px;
  background: var(--philly-white);
  margin-top: 8px;
}

.equity-header { padding: 10px 16px; border-bottom: 1px solid var(--philly-border); }
.equity-header h2 { font-size: 14px; font-weight: 700; color: var(--philly-dark); margin: 0; }

#equity-status-banner {
  padding: 10px 16px;
  margin: 0;
  font-size: 13px;
  border-bottom: 1px solid var(--philly-border);
}

#equity-status-banner.passed {
  background: #EEF6E8;
  border-left: 4px solid var(--philly-green);
}

#equity-status-banner.failed {
  background: #FEF5E4;
  border-left: 4px solid var(--philly-red);
}

#equity-table-wrapper { padding: 10px 16px 6px 16px; overflow-x: auto; }

#equity-table { width: 100%; border-collapse: collapse; font-size: 13px; }

#equity-table caption {
  caption-side: top;
  text-align: left;
  font-size: 12px;
  color: var(--philly-mid);
  padding-bottom: 4px;
}

#equity-table thead th {
  background: var(--philly-blue-dark);
  color: var(--philly-white);
  font-weight: 600;
  text-align: left;
  padding: 6px 10px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

#equity-table tbody td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--philly-border);
}

.equity-flag-icon {
  display: inline-block;
  padding: 0 6px;
  border-radius: 2px;
  font-size: 12px;
  font-weight: 600;
  background: #FEF5E4;
  color: var(--philly-dark);
}

.equity-flag-icon.pass { background: #EEF6E8; color: var(--philly-green); }

.equity-narrative {
  padding: 6px 16px 16px 16px;
  font-size: 13px;
  color: var(--philly-dark);
  border-top: 1px solid var(--philly-border);
  margin-top: 4px;
}
</style>
