# Instagram Data Pipeline: Research & Cost Analysis

---

## 1. Apify

Apify is a full-stack cloud platform designed for web scraping, data extraction, and browser automation.

### Key Scraper Types

Depending on your goals, you can use specialized scrapers for better performance and lower costs:

- **Instagram Scraper (All-in-One):** A comprehensive tool that can scrape posts, profiles, hashtags, and places.
- **Instagram Profile Scraper:** Focuses on account metadata such as bio, follower/following counts, verification status, and recent posts.
- **Instagram Hashtag Scraper:** Extracts recent posts and reels associated with specific hashtags, including engagement metrics like likes and comment counts.
- **Instagram Reel Scraper:** Specifically designed for video content, capturing captions, timestamps, transcripts, and view counts.
- **Instagram Comments Scraper:** Useful for sentiment analysis; extracts comment text, owner IDs, and timestamps from specific posts.

### API Parameters

| Parameter          | Type    | Description                                                  |
| :----------------- | :------ | :----------------------------------------------------------- |
| `timeout`          | number  | Max seconds the run can take. Defaults to actor's config.    |
| `memory`           | number  | RAM in MB. Must be a power of 2, minimum 128.                |
| `maxTotalChargeUsd`| number  | For pay-per-event actors — caps the USD cost of the run.     |
| `restartOnError`   | boolean | If `true`, automatically restarts the run if it crashes.     |
| `format`           | string  | Output format: `json`, `jsonl`, `csv`, `html`, `xlsx`, `xml`, `rss`. |
| `startedAfter`     | string  | ISO 8601 datetime — filter runs started after this time.     |
| `startedBefore`    | string  | ISO 8601 datetime — filter runs started before this time.    |

---

## 2. Playwright

Playwright is a modern, open-source automation library developed by Microsoft for end-to-end testing and web scraping.

### Features

- **Dynamic Loading:** Instagram is a single-page application (SPA) that heavily uses JavaScript. Playwright's auto-waiting feature ensures elements load before data is extracted.
- **Infinite Scrolling:** Playwright can be programmed to scroll down a profile or hashtag page to load and scrape more results.
- **Authentication:** It can automate Instagram login flows, including 2FA handling, and store session cookies for subsequent runs.

### Challenges

1. Headless browser requires heavy resource usage.
2. Instagram actively challenges automated profile access.
3. Cookies expire frequently; when present, Instagram sends an OTP to verify the user.
4. Deployment server IPs are flagged as suspicious by Instagram.
5. Instagram's lazy-load behaviour significantly increases scraping time.

### Notes

The more the scraper runs, the more edge cases are encountered each resolved challenge makes the tool more robust for production use.

---

## 3. Cost Estimation

### 3.1 Apify

| Results      | Cost       | Cost per Result |
| :----------- | :--------- | :-------------- |
| 74           | $0.200     | $0.0027         |
| 1            | $0.003     | $0.0030         |
| 192          | $0.518     | $0.0027         |
| 109          | $0.294     | $0.0027         |
| 175          | $0.473     | $0.0027         |
| 120          | $0.324     | $0.0027         |
| 38           | $0.103     | $0.0027         |
| **Total**    | **$2.06**  |                 |

```
 Note: The sum of individual run costs is $1.915. The difference of $0.145 from the billed $2.06 is attributed to platform compute overhead not reflected in per-run breakdowns.
```


**Free tier capacity:**
```
$5.00 / $0.0027 = ~1,850 results
```

---

### 3.2 AssemblyAI

Transcription is free for 333 hours as a one-time signup credit; it does not reset.

```
333 hours = 19,980 minutes = ~39,960 reels
```

After the free tier is exhausted, billing starts at **$0.15 per hour**.

---

### 3.3 Playwright vs. Apify

#### Key Differences

| Aspect               | Apify                                              | Playwright                                      |
| :------------------- | :------------------------------------------------- | :---------------------------------------------- |
| Video URL access     | Directly provides the reel video URL               | Requires additional tooling (e.g. yt-dlp)       |
| Challenge handling   | Handled internally by the platform                 | Must be handled manually in code                |
| Scrolling            | Limited                                            | Full infinite scroll control                    |
| Control              | Limited to API parameters                          | Full control over scraping logic                |
| Speed                | Faster   API-based                                 | Slower   headless browser                       |
| AssemblyAI pipeline  | Direct video URL can be passed without downloading | Requires download step before transcription     |


#### Cost Comparison

| Volume (reels/month) | Apify Cost (@$0.0027) | Hetzner Cost | Cheaper Option |
| :------------------- | :-------------------- | :----------- | :------------- |
| 1,000                | $2.70                 | $48.00       | Apify          |
| 5,000                | $13.50                | $48.00       | Apify          |
| 10,000               | $27.00                | $48.00       | Apify          |
| 18,000               | $48.60                | $48.00       | Break-even     |
| 50,000               | $135.00               | $48.00       | Hetzner        |
| 100,000              | $270.00               | $48.00       | Hetzner        |
| 500,000              | $1,350.00             | $48.00       | Hetzner        |
| 2,100,000            | $5,670.00             | $48.00       | Hetzner        |
