import requests
import json
import time
import os
import psutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 🔹 API endpoint
BASE_URL = "http://127.0.0.1:8000"

# 🔹 Test Instagram usernames
INSTAGRAM_USERS = [
    "aliaabhatt",
    "iam_srk",
    "bhuvan.bam22",
    "janhvikapoor",
    "shubmangill",
    "samantharuthprabhuoffl",
    "hrithikroshan",
    "ranveersingh",
    "leomessi",
    "therock"
]

# 🔹 Directory for reports
os.makedirs("stress_reports", exist_ok=True)

# -----------------------
# 🔹 STREAM PROFILE
# -----------------------
def stream_user(username, days=2):
    url = f"{BASE_URL}/scrape/reels?username={username}&days={days}"
    stats = {
        "username": username,
        "reels_scraped": 0,
        "start_time": time.time(),
        "end_time": None,
        "duration": None,
        "status": "success",
        "error": None,
        "debug": None,
        "cpu_percent_start": psutil.cpu_percent(interval=None),
        "memory_percent_start": psutil.virtual_memory().percent
    }

    received_any_data = False

    try:
        with requests.get(url, stream=True, timeout=300) as response:

            if response.status_code != 200:
                stats["status"] = "http_error"
                stats["error"] = response.status_code
                return finalize(stats)

            for line in response.iter_lines():
                if not line:
                    continue

                received_any_data = True
                decoded = line.decode()

                if decoded.startswith("data: "):
                    try:
                        payload = json.loads(decoded.replace("data: ", ""))

                        # OPTIONAL: validate payload contains reel info
                        if isinstance(payload, dict):
                            stats["reels_scraped"] += 1

                    except Exception as e:
                        stats["status"] = "parse_error"
                        stats["error"] = str(e)
                        return finalize(stats)

    except Exception as e:
        stats["status"] = "exception"
        stats["error"] = str(e)
        return finalize(stats)

    # 🔥 classify result properly
    if stats["status"] == "success":
        if not received_any_data:
            stats["status"] = "empty"
            stats["debug"] = "no_stream_data"
        elif stats["reels_scraped"] == 0:
            stats["status"] = "empty"
            stats["debug"] = "no_reels_extracted"

    return finalize(stats)


# -----------------------
# 🔹 FINALIZE METRICS
# -----------------------
def finalize(stats):
    stats["end_time"] = time.time()
    stats["duration"] = round(stats["end_time"] - stats["start_time"], 2)
    stats["cpu_percent_end"] = psutil.cpu_percent(interval=None)
    stats["memory_percent_end"] = psutil.virtual_memory().percent
    return stats


# -----------------------
# 🔹 CONCURRENT USER TEST
# -----------------------
def concurrency_test(usernames, workers):
    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(stream_user, user) for user in usernames]
        for future in as_completed(futures):
            results.append(future.result())

    duration = round(time.time() - start_time, 2)

    # 🔥 proper classification
    success = sum(1 for r in results if r["status"] == "success")
    empty = sum(1 for r in results if r["status"] == "empty")
    failures = sum(1 for r in results if r["status"] not in ["success", "empty"])

    durations = [r["duration"] for r in results if r["duration"] is not None]
    avg_latency = round(sum(durations) / len(durations), 2) if durations else 0

    summary = {
        "workers": workers,
        "total_requests": len(usernames),
        "success": success,
        "empty": empty,
        "failures": failures,
        "total_time": duration,
        "avg_latency": avg_latency,
        "cpu_start": psutil.cpu_percent(interval=None),
        "cpu_end": psutil.cpu_percent(interval=None),
        "memory_start": psutil.virtual_memory().percent,
        "memory_end": psutil.virtual_memory().percent
    }

    return summary, results


# -----------------------
# 🔹 RAMP TEST
# -----------------------
def ramp_test(usernames, max_workers_list=[1,3,5,10,15,20,30,50]):
    print("\n=== RAMP TEST: System & Rate Limits ===")

    ramp_results, detailed_results = [], []

    for workers in max_workers_list:
        print(f"\n🚀 Testing {workers} concurrent users...")

        summary, results = concurrency_test(usernames * workers, workers)

        ramp_results.append(summary)
        detailed_results.append({"workers": workers, "results": results})

        print(
            f"   Success: {summary['success']} | "
            f"Empty: {summary['empty']} | "
            f"Failures: {summary['failures']} | "
            f"Avg Latency: {summary['avg_latency']}s"
        )

        print(
            f"   CPU: {summary['cpu_start']} → {summary['cpu_end']}%, "
            f"Memory: {summary['memory_start']} → {summary['memory_end']}%"
        )

        if summary["failures"] > 0:
            print(f"⚠️ Failures detected at ~{workers} users → bottleneck or rate limit")
            break

    return ramp_results, detailed_results


# -----------------------
# 🔹 SAVE REPORT
# -----------------------
def save_report(report):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"stress_reports/report_stressTest_{timestamp}.json"

    with open(filepath, "w") as f:
        json.dump(report, f, indent=4)

    print(f"\n✅ Report saved → {filepath}")


# -----------------------
# 🔹 MAIN
# -----------------------
def main():
    print("=== Instagram Scraper Stress Test ===")

    # 🔹 Single user test
    print("\n--- Best Case: Single User Test ---")
    single_result = stream_user(INSTAGRAM_USERS[0])

    print(
        f"   Reels: {single_result['reels_scraped']} | "
        f"Status: {single_result['status']} | "
        f"Duration: {single_result['duration']}s"
    )

    # 🔹 Ramp test
    print("\n--- Worst Case: High Concurrency Ramp Test ---")
    ramp_summary, ramp_details = ramp_test(INSTAGRAM_USERS)

    report = {
        "single_profile_test": [single_result],
        "concurrency_summary": ramp_summary,
        "concurrency_detailed": ramp_details,
        "system_info": {
            "cpu_cores": psutil.cpu_count(),
            "total_memory_mb": round(psutil.virtual_memory().total / 1024 / 1024)
        }
    }

    save_report(report)


if __name__ == "__main__":
    main()
