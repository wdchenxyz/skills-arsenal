# GCP Monitoring API Reference

## Cloud Monitoring Time-Series API

The `gcloud` CLI does NOT support querying time-series metrics directly. Use the REST API via curl.

### Authentication & Base URL

```bash
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://monitoring.googleapis.com/v3/projects/{PROJECT_ID}/timeSeries?..."
```

### Query Parameters

| Parameter | Description |
|---|---|
| `filter` | Metric filter (URL-encoded) |
| `interval.startTime` / `interval.endTime` | ISO 8601 timestamps |
| `aggregation.alignmentPeriod` | Bucket size (`60s`, `300s`, `1800s`) |
| `aggregation.perSeriesAligner` | `ALIGN_SUM`, `ALIGN_RATE`, `ALIGN_MEAN` |
| `aggregation.crossSeriesReducer` | `REDUCE_SUM`, `REDUCE_MEAN`, `REDUCE_NONE` |
| `aggregation.groupByFields` | Group by fields (e.g., `metric.labels.method`) |

### Common Metric Types

**Cloud Run:**
- `run.googleapis.com/request_count` — by `response_code_class` (2xx/4xx/5xx)
- `run.googleapis.com/request_latencies` — latency distribution
- `run.googleapis.com/container/instance_count` — running instances

**Bigtable:**
- `bigtable.googleapis.com/server/request_count` — by `method` (ReadRows, MutateRow, MutateRows)
- `bigtable.googleapis.com/client/server_latencies` — server-side latency

**Dataflow:**
- `dataflow.googleapis.com/job/elements_produced_count` — elements per pcollection
- `dataflow.googleapis.com/job/data_watermark_age` — watermark lag

**Custom / Log-based:**
- `logging.googleapis.com/user/{metric_name}` — custom log-based metrics

### Example: Query 5xx Errors

```bash
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://monitoring.googleapis.com/v3/projects/PROJECT_ID/timeSeries?\
filter=metric.type%3D%22run.googleapis.com%2Frequest_count%22\
%20AND%20resource.labels.service_name%3Dmonitoring.regex.full_match(%22SERVICE_PATTERN%22)\
%20AND%20metric.labels.response_code_class%3D%225xx%22\
&interval.startTime=$(date -u -v-1H '+%Y-%m-%dT%H:%M:%SZ')\
&interval.endTime=$(date -u '+%Y-%m-%dT%H:%M:%SZ')\
&aggregation.alignmentPeriod=300s\
&aggregation.perSeriesAligner=ALIGN_SUM"
```

### Example: Bigtable Request Count by Method

```bash
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://monitoring.googleapis.com/v3/projects/PROJECT_ID/timeSeries?\
filter=metric.type%3D%22bigtable.googleapis.com%2Fserver%2Frequest_count%22\
%20AND%20resource.labels.instance%3D%22INSTANCE_ID%22\
%20AND%20resource.labels.table%3D%22TABLE_ID%22\
&interval.startTime=$(date -u -v-1H '+%Y-%m-%dT%H:%M:%SZ')\
&interval.endTime=$(date -u '+%Y-%m-%dT%H:%M:%SZ')\
&aggregation.alignmentPeriod=300s\
&aggregation.perSeriesAligner=ALIGN_SUM\
&aggregation.crossSeriesReducer=REDUCE_SUM\
&aggregation.groupByFields=metric.labels.method"
```

### Example: Single Summed Value

Use large `alignmentPeriod` with `REDUCE_SUM`:

```bash
&aggregation.alignmentPeriod=1800s\
&aggregation.perSeriesAligner=ALIGN_SUM\
&aggregation.crossSeriesReducer=REDUCE_SUM
```

### Parsing Responses

```bash
curl -s ... | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'timeSeries' not in data:
    print('No data:', json.dumps(data, indent=2)[:500])
else:
    for ts in data['timeSeries']:
        labels = ts['metric']['labels']
        rlabels = ts['resource']['labels']
        print(f'labels={labels}')
        for p in ts.get('points', []):
            val = p['value'].get('int64Value', p['value'].get('doubleValue', 0))
            t = p['interval']['startTime']
            print(f'  {t}: {val}')
"
```

## Alert Policy: Check Open Incidents

```bash
curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://monitoring.googleapis.com/v3/projects/PROJECT_ID/incidents?filter=state%3D%22open%22"
```

## evaluationMissingData Behavior

| Value | When Data Missing |
|---|---|
| default / `NO_OP` | No alert — series ignored |
| `ACTIVE` | Treated as violation — alert fires |
| `INACTIVE` | Treated as not violating |

Critical when a service/job is intentionally stopped: default means alerts won't fire for disappeared metrics.

## Date Helpers (macOS)

```bash
date -u -v-1H '+%Y-%m-%dT%H:%M:%SZ'   # 1 hour ago
date -u -v-30M '+%Y-%m-%dT%H:%M:%SZ'   # 30 min ago
date -u -v-3H '+%Y-%m-%dT%H:%M:%SZ'    # 3 hours ago
date -u '+%Y-%m-%dT%H:%M:%SZ'           # now
```
