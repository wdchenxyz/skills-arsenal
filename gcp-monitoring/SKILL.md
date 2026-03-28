---
name: gcp-monitoring
description: >
  GCP monitoring and troubleshooting for Cloud Run services, Bigtable, Dataflow, and alert policies.
  Use when asked to: check Cloud Run logs, query 5xx errors, inspect monitoring dashboards,
  check metrics/time-series data, review alert policies, check Bigtable table status,
  list dataflow jobs, or investigate production issues on GCP.
  Triggers on: "check logs", "5xx errors", "cloud run", "monitoring dashboard", "alert policy",
  "bigtable", "dataflow", "check metrics", "is the service healthy", "check incidents".
---

# GCP Monitoring

## Cloud Run Services

```bash
# List services across all regions
gcloud run services list --project=PROJECT_ID --filter="service:SERVICE_NAME"

# Describe a specific service (scaling, resources, status)
gcloud run services describe SERVICE_NAME --region=REGION --project=PROJECT_ID \
  --format="yaml(status.conditions,spec.template.spec.containers[0].resources,spec.template.metadata.annotations)"
```

## Querying Logs

Use `gcloud logging read` with filters. Always specify `--freshness` to limit time range.

```bash
# 5xx HTTP errors
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name=~"SERVICE_PATTERN" AND httpRequest.status>=500' \
  --project=PROJECT_ID --limit=50 --freshness=1h \
  --format="table(timestamp,resource.labels.location,httpRequest.status,httpRequest.requestUrl)"

# Application error logs
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name=~"SERVICE_PATTERN" AND textPayload=~"Error"' \
  --project=PROJECT_ID --limit=50 --freshness=1h \
  --format="value(timestamp,textPayload)"

# Filter by specific text pattern
gcloud logging read \
  'resource.type="cloud_run_revision" AND textPayload=~"PATTERN"' \
  --project=PROJECT_ID --limit=20 --freshness=30m
```

## Querying Dashboard Metrics

The `gcloud` CLI cannot query time-series data. Use the Monitoring REST API via curl instead.
See [references/api_reference.md](references/api_reference.md) for full API details, common metric types, and examples.

### Workflow

1. **List dashboards** to find the relevant one:
   ```bash
   gcloud monitoring dashboards list --project=PROJECT_ID --format="table(name,displayName)"
   ```

2. **Describe dashboard** to see widget metrics:
   ```bash
   gcloud monitoring dashboards describe DASHBOARD_NAME --project=PROJECT_ID --format=json
   ```
   Parse with python3 to extract widget titles and metric filters.

3. **Query metrics** using curl to the Monitoring API with the metric filter from the dashboard widget.

## Alert Policies

```bash
# List policies (filter with grep)
gcloud alpha monitoring policies list --project=PROJECT_ID \
  --format="table(name.basename(),displayName,enabled)" | grep -i "PATTERN"

# Describe a policy (conditions, thresholds, notification channels)
gcloud alpha monitoring policies describe projects/PROJECT_ID/alertPolicies/POLICY_ID \
  --project=PROJECT_ID --format=yaml

# Check open incidents
# Use curl — see references/api_reference.md
```

Key fields to check in alert policies:
- `filter` — what resources are monitored
- `groupByFields` — whether each resource is evaluated independently
- `duration` — how long condition must be violated before firing
- `evaluationMissingData` — behavior when metric disappears (critical for stopped services)
- `trigger.percent` — percentage of series that must violate

### GCP Console URL for a policy
```
https://console.cloud.google.com/monitoring/alerting/policies/POLICY_ID?project=PROJECT_ID
```

## Bigtable

```bash
# Describe table (shows column families and GC rules)
gcloud bigtable tables describe TABLE_ID --instance=INSTANCE_ID --project=PROJECT_ID

# Query read/write metrics — use curl API (see references/api_reference.md)
```

## Dataflow Jobs

```bash
# List active jobs (all regions)
gcloud dataflow jobs list --project=PROJECT_ID --status=active \
  --filter="name~PATTERN" --format="table(id,name,state,currentStateTime)"
```

## Troubleshooting Checklist

1. **Check service health**: `gcloud run services describe` — look for `Ready: True`
2. **Check recent errors**: `gcloud logging read` with `httpRequest.status>=500`
3. **Check error details**: `gcloud logging read` with `textPayload=~"Error"` for stack traces
4. **Check metrics**: curl Monitoring API for request counts, error rates, latencies
5. **Check alerts**: `gcloud alpha monitoring policies list/describe` for configured thresholds
6. **Check incidents**: curl incidents API for currently firing alerts
7. **Check upstream**: Bigtable table schema, dataflow job status
