import streamlit as st
import requests
from textblob import TextBlob
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs

# Set your YouTube API Key
API_KEY = "AIzaSyBgHxw_GJy6eeP_A4QwgPOA3_rCocjbmWs"


def extract_video_id(youtube_url):
    """Extract video ID from YouTube URL."""
    parsed_url = urlparse(youtube_url)
    query_params = parse_qs(parsed_url.query)
    if "v" in query_params:
        return query_params["v"][0]
    return None


def fetch_comments(video_id):
    """Fetch comments from a YouTube video using the YouTube Data API v3."""
    url = f"https://youtube.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults=100&key={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        comments = [
            item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            for item in data["items"]
        ]
        return comments
    else:
        st.error(
            f"Error fetching comments: {response.status_code}, {response.json()['error']['message']}"
        )
        return []


def analyze_sentiment(comment):
    """Analyze the sentiment of a comment using TextBlob."""
    blob = TextBlob(comment)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "Good"
    elif polarity < 0:
        return "Bad"
    else:
        return "Neutral"


def main():
    st.title("YouTube Video Comment Sentiment Analyzer 🎥")
    st.markdown(
        "This app fetches comments from a YouTube video and analyzes their sentiment (Good, Bad, or Neutral)."
    )

    # Input YouTube Video URL
    youtube_url = st.text_input("Enter YouTube Video URL", "")

    if youtube_url:
        video_id = extract_video_id(youtube_url)

        if video_id:
            st.success(f"Extracted Video ID: {video_id}")
            st.write("Fetching comments...")

            # Fetch Comments
            comments = fetch_comments(video_id)

            if comments:
                st.write(f"Fetched {len(comments)} comments.")

                # Analyze Sentiment
                sentiment_data = []
                for comment in comments:
                    sentiment = analyze_sentiment(comment)
                    sentiment_data.append({"Comment": comment, "Sentiment": sentiment})

                df = pd.DataFrame(sentiment_data)

                # Display Results
                st.write("### Comment Sentiments")
                st.dataframe(df)

                # Sentiment Visualization
                st.write("### Sentiment Analysis Results")
                sentiment_counts = df["Sentiment"].value_counts()
                st.bar_chart(sentiment_counts)

        else:
            st.error("Invalid YouTube URL. Please enter a valid URL.")

if __name__ == "__main__":
    main()
