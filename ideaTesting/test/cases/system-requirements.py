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
os.makedirs("capacity_reports", exist_ok=True)

# -----------------------
# 🔹 STREAM USER FUNCTION
# -----------------------
def stream_user(username, days=365):
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
        with requests.get(url, stream=True, timeout=600) as response:
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

    # classify result
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

    # classify results
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
        "memory_end": psutil.virtual_memory().percent,
        "total_reels": sum(r["reels_scraped"] for r in results)
    }

    return summary, results


# -----------------------
# 🔹 CAPACITY BENCHMARK
# -----------------------
def capacity_benchmark(usernames):
    print("\n=== CAPACITY BENCHMARK: Increasing Users Until Limit ===")
    capacity_results = []

    workers = 1
    step = 1  # increment users by 1 each round
    max_failures_pct = 20  # stop if more than 20% failures
    max_cpu_percent = 95   # stop if CPU is above 95%
    max_memory_percent = 95 # stop if RAM is above 95%

    while True:
        print(f"\n🚀 Testing {workers} concurrent users...")

        # prepare exact number of test users
        test_users = []
        while len(test_users) < workers:
            test_users.extend(usernames)
        test_users = test_users[:workers]

        summary, results = concurrency_test(test_users, workers)

        # calculate failure %
        failure_pct = round((summary["failures"] / summary["total_requests"]) * 100, 2)

        # save results
        capacity_results.append({
            "workers": workers,
            "total_requests": summary["total_requests"],
            "success": summary["success"],
            "empty": summary["empty"],
            "failures": summary["failures"],
            "failure_rate_%": failure_pct,
            "total_reels": summary["total_reels"],
            "avg_reels_per_user": round(summary["total_reels"] / workers, 2),
            "reels_per_sec": round(summary["total_reels"] / summary["total_time"], 2),
            "avg_latency": summary["avg_latency"],
            "cpu_start": summary["cpu_start"],
            "cpu_end": summary["cpu_end"],
            "memory_start": summary["memory_start"],
            "memory_end": summary["memory_end"]
        })

        # print summary
        print(
            f"Users: {workers} | Reels: {summary['total_reels']} | "
            f"Throughput: {round(summary['total_reels']/summary['total_time'],2)} reels/sec | "
            f"Failures: {failure_pct}%"
        )

        # 🚨 check stopping conditions
        if failure_pct >= max_failures_pct:
            print(f"⚠️ Stopping: Failures exceeded {max_failures_pct}% → likely Instagram rate limit")
            break

        if summary["cpu_end"] >= max_cpu_percent or summary["memory_end"] >= max_memory_percent:
            print("⚠️ Stopping: System resource exhausted (CPU or RAM too high)")
            break

        workers += step  # increase concurrency

    return capacity_results


# -----------------------
# 🔹 SAVE REPORT
# -----------------------
def save_report(report):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"capacity_reports/report_capacity_{timestamp}.json"
    with open(filepath, "w") as f:
        json.dump(report, f, indent=4)
    print(f"\n✅ Report saved → {filepath}")


# -----------------------
# 🔹 MAIN
# -----------------------
def main():
    print("=== Instagram Scraper Capacity Benchmark ===")

    # single user baseline
    print("\n--- Single User Baseline ---")
    single_result = stream_user(INSTAGRAM_USERS[0])
    print(
        f"Reels: {single_result['reels_scraped']} | "
        f"Status: {single_result['status']} | "
        f"Duration: {single_result['duration']}s"
    )

    # capacity benchmark
    capacity_results = capacity_benchmark(INSTAGRAM_USERS)

    report = {
        "single_user_baseline": single_result,
        "capacity_results": capacity_results,
        "system_info": {
            "cpu_cores": psutil.cpu_count(),
            "total_memory_mb": round(psutil.virtual_memory().total / 1024 / 1024)
        }
    }

    save_report(report)


if __name__ == "__main__":
    main()