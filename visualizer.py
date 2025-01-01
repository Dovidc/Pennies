from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_plots_for_top_words(all_data, group_by="day"):
    plt.figure(figsize=(10, 6))

    for word, data in all_data.items():
        dates = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").date() for ts in data]

        # Group by day or week
        date_counts = defaultdict(int)
        for date in dates:
            if group_by == "week":
                date = date - timedelta(days=date.weekday())
            date_counts[date] += 1

        # Prepare data for plotting
        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[date] for date in sorted_dates]

        # Plot the data
        plt.plot(sorted_dates, counts, marker="o", label=word)

    plt.title("Top 10 Most Mentioned Tickers on r/pennystocks")
    plt.xlabel("Date")
    plt.ylabel("Mentions")
    plt.legend()
    plt.grid()
    plt.show()

