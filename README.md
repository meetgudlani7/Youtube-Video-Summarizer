# YouTube Video Transcript Summarizer

This Flask application allows you to input a YouTube video URL, extracts its transcript, and generates a concise summary using Google's Gemini Pro generative AI model.

## Features

- **Extract Transcripts**: Supports auto-generated and manual transcripts via YouTube APIs and Pytube.
- **Retry Mechanism**: Ensures reliable transcript extraction with multiple fallback methods.
- **AI-Powered Summarization**: Uses Google's Gemini Pro AI model to generate a structured summary.
- **Error Handling**: Provides detailed error messages for invalid URLs, missing transcripts, or API issues.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/youtube-transcript-summarizer.git
   cd youtube-transcript-summarizer
