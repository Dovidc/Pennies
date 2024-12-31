from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_plots_for_top_words(all_data, group_by="day"):
    plt.figure(figsize=(10, 6))

    # For each word in the data, generate a plot line
    for word, data in all_data.items():
        # Parse timestamps into dates
        invalid_timestamps = 0
        dates = []
        
        # Try to parse each timestamp
        for ts in data:
            try:
                date = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").date()
                dates.append(date)
            except ValueError:
                invalid_timestamps += 1
                continue  # Skip invalid timestamps

        if invalid_timestamps > 0:
            print(f"Found {invalid_timestamps} invalid timestamps for word '{word}'. Skipping.")
            continue

        # Group by date or week
        date_counts = defaultdict(int)
        for date in dates:
            if group_by == "week":
                date = date - timedelta(days=date.weekday())  # Group by week start (Monday)
            date_counts[date] += 1

        # Sort dates and counts
        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[date] for date in sorted_dates]

        # Plot the data for this word
        plt.plot(sorted_dates, counts, marker="o", label=word)

    # Customize and display the plot
    plt.title("Top 5 Most Frequent Words Over Time")
    plt.xlabel("Date")
    plt.ylabel("Occurrences")
    plt.legend()
    plt.grid()
    plt.show()
