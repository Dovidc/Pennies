from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

def generate_plots_for_top_words(all_data, group_by="day"):
    plt.figure(figsize=(10, 6))

    # Use a categorical colormap with distinct colors
    cmap = get_cmap("tab20")  # "tab20" provides 20 distinct colors
    num_colors = len(all_data)
    colors = [cmap(i % 20) for i in range(num_colors)]  # Cycle through if >20 tickers

    for i, (word, data) in enumerate(all_data.items()):
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

        # Plot the data with a unique color
        plt.plot(
            sorted_dates,
            counts,
            marker="o",
            label=word,
            color=colors[i]  # Assign a unique color from the colormap
        )

    plt.title("Top 15 Most Mentioned Tickers on r/pennystocks")
    plt.suptitle("Pennywise", fontsize=27, color="red")  # Subtitle
    plt.xlabel("Date")
    plt.ylabel("Mentions")
    plt.legend()
    plt.grid()
    plt.show()


