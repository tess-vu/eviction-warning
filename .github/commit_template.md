<TYPE>(<scope>): <short summary>

<Explain WHAT change accomplishes and WHY it was made. Wrap text at 72 characters. Focus on architectural, spatial, or business logic reasons. Do not include raw implementation code here.>

<Ticket references or breaking change notes, e.g. "Closes #123">

# Commit Message Guidelines
#
# Commit Structure:
# Prefix summary line with uppercase TYPE and lowercase relevant scope.
#
# Valid Types: FEAT, FIX, REFACTOR, PERF, STYLE, TEST, DOCS, CHORE
#
# Valid Scopes:
# - Data Pipelines & Language Contexts: python, r, sql (captures standard non-spatial scripting updates).
# - Database Layers: db, postgis (isolates database architecture, database indexing, and heavy SQL migrations).
# - Data Specifics: raster, vector, data (great for tracking changes to GeoTIFF handlers, Shapefile/GeoJSON utilities, or download workflows)
# - Visualizations & Dashboards: viz, leaflet, mapbox, streamlit (instantly informs code reviewers that front-end interface changes are present)
# - Infrastructure / Core Project Setup: repo, deps, ci (for managing your repository structure, package tracking, and .gitignore shifts).
#
# Format Rules:
# - Summary Line: Max 50 characters. No trailing period.
# - Blank Line: Required before and after the body.
# - Body Text: Wrap at 72 characters.
#
# Example Commit Message:
# PERF(postgis): add spatial indexing to parcel table
#
# Created spatial index on geometry column for parcel dataset.
# Index required to drastically reduce query times for
# bounding box intersections used by frontend.
#
# Resolves #404
