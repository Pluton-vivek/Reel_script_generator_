## Instagram Reels Scraper: Performance & Capacity Analysis

---

### 1. Benchmark Results

#### Single User Baseline
| Metric | Value |
| :--- | :--- |
| Username | aliaabhatt |
| Reels Scraped | 63 |
| Duration | 128.55 sec |
| Status | Success |
| CPU (Start -> End) | 33.3% -> 51.1% |
| Memory (Start -> End) | 88.5% -> 60.9% |

---

#### Capacity Benchmark (Concurrent Users)
| Users | Success | Failures | Failure % | Total Reels | Avg Reels/User | Reels/sec | Avg Latency (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 1 | 0 | 0% | 63 | 63.0 | 0.58 | 108.24 |
| 2 | 2 | 0 | 0% | 64 | 32.0 | 0.50 | 117.86 |
| 3 | 3 | 0 | 0% | 129 | 43.0 | 1.01 | 119.30 |
| 4 | 4 | 0 | 0% | 308 | 77.0 | 0.88 | 196.05 |
| 5 | 5 | 0 | 0% | 379 | 75.8 | 0.92 | 227.32 |
| 6 | 6 | 0 | 0% | 549 | 91.5 | 1.10 | 268.58 |
| 7 | 7 | 0 | 0% | 761 | 108.71 | 1.47 | 338.70 |
| 8 | 4 | 4 | 50% | 334 | 41.75 | 0.89 | 133.86 |

---

### 2. Key Observations

* System scales effectively up to 7 concurrent users.
* Peak throughput is reached at 7 concurrent users (1.47 reels/sec).
* At 8 concurrent users, failure rate spikes to 50% due to resource exhaustion.
* Latency increases with concurrency due to CPU and browser instance contention.
* The system is compute-bound (CPU + Playwright instances), not network-bound.
* The 7-user limit represents a concurrency cap, not a time-based limit.
* With an average processing time of ~4–5 minutes per user, the system can handle ~70–90 users per hour under continuous load.
* Additional requests beyond 7 concurrent users are queued, increasing wait time.

---

### 3. System Requirements & Test Environment

#### Current Environment

* CPU: 12 cores  
* Memory: ~7.5 GB RAM  
* Architecture: Single machine  
* Workload: Playwright (browser-heavy)  
* Concurrency Model: ThreadPool (client-side)

---

#### Capacity Model (Reel-Based)

The system capacity is better defined in terms of reels processed rather than users.

* Stable throughput: ~1.1 reels/sec  
* Daily capacity (ideal): ~95,000 reels/day  
* Adjusted capacity (~50% real-world efficiency): ~47,000 reels/day  

This represents the total processing budget of the system.

---

#### User Capacity (Variable)

User capacity depends on reels requested per user:

| Scenario | Reels/User | Users/Day |
| :--- | :--- | :--- |
| Light usage | 50 | ~900 |
| Average usage | 70 | ~650 |
| Heavy usage (deep scrape) | 200 | ~230 |
| Very heavy usage | 300+ | ~150 |

Conclusion: system is reel-bound, not user-bound.

---

#### Capacity Gap

* Target workload: ~70,000 reels/day  
* Available capacity: ~47,000 reels/day  

Current system cannot meet target reliably.

---

### 4. Production Recommendation

To meet the target load, horizontal scaling is required.

#### Recommended Setup

* 2 worker nodes  
* Each node:
  * 8 vCPU  
  * 8–16 GB RAM  
  * 5–6 concurrent Playwright workers  

---

#### Expected Production Performance

| Metric | Value |
| :--- | :--- |
| Users/day | ~1000 (under average load) |
| Reels/user | ~70 |
| Total reels/day | ~70,000 |
| Time per user | ~2–6 minutes |
| Time per reel | ~1–2 seconds |

---

### 5. Cost Estimation (Official Pricing)

| Provider | Monthly Cost (INR) | Notes |
| :--- | :--- | :--- |
| AWS (EC2) | 45,000 - 55,000 | 8 vCPU / 16 GB |
| GCP | 47,000 - 55,000 | Similar to AWS |
| Render | 55,000 - 65,000 | Managed service |
| Railway | 38,000 - 45,000 | Usage-based |
| Hetzner (VPS) | 2,000 - 4,000 | 8 vCPU / 16 GB |

---

### 6. Conclusion

* Current system supports ~47,000 reels/day safely.
* User capacity varies based on workload per user.
* System is constrained by CPU and browser instances.
* Horizontal scaling is required to meet 70,000 reels/day target.
* Most cost-efficient solution:
  * 2 Hetzner VPS nodes
  * ~₹2,000–₹4,000/month total

---

### 7. Future Improvements

* Reuse browser instances instead of launching new ones
* Move to async worker model
* Introduce job queue (Redis + workers)
* Implement request limits or pagination for deep scraping
* Add proxy rotation to handle rate limiting

---