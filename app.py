from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import time

load_dotenv()

app = Flask(__name__, static_folder='static')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def extract_video_id(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
    except:
        pass

    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\?\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\?\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript_with_retries(video_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                return ' '.join([entry['text'] for entry in transcript_list])
            except Exception as e:
                print(f"YouTube Transcript API failed: {str(e)}")

            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                for transcript in transcript_list:
                    try:
                        if transcript.is_generated:
                            continue
                        translated = transcript.translate('en')
                        return ' '.join([entry['text'] for entry in translated.fetch()])
                    except:
                        continue

                for transcript in transcript_list:
                    try:
                        translated = transcript.translate('en')
                        return ' '.join([entry['text'] for entry in translated.fetch()])
                    except:
                        continue
                        
            except Exception as e:
                print(f"Transcript translation failed: {str(e)}")

            try:
                yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
                caption = yt.captions.get_by_language_code('en')
                if not caption:
                    captions = yt.captions.all()
                    if captions:
                        caption = captions[0]
                
                if caption:
                    transcript_text = caption.generate_srt_captions()
                    cleaned_text = '\n'.join(
                        line for line in transcript_text.split('\n')
                        if not line.strip().isdigit() and '-->' not in line and line.strip()
                    )
                    if cleaned_text.strip():
                        return cleaned_text

            except Exception as e:
                print(f"Pytube captions failed: {str(e)}")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))
                continue
            raise e

    raise Exception("Could not retrieve transcript using any available method")

def get_video_transcript(url):
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return "Error: Invalid YouTube URL format"

        transcript_text = get_transcript_with_retries(video_id)
        
        if not transcript_text or not transcript_text.strip():
            return "Error: Could not extract any text from the video"

        return transcript_text

    except Exception as e:
        return f"Error processing video: {str(e)}"

def summarize_text(text):
    prompt = f"""
    Please provide a clear and concise summary of the following video transcript. Format your response exactly as follows, without any markdown symbols or asterisks:

    Main Topic:
    [Write the main topic here]

    Key Points:
    • [First key point]
    • [Second key point]
    • [Third key point]
    [Add more bullet points as needed]

    Conclusion:
    [Write a brief conclusion]

    Here's the transcript to summarize:
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
        summary = re.sub(r'\*\*', '', summary) 
        summary = re.sub(r'\*', '', summary)    
        return summary
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        transcript = get_video_transcript(video_url)
        
        if transcript.startswith('Error'):
            return jsonify({'error': transcript}), 400
        
        summary = summarize_text(transcript)
        
        return jsonify({'summary': summary})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
