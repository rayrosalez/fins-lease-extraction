#!/bin/bash
set -euo pipefail

# =============================================================================
# LeaseMiner Setup Script
# Provisions all Databricks resources and deploys the application.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.env"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }

# --- Load config ---
if [ ! -f "$CONFIG_FILE" ]; then
  err "config.env not found. Run: cp config.env.template config.env"
fi
source "$CONFIG_FILE"

# --- Validate required vars ---
for var in DATABRICKS_HOST DATABRICKS_CATALOG DATABRICKS_SCHEMA DATABRICKS_VOLUME DATABRICKS_WAREHOUSE_ID SERVING_ENDPOINT; do
  if [ -z "${!var:-}" ]; then
    err "$var is required in config.env"
  fi
done

APP_NAME="${APP_NAME:-lease-extraction}"
PROFILE_FLAG=""
if [ -n "${DATABRICKS_PROFILE:-}" ]; then
  PROFILE_FLAG="--profile=${DATABRICKS_PROFILE}"
fi

info "Deploying LeaseMiner to ${DATABRICKS_HOST}"
info "Catalog: ${DATABRICKS_CATALOG} | Schema: ${DATABRICKS_SCHEMA}"

# --- Check prerequisites ---
command -v databricks >/dev/null 2>&1 || err "Databricks CLI not found. Install: https://docs.databricks.com/dev-tools/cli/install.html"
command -v jq >/dev/null 2>&1 || err "jq not found. Install: brew install jq"

# --- Validate auth ---
info "Checking Databricks authentication..."
databricks auth env $PROFILE_FLAG >/dev/null 2>&1 || err "Not authenticated. Run: databricks auth login ${DATABRICKS_HOST} $PROFILE_FLAG"
log "Authenticated to ${DATABRICKS_HOST}"

# --- Get current user for notebook path ---
CURRENT_USER=$(databricks current-user me $PROFILE_FLAG -o json 2>/dev/null | jq -r '.userName // empty' || echo "")
if [ -z "$CURRENT_USER" ]; then
  err "Could not determine current user. Check your authentication."
fi
NOTEBOOK_PATH="/Workspace/Users/${CURRENT_USER}/lease-extraction-pipeline"
log "Notebook path: ${NOTEBOOK_PATH}"

# =============================================================================
# Step 1: Create Unity Catalog resources
# =============================================================================
info "Creating Unity Catalog resources..."

# Create catalog (ignore if exists)
databricks api post /api/2.1/unity-catalog/catalogs $PROFILE_FLAG \
  --json "{\"name\": \"${DATABRICKS_CATALOG}\"}" 2>/dev/null || true
log "Catalog: ${DATABRICKS_CATALOG}"

# Create schema
databricks api post /api/2.1/unity-catalog/schemas $PROFILE_FLAG \
  --json "{\"catalog_name\": \"${DATABRICKS_CATALOG}\", \"name\": \"${DATABRICKS_SCHEMA}\"}" 2>/dev/null || true
log "Schema: ${DATABRICKS_CATALOG}.${DATABRICKS_SCHEMA}"

# Create volume
databricks api post /api/2.1/unity-catalog/volumes $PROFILE_FLAG \
  --json "{\"catalog_name\": \"${DATABRICKS_CATALOG}\", \"schema_name\": \"${DATABRICKS_SCHEMA}\", \"name\": \"${DATABRICKS_VOLUME}\", \"volume_type\": \"MANAGED\"}" 2>/dev/null || true
log "Volume: ${DATABRICKS_CATALOG}.${DATABRICKS_SCHEMA}.${DATABRICKS_VOLUME}"

# Create uploads subfolder
databricks api put "/api/2.0/fs/directories/Volumes/${DATABRICKS_CATALOG}/${DATABRICKS_SCHEMA}/${DATABRICKS_VOLUME}/uploads" $PROFILE_FLAG 2>/dev/null || true

# =============================================================================
# Step 2: Create tables
# =============================================================================
info "Creating tables..."

for sql_file in "${SCRIPT_DIR}/DatabricksResources"/Create*.sql; do
  if [ -f "$sql_file" ]; then
    SQL=$(sed "s/\${CATALOG}/${DATABRICKS_CATALOG}/g; s/\${SCHEMA}/${DATABRICKS_SCHEMA}/g" "$sql_file")
    databricks api post /api/2.0/sql/statements $PROFILE_FLAG \
      --json "{\"warehouse_id\": \"${DATABRICKS_WAREHOUSE_ID}\", \"statement\": $(echo "$SQL" | jq -Rs .), \"wait_timeout\": \"50s\"}" >/dev/null 2>&1
    log "Table: $(basename "$sql_file" .sql)"
  fi
done

# =============================================================================
# Step 3: Upload pipeline notebooks
# =============================================================================
info "Uploading pipeline notebooks to ${NOTEBOOK_PATH}..."

for nb in "${SCRIPT_DIR}/DatabricksResources/pipeline"/*.py; do
  nb_name=$(basename "$nb" .py)
  databricks workspace import "${NOTEBOOK_PATH}/${nb_name}" \
    --file "$nb" --language PYTHON --format SOURCE --overwrite $PROFILE_FLAG 2>/dev/null
  log "Notebook: ${nb_name}"
done

# =============================================================================
# Step 4: Create pipeline jobs
# =============================================================================
info "Creating pipeline jobs..."

# Ingest job (steps 1-2)
INGEST_JOB_RESPONSE=$(databricks api post /api/2.1/jobs/create $PROFILE_FLAG --json "{
  \"name\": \"Lease Ingestion Pipeline (Steps 1-2)\",
  \"tasks\": [
    {
      \"task_key\": \"01_ingest_documents\",
      \"notebook_task\": {
        \"notebook_path\": \"${NOTEBOOK_PATH}/01_Ingestor\",
        \"base_parameters\": {\"catalog\": \"${DATABRICKS_CATALOG}\", \"schema\": \"${DATABRICKS_SCHEMA}\", \"volume\": \"${DATABRICKS_VOLUME}\"},
        \"source\": \"WORKSPACE\"
      },
      \"environment_key\": \"default\"
    },
    {
      \"task_key\": \"02_structure_extraction\",
      \"depends_on\": [{\"task_key\": \"01_ingest_documents\"}],
      \"notebook_task\": {
        \"notebook_path\": \"${NOTEBOOK_PATH}/02_Structurer\",
        \"base_parameters\": {\"catalog\": \"${DATABRICKS_CATALOG}\", \"schema\": \"${DATABRICKS_SCHEMA}\", \"serving_endpoint\": \"${SERVING_ENDPOINT}\"},
        \"source\": \"WORKSPACE\"
      },
      \"environment_key\": \"default\"
    }
  ],
  \"environments\": [{\"environment_key\": \"default\", \"spec\": {\"client\": \"1\"}}],
  \"tags\": {\"project\": \"lease-extraction\"},
  \"max_concurrent_runs\": 1,
  \"queue\": {\"enabled\": true}
}" 2>&1)

INGEST_JOB_ID=$(echo "$INGEST_JOB_RESPONSE" | jq -r '.job_id // empty')
if [ -z "$INGEST_JOB_ID" ]; then
  err "Failed to create ingest job: $INGEST_JOB_RESPONSE"
fi
log "Ingest job created: ${INGEST_JOB_ID}"

# Full pipeline job (steps 1-4)
PIPELINE_JOB_RESPONSE=$(databricks api post /api/2.1/jobs/create $PROFILE_FLAG --json "{
  \"name\": \"Lease Extraction Pipeline (Full)\",
  \"tasks\": [
    {
      \"task_key\": \"01_ingest_documents\",
      \"notebook_task\": {
        \"notebook_path\": \"${NOTEBOOK_PATH}/01_Ingestor\",
        \"base_parameters\": {\"catalog\": \"${DATABRICKS_CATALOG}\", \"schema\": \"${DATABRICKS_SCHEMA}\", \"volume\": \"${DATABRICKS_VOLUME}\"},
        \"source\": \"WORKSPACE\"
      },
      \"environment_key\": \"default\"
    },
    {
      \"task_key\": \"02_structure_extraction\",
      \"depends_on\": [{\"task_key\": \"01_ingest_documents\"}],
      \"notebook_task\": {
        \"notebook_path\": \"${NOTEBOOK_PATH}/02_Structurer\",
        \"base_parameters\": {\"catalog\": \"${DATABRICKS_CATALOG}\", \"schema\": \"${DATABRICKS_SCHEMA}\", \"serving_endpoint\": \"${SERVING_ENDPOINT}\"},
        \"source\": \"WORKSPACE\"
      },
      \"environment_key\": \"default\"
    },
    {
      \"task_key\": \"03_enrich_entities\",
      \"depends_on\": [{\"task_key\": \"02_structure_extraction\"}],
      \"notebook_task\": {
        \"notebook_path\": \"${NOTEBOOK_PATH}/03_Enricher\",
        \"base_parameters\": {\"catalog\": \"${DATABRICKS_CATALOG}\", \"schema\": \"${DATABRICKS_SCHEMA}\", \"serving_endpoint\": \"${SERVING_ENDPOINT}\"},
        \"source\": \"WORKSPACE\"
      },
      \"environment_key\": \"default\"
    },
    {
      \"task_key\": \"04_promote_to_silver\",
      \"depends_on\": [{\"task_key\": \"03_enrich_entities\"}],
      \"notebook_task\": {
        \"notebook_path\": \"${NOTEBOOK_PATH}/04_PromoteBronzeToSilver\",
        \"base_parameters\": {\"catalog\": \"${DATABRICKS_CATALOG}\", \"schema\": \"${DATABRICKS_SCHEMA}\"},
        \"source\": \"WORKSPACE\"
      },
      \"environment_key\": \"default\"
    }
  ],
  \"environments\": [{\"environment_key\": \"default\", \"spec\": {\"client\": \"1\"}}],
  \"tags\": {\"project\": \"lease-extraction\"},
  \"max_concurrent_runs\": 1,
  \"queue\": {\"enabled\": true}
}" 2>&1)

PIPELINE_JOB_ID=$(echo "$PIPELINE_JOB_RESPONSE" | jq -r '.job_id // empty')
if [ -z "$PIPELINE_JOB_ID" ]; then
  err "Failed to create pipeline job: $PIPELINE_JOB_RESPONSE"
fi
log "Pipeline job created: ${PIPELINE_JOB_ID}"

# =============================================================================
# Step 5: Build and deploy the app
# =============================================================================
info "Building React frontend..."
cd "${SCRIPT_DIR}/app"
npm install --silent 2>/dev/null
npm run build 2>/dev/null
cd "$SCRIPT_DIR"
log "React build complete"

info "Rendering app.yaml with workspace-specific values..."
sed \
  -e "s/__DATABRICKS_CATALOG__/${DATABRICKS_CATALOG}/g" \
  -e "s/__DATABRICKS_SCHEMA__/${DATABRICKS_SCHEMA}/g" \
  -e "s/__DATABRICKS_VOLUME__/${DATABRICKS_VOLUME}/g" \
  -e "s/__DATABRICKS_WAREHOUSE_ID__/${DATABRICKS_WAREHOUSE_ID}/g" \
  -e "s/__INGEST_JOB_ID__/${INGEST_JOB_ID}/g" \
  -e "s/__PIPELINE_JOB_ID__/${PIPELINE_JOB_ID}/g" \
  -e "s/__SERVING_ENDPOINT__/${SERVING_ENDPOINT}/g" \
  "${SCRIPT_DIR}/app/app.yaml" > "${SCRIPT_DIR}/app/app.yaml.rendered"
cp "${SCRIPT_DIR}/app/app.yaml.rendered" "${SCRIPT_DIR}/app/app.yaml.deploy"
log "app.yaml rendered"

# Upload app to workspace
APP_WS_PATH="/Workspace/Users/${CURRENT_USER}/${APP_NAME}"
info "Uploading app to ${APP_WS_PATH}..."

# Upload key directories (skip node_modules)
for dir in backend build data_generation public; do
  if [ -d "${SCRIPT_DIR}/app/${dir}" ]; then
    databricks workspace import-dir "${SCRIPT_DIR}/app/${dir}" "${APP_WS_PATH}/${dir}" --overwrite $PROFILE_FLAG 2>/dev/null || true
  fi
done
# Upload root files
for f in app.yaml.deploy requirements.txt package.json; do
  src="${SCRIPT_DIR}/app/${f}"
  [ "$f" = "app.yaml.deploy" ] && dest="${APP_WS_PATH}/app.yaml" || dest="${APP_WS_PATH}/${f}"
  if [ -f "$src" ]; then
    databricks workspace delete "$dest" $PROFILE_FLAG 2>/dev/null || true
    databricks workspace import "$dest" --file "$src" --format AUTO $PROFILE_FLAG 2>/dev/null || true
  fi
done
log "App uploaded to workspace"

# Create the app if it doesn't exist
info "Creating/deploying Databricks App: ${APP_NAME}..."
databricks apps create --name "${APP_NAME}" $PROFILE_FLAG 2>/dev/null || true

# Deploy
databricks apps deploy "${APP_NAME}" --source-code-path "${APP_WS_PATH}" $PROFILE_FLAG 2>/dev/null
log "App deployment started"

# Grant job permissions to app service principal
info "Granting job permissions to app service principal..."
SP_CLIENT_ID=$(databricks api get "/api/2.0/apps/${APP_NAME}" $PROFILE_FLAG 2>/dev/null | jq -r '.service_principal_client_id // empty')
if [ -n "$SP_CLIENT_ID" ]; then
  for job_id in "$INGEST_JOB_ID" "$PIPELINE_JOB_ID"; do
    databricks api patch "/api/2.0/permissions/jobs/${job_id}" $PROFILE_FLAG \
      --json "{\"access_control_list\": [{\"service_principal_name\": \"${SP_CLIENT_ID}\", \"permission_level\": \"CAN_MANAGE_RUN\"}]}" >/dev/null 2>&1
  done
  log "Job permissions granted to app service principal"
else
  warn "Could not find app service principal. Grant job permissions manually."
fi

# =============================================================================
# Step 6: Save dynamic values back to config.env
# =============================================================================
sed -i.bak \
  -e "s/^INGEST_JOB_ID=.*/INGEST_JOB_ID=${INGEST_JOB_ID}/" \
  -e "s/^PIPELINE_JOB_ID=.*/PIPELINE_JOB_ID=${PIPELINE_JOB_ID}/" \
  -e "s|^NOTEBOOK_PATH=.*|NOTEBOOK_PATH=${NOTEBOOK_PATH}|" \
  "$CONFIG_FILE"
rm -f "${CONFIG_FILE}.bak"
log "Updated config.env with job IDs"

# =============================================================================
# Done
# =============================================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  LeaseMiner deployed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  Catalog:      ${DATABRICKS_CATALOG}.${DATABRICKS_SCHEMA}"
echo "  Ingest Job:   ${INGEST_JOB_ID}"
echo "  Pipeline Job: ${PIPELINE_JOB_ID}"
echo "  Notebooks:    ${NOTEBOOK_PATH}"
echo "  App:          ${APP_NAME}"
echo ""
echo "  Open: ${DATABRICKS_HOST}/apps/${APP_NAME}"
echo ""
