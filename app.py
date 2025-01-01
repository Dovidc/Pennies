import threading
from flask import Flask, request, jsonify
from reddit_scanner import initialize_reddit, fetch_reddit_data
from db_manager import initialize_db, save_to_db, get_word_data
from visualizer import generate_plots_for_top_words
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Initialize Flask app, database, and Reddit API
app = Flask(__name__)
reddit = initialize_reddit()

# Scheduler to automate tasks
scheduler = BackgroundScheduler()

def automated_data_fetch():
    """
    Fetch data from Reddit automatically and save it to the database.
    """
    try:
        print(f"[{datetime.utcnow()}] Automated data fetch started.")
        subreddits = ["pennystocks"]
        days = 1  # Fetch data for the last day
        data = fetch_reddit_data(reddit, subreddits, days)
        save_to_db(data)  # Updated to handle locking issues
        print(f"[{datetime.utcnow()}] Data fetch complete.")
    except Exception as e:
        print(f"Error during automated data fetch: {e}")

def automated_plot_generation():
    """
    Generate the graph automatically based on the latest data.
    """
    try:
        print(f"[{datetime.utcnow()}] Automated graph generation started.")
        conn, cursor = initialize_db()
        cursor.execute("SELECT word FROM word_data GROUP BY word ORDER BY COUNT(*) DESC LIMIT 10")
        top_words = [word[0] for word in cursor.fetchall()]
        all_data = {word: get_word_data(word) for word in top_words}
        generate_plots_for_top_words(all_data)
        print(f"[{datetime.utcnow()}] Graph generation complete.")
    except Exception as e:
        print(f"Error during automated graph generation: {e}")

# Schedule automated tasks
scheduler.add_job(automated_data_fetch, 'interval', hours=1)  # Fetch data every hour
scheduler.start()

@app.route('/scan', methods=['POST'])
def scan():
    subreddits = ["pennystocks"]  # Only scan r/pennystocks
    days = request.json.get('days', 7)  # Default to 7 days if not provided
    
    # Fetch data from Reddit
    data = fetch_reddit_data(reddit, subreddits, days)
    
    # Save to the database
    save_to_db(data)  # Updated to handle locking issues
    
    # Return a summary of top words detected
    word_frequencies = {word: len(timestamps) for word, timestamps in data.items()}
    top_words = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        "message": "Scan complete!",
        "top_words": top_words
    })

@app.route('/plot', methods=['GET'])
def plot():
    group_by = request.args.get('group_by', "day")  # 'day' or 'week'
    
    # Get the top 10 words from the database
    conn, cursor = initialize_db()
    cursor.execute("SELECT word FROM word_data GROUP BY word ORDER BY COUNT(*) DESC LIMIT 10")
    top_words = [word[0] for word in cursor.fetchall()]
    
    # Prepare the data for plotting
    all_data = {word: get_word_data(word) for word in top_words}
    threading.Thread(target=generate_plots_for_top_words, args=(all_data, group_by)).start()
    
    return jsonify({"message": "Plot generation in progress."})

if __name__ == "__main__":
    print("Starting server and scheduler...")
    app.run(debug=True)
