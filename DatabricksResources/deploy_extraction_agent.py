# Databricks notebook source
# MAGIC %md
# MAGIC # Deploy Lease Extraction Agent
# MAGIC Registers a Mosaic AI Agent for structured lease extraction and deploys it via the Agent Framework.

# COMMAND ----------

# MAGIC %pip install -q databricks-agents databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import mlflow
print(f"MLflow version: {mlflow.__version__}")

dbutils.widgets.text("catalog", "REPLACE_WITH_YOUR_CATALOG", "UC Catalog")
dbutils.widgets.text("schema", "lease_management", "UC Schema")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
MODEL_NAME = f"{CATALOG}.{SCHEMA}.lease_extraction_agent"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define the Agent

# COMMAND ----------

import mlflow.pyfunc
from databricks.sdk import WorkspaceClient

SYSTEM_PROMPT = """You are a lease extraction AI specializing in commercial real estate documents.
Given a parsed lease document, extract all key fields into a structured JSON object.
Return ONLY valid JSON matching the required schema. Do not include any explanation or markdown formatting.
Extract values exactly as they appear in the document. Use null for fields that cannot be determined.
Dates must be in YYYY-MM-DD format. Monetary values should be numeric without currency symbols.

Required JSON schema:
{
  "landlord": {"name": "string|null", "address": "string|null"},
  "tenant": {"name": "string|null", "address": "string|null", "industry_sector": "string|null"},
  "property_location": {"full_address": "string|null", "street_address": "string|null", "city": "string|null", "state": "string|null", "zip_code": "string|null", "country": "string|null"},
  "lease_details": {"suite_number": "string|null", "lease_type": "string|null", "commencement_date": "YYYY-MM-DD|null", "expiration_date": "YYYY-MM-DD|null", "term_months": "int|null", "rentable_square_feet": "int|null"},
  "financial_terms": {"annual_base_rent": "int|null", "monthly_base_rent": "number|null", "base_rent_psf": "number|null", "annual_escalation_pct": "int|null", "additional_rent_estimate": "number|null", "pro_rata_share": "number|null", "security_deposit": "int|null"},
  "risk_and_options": {"renewal_options": "string|null", "renewal_notice_days": "int|null", "termination_rights": "string|null", "guarantor": "string|null"}
}"""

SERVING_ENDPOINT = "databricks-claude-sonnet-4-5"


class LeaseExtractionAgent(mlflow.pyfunc.PythonModel):

    def predict(self, context, model_input, params=None):
        # model_input is a dict with "messages" key when called via chat endpoint
        if isinstance(model_input, dict):
            input_messages = model_input.get("messages", [])
        else:
            # DataFrame input — extract messages from first row
            input_messages = model_input.to_dict(orient="records")[0].get("messages", [])

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in input_messages:
            if isinstance(msg, dict):
                messages.append({"role": msg["role"], "content": msg["content"]})
            else:
                messages.append({"role": msg.role, "content": msg.content})

        w = WorkspaceClient()
        response = w.serving_endpoints.query(
            name=SERVING_ENDPOINT,
            messages=messages,
            temperature=0.0,
            max_tokens=4096,
        )

        return response.choices[0].message.content

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log and Register the Agent

# COMMAND ----------

from mlflow.models import infer_signature
from mlflow.models.resources import DatabricksServingEndpoint

mlflow.set_registry_uri("databricks-uc")

# Define chat-compatible input/output signature
input_example = {
    "messages": [
        {"role": "user", "content": "Extract lease details from this document..."}
    ]
}

output_example = '{"landlord": {"name": "Example Corp", "address": "123 Main St"}}'

signature = infer_signature(input_example, output_example)

agent = LeaseExtractionAgent()

with mlflow.start_run(run_name="lease_extraction_agent_v5"):
    logged = mlflow.pyfunc.log_model(
        artifact_path="lease_extraction_agent",
        python_model=agent,
        signature=signature,
        input_example=input_example,
        pip_requirements=[
            "mlflow",
            "databricks-sdk",
        ],
        resources=[
            DatabricksServingEndpoint(endpoint_name="databricks-claude-sonnet-4-5"),
        ],
        registered_model_name=MODEL_NAME,
    )

print(f"Model registered: {MODEL_NAME}")
print(f"Run ID: {logged.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Deploy with Agent Framework

# COMMAND ----------

from databricks import agents
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
latest_versions = list(w.model_versions.list(full_name=MODEL_NAME))
model_version = max([v.version for v in latest_versions])
print(f"Deploying model version: {model_version}")

deployment = agents.deploy(
    model_name=MODEL_NAME,
    model_version=model_version,
    scale_to_zero=True,
)

print(f"Agent deployed!")
print(f"Endpoint name: {deployment.endpoint_name}")
print(f"Query endpoint: {deployment.query_endpoint}")
