<!--
  PULL REQUEST TEMPLATE
  Make sure PR title matches conventional commits pattern.
  Example: "FEAT(db): add spatial indexing to postgis table"
           "FEAT(postgis): add spatial indexing to postgis table"
-->

## EXECUTIVE SUMMARY
<!-- State what and why of changes at high level. -->
* **What:**
* **Why:**

## TYPE OF CHANGE
<!-- Check relevant boxes. -->
- [ ] **FEAT:** New feature (e.g. new processing script, dashboard addition)
- [ ] **FIX:** Bug fix (e.g. corrected CRS transformation, fixed topology error)
- [ ] **REFACTOR:** Structural code updates that change logic architecture without changing external behavior
- [ ] **PERF:** Increase processing speeds, query optimization, or reducing memory footprints (e.g. SQL query indexing, rendering speedup, crucial for big spatial vector/raster data)
- [ ] **STYLE:** Linting, fixing trailing spaces, or syntax fixes that don't alter logic execution
- [ ] **TEST:** Adding or correcting RSpec, PyTest, or spatial unit tests
- [ ] **DOCS:** Documentation updates
- [ ] **CHORE:** Maintenance, `.gitignore` adjustments for heavy spatial files

## SPATIAL AND DATA VERIFICATION
<!-- Verify spatial assets and logic. Check all that apply. -->
- [ ] **CRS AND PROJECTIONS:** Geometries are in correct coordinate reference system.
- [ ] **ASSET TRACKING:** Heavy assets (GeoJSON, Shapefiles, Cloud-Optimized GeoTIFFs, etc.) ignored or stored via LFS/endpoints.
- [ ] **EXECUTION:** Python/R/SQL spatial processing executes without topology or geometry errors.
- [ ] **VISUALIZATION:** Map components (Leaflet, Mapbox, Streamlit, etc.) render spatial vectors or rasters accurately.

## FOOTERS AND TICKET LINKS
<!-- Reference any related tickets or issues here. -->
* **Tickets:**
