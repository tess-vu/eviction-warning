<script setup lang="ts">
import { useForecastStore } from '@/stores/forecast'

const store = useForecastStore()

function badgeClass(tier: string) {
  if (tier === 'Deploy Canvassers') return 'badge-red'
  if (tier === 'Direct Mail') return 'badge-yellow'
  if (tier === 'Legal Aid Pop-Up') return 'badge-blue'
  return 'badge-gray'
}
</script>

<template>
  <section id="tract-table-section" aria-labelledby="tract-table-heading" v-if="store.tracts.length">
    <h2 id="tract-table-heading">Top Tracts by Predicted Filings</h2>
    <div id="tract-table-wrapper">
      <table id="tract-table">
        <caption>Top Tracts Sorted by Predicted Eviction Filings</caption>
        <thead>
          <tr>
            <th scope="col">Rank</th>
            <th scope="col">GEOID</th>
            <th scope="col">Neighborhood</th>
            <th scope="col">Predicted</th>
            <th scope="col">Action Tier</th>
            <th scope="col">Race Majority</th>
            <th scope="col">Tax Stress</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in store.tracts" :key="t.geoid">
            <td>{{ t.rank }}</td>
            <td>{{ t.geoid }}</td>
            <td>{{ t.neighborhood }}</td>
            <td>{{ t.predicted }}</td>
            <td><span class="badge" :class="badgeClass(t.action_tier)">{{ t.action_tier }}</span></td>
            <td>{{ t.racial_majority }}</td>
            <td :class="t.tax_stress === 'Yes' ? 'tax-yes' : 'tax-no'">{{ t.tax_stress }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
#tract-table-section h2 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--philly-dark);
}

#tract-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

#tract-table caption {
  caption-side: top;
  text-align: left;
  font-size: 12px;
  font-weight: 400;
  color: var(--philly-mid);
  padding-bottom: 4px;
}

#tract-table thead th {
  background: var(--philly-blue-dark);
  color: var(--philly-white);
  font-weight: 600;
  text-align: left;
  padding: 8px 12px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

#tract-table tbody td {
  padding: 7px 12px;
  border-bottom: 1px solid var(--philly-border);
}

#tract-table tbody tr:nth-child(even) { background: var(--philly-light); }
#tract-table tbody tr:nth-child(odd) { background: var(--philly-white); }

@media (max-width: 768px) {
  #tract-table { font-size: 12px; }
  #tract-table thead th, #tract-table tbody td { padding: 5px 6px; }
}
</style>
