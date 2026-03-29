# Instagram Reels Scraper – Deployment vs Local Comparison Report

## 1. Overview

This report compares the performance, reliability, and scalability of the Instagram Reels Scraper in two environments:

---

## 2. Single Profile Test Comparison

| Metric | Local | Deployment (Render Free Tier) |
|------|------|------------------------------|
| Username Tested | aliaabhatt | aliaabhatt |
| Reels Scraped | 13 | 3 |
| Duration | 104.18 sec | 70.77 sec |
| Status | ✅ Success | ✅ Success |

### Key Insights

- Local environment scraped **4x more reels**.
- Deployment finished faster but with **significantly reduced data extraction**.
- Indicates **partial scraping or early termination** in deployment.

---

## 3. Concurrency Performance Comparison

### 3.1 Summary Table

| Workers | Env | Total Requests | Success | Failures | Avg Latency (s) | Total Time (s) |
|--------|-----|---------------|---------|----------|----------------|---------------|
| 1 | Local | 10 | 10 | 0 | 41.82 | 418.24 |
| 3 | Local | 30 | 30 | 0 | 40.90 | 415.02 |
| 5 | Local | 50 | 20 | 30 | 23.65 | 323.57 |
| 1 | Deploy | 10 | 0 | 10 | 0.99 | 9.92 |

---

## 4. Reliability Analysis

### Local Environment

- ✅ **100% success rate** for 1 and 3 workers
- ⚠️ At 5 workers:
  - Success dropped to **40%**
  - Failures due to: `"Response ended prematurely"`
- System still functional under moderate concurrency

### Deployment (Render Free Tier)

- ❌ **0% success rate even at 1 worker**
- All requests failed with:
  - `HTTP 502 (Bad Gateway)`
- Failure latency extremely low (~1 sec), indicating:
  - Requests are **failing instantly at infrastructure level**

---

## 5. Error Analysis

| Environment | Error Type | Cause |
|------------|-----------|------|
| Local | Response ended prematurely | High concurrency overload |
| Deployment | HTTP 502 | Server/proxy failure (Render infra) |

### Deployment Failure Pattern

- Every request returned:
  - `status: http_error`
  - `error: 502`
- Suggests:
  - Upstream service crash
  - Timeout / worker killed
  - Reverse proxy rejection

---

## 6. Resource Utilization

| Metric | Local | Deployment |
|------|------|------------|
| CPU Usage | Scales up to ~90% | Very low (~5–10%) |
| Memory Usage | Stable (50–75%) | High baseline (~82%) |
| Behavior | Efficient utilization | Underutilized due to failures |

### Insight

- Deployment is **not resource-bound**
- Failures occur **before actual processing begins**

---

## 7. Scalability Comparison

| Aspect | Local | Deployment |
|------|------|------------|
| Handles 1 worker | ✅ Stable | ❌ Fails |
| Handles 3 workers | ✅ Stable | ❌ Not tested (baseline failed) |
| Handles 5 workers | ⚠️ Partial failure | ❌ Impossible |
| Horizontal scaling | Moderate | None |

---

## 8. Root Cause Analysis (Deployment)

Based on behavior:

### Likely Issues with Render Free Tier:

1. **Request Timeout Limits**
   - Long-running scraping jobs exceed limits

2. **Cold Start Delays**
   - Instance not ready → 502 errors

3. **Single-threaded / limited worker execution**
   - Cannot handle blocking Playwright operations

4. **Memory Constraints**
   - Browser automation may exceed limits

5. **Reverse Proxy Restrictions**
   - Render kills long HTTP connections

---
## 9. System Requirements (Derived from Local Testing)

Based on the performance observed in the local environment, the following system requirements are recommended for stable and scalable deployment of the Instagram Reels Scraper.

---

### 9.1 Workload Characteristics

- Average request duration: **~40 seconds per profile**
- Scraping type: **Browser automation (Playwright)**
- Nature: **CPU-intensive + moderate memory usage**
- Concurrency limit (stable): **3 workers**
- Failure threshold observed: **≥5 workers**

---

### 9.2 Per-Worker Resource Estimation

| Resource | Estimated Usage |
|---------|----------------|
| CPU | 0.5 – 1 vCPU |
| Memory | 400MB – 700MB |
| Network | Moderate |
| Disk | Minimal |

---

### 9.3 Minimum System Requirements (Stable Operation)

Suitable for low-scale usage and testing:

- **CPU:** 2 vCPU  
- **Memory:** 4 GB RAM  
- **Concurrency:** 2–3 workers  
- **Expected Behavior:** Stable scraping with no failures  

---

### 9.4 Recommended Production Configuration

Balanced setup for reliability and moderate scale:

- **CPU:** 4 vCPU  
- **Memory:** 8 GB RAM  
- **Concurrency:** 4–6 workers  
- **Expected Throughput:** ~8–10 requests per minute  
- **Notes:** Provides headroom for CPU spikes and parallel scraping  

---

### 9.5 High-Scale Configuration (Future Expansion)

For handling larger workloads and multiple users:

- **CPU:** 8 vCPU  
- **Memory:** 16 GB RAM  
- **Concurrency:** 8–12 workers (with queue system)  
- **Requirement:** Task queue (Redis + Celery/RQ) mandatory  

---

### 9.6 Deployment Considerations

- Browser-based scraping (Playwright) requires:
  - Sufficient CPU for rendering and execution
  - Memory overhead per browser instance
- Long-running requests are **not suitable for serverless or free-tier platforms**
- A **queue-based architecture** is strongly recommended:
  
---

### 9.7 Cost Estimation

| Infrastructure | Specs | Estimated Cost |
|---------------|------|----------------|
| Budget VPS | 4 vCPU / 8GB RAM | ₹1,800 – ₹2,800 / month |
| GCP VM | 4 vCPU / 8GB RAM | ₹9,000 – ₹12,000 / month |

---

### 9.8 Final Recommendation

For production deployment:

> Use a **4 vCPU, 8GB RAM VPS with 4–6 workers and a queue-based architecture** to ensure stability, scalability, and cost efficiency.

---