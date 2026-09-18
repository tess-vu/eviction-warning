<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import maplibregl from 'maplibre-gl'
import { useForecastStore } from '@/stores/forecast'

const store = useForecastStore()
const mapContainer = ref<HTMLElement | null>(null)
let map: maplibregl.Map | null = null

const QUINTILE_COLORS: Record<number, string> = {
  1: '#DAEDFE',
  2: '#7AB8F5',
  3: '#2176D2',
  4: '#F3A738',
  5: '#BF2600',
}

onMounted(() => {
  if (!mapContainer.value) return
  map = new maplibregl.Map({
    container: mapContainer.value,
    style: {
      version: 8,
      sources: {
        carto: {
          type: 'raster',
          tiles: ['https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png'],
          tileSize: 256,
          attribution: '&copy; OpenStreetMap, &copy; CartoDB',
        },
      },
      layers: [{ id: 'carto', type: 'raster', source: 'carto' }],
    },
    center: [-75.16361204959983, 39.952405197097015],
    zoom: 11,
  })
  map.addControl(new maplibregl.NavigationControl(), 'top-right')
})

// Placeholder: WIP. Watch store.tracts and load GeoJSON features
// with fill colors keyed to risk_quintile. Skipped bc GeoJSON
// source (ArcGIS) requires tract geometry that isn't in model_predictions.csv.
</script>

<template>
  <section id="map-panel" aria-label="Eviction Risk map of Philadelphia Census Tracts">
    <div id="map" ref="mapContainer" role="img" aria-label="Eviction Risk Map of Philadelphia Census Tracts"></div>
    <div class="map-legend">
      <div class="legend-title">Risk Quintile</div>
      <div class="legend-gradient">
        <div class="gradient-step" style="background:#DAEDFE;"></div>
        <div class="gradient-step" style="background:#7AB8F5;"></div>
        <div class="gradient-step" style="background:#2176D2;"></div>
        <div class="gradient-step" style="background:#F3A738;"></div>
        <div class="gradient-step" style="background:#BF2600;"></div>
      </div>
      <div class="legend-labels">
        <span>Lowest Risk</span>
        <span>Highest Risk</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
#map-panel {
  border: 1px solid var(--philly-border);
  border-radius: 2px;
  overflow: hidden;
  position: relative;
}

#map { height: 440px; width: 100%; background: #E5E9F0; }

.map-legend {
  background: var(--philly-white);
  border: 1px solid var(--philly-border);
  border-radius: 2px;
  padding: 8px 10px;
  font-size: 12px;
  line-height: 1.4;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  position: absolute;
  bottom: 20px;
  right: 10px;
  z-index: 3;
  pointer-events: none;
}

.legend-title { font-weight: 600; margin-bottom: 4px; font-size: 11px; }

.legend-gradient { display: flex; height: 12px; width: 140px; margin: 4px 0; }
.legend-gradient .gradient-step { flex: 1; }

.legend-labels { display: flex; justify-content: space-between; font-size: 10px; color: var(--philly-mid); }

@media (max-width: 768px) {
  #map { height: 320px; }
  .map-legend { bottom: 10px; right: 6px; }
  .map-legend .legend-gradient { width: 100px; }
}
</style>
