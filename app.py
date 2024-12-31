import threading
from flask import Flask, request, jsonify
from reddit_scanner import initialize_reddit, fetch_reddit_data
from db_manager import initialize_db, save_to_db, get_word_data
from visualizer import generate_plots_for_top_words


app = Flask(__name__)
reddit = initialize_reddit()
conn, cursor = initialize_db()

# This function will run the plot generation in a separate thread
def generate_plot_in_background(data, group_by="day"):
    threading.Thread(target=generate_plots_for_top_words, args=(data, group_by)).start()

@app.route('/scan', methods=['POST'])
def scan():
    subreddits = request.json.get('subreddits', ["pennystocks", "wallstreetbets"])
    days = request.json.get('days', 21)
    
    # Fetch data from Reddit
    data = fetch_reddit_data(reddit, subreddits, days)
    
    # Save to the database
    save_to_db(cursor, data)
    
    # Calculate the frequency of each word
    word_frequencies = {word: len(timestamps) for word, timestamps in data.items()}
    
    # Sort the words by frequency and get the top 5
    top_5_words = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return jsonify({
        "message": "Scan complete!",
        "words_detected": list(word_frequencies.keys()),
        "top_5_words": top_5_words
    })

@app.route('/plot', methods=['GET'])
def plot():
    group_by = request.args.get('group_by', "day")  # 'day' or 'week'
    
    # Get the top 5 words from the database
    cursor.execute("SELECT word FROM word_data GROUP BY word ORDER BY COUNT(*) DESC LIMIT 12")
    top_5_words = [word[0] for word in cursor.fetchall()]
    
    # Prepare the data for all top 5 words
    all_data = {}
    for word in top_5_words:
        data = get_word_data(cursor, word)
        all_data[word] = data
    
    # Run the plotting in the background for all top words
    threading.Thread(target=generate_plots_for_top_words, args=(all_data, group_by)).start()
    
    return jsonify({"message": "Plot generation for top 6 words is in progress."})

if __name__ == "__main__":
    app.run(debug=True)



