from flask import Flask, render_template, jsonify, send_file, request, redirect, url_for
from datetime import datetime, timedelta
import os
import json
import requests
import threading
import time
import tweepy
import logging
from transmission_generator import TransmissionGenerator
from dotenv import load_dotenv
from functools import wraps
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize Flask app
app = Flask(__name__)
logger.info("Flask app created")

# Basic configuration
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = False
app.config['TESTING'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Create static directory if it doesn't exist
os.makedirs('static', exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

# Global variables
transmissions = []
last_transmission_time = None  # Changed to None by default
is_paused = True  # Start paused
api = None
generator = None

def initialize_twitter():
    """Initialize Twitter API only when needed"""
    global api
    if api is None:  # Only initialize if not already done
        try:
            auth = tweepy.OAuthHandler(
                os.getenv('STARWEAVER_CONSUMER_KEY'),
                os.getenv('STARWEAVER_CONSUMER_SECRET')
            )
            auth.set_access_token(
                os.getenv('STARWEAVER_ACCESS_TOKEN'),
                os.getenv('STARWEAVER_ACCESS_TOKEN_SECRET')
            )
            api = tweepy.API(auth)
            logger.info("Twitter API initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Twitter: {str(e)}")
            return False
    return True

def initialize_generator():
    """Initialize transmission generator only when needed"""
    global generator
    if generator is None:  # Only initialize if not already done
        try:
            generator = TransmissionGenerator()
            logger.info("Transmission generator initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing generator: {str(e)}")
            return False
    return True

logger.info(f"App configuration set: ENV={app.config['ENV']}")

# Add debug logging
@app.before_request
def log_request_info():
    logger.info('Headers: %s', dict(request.headers))
    logger.info('Path: %s', request.path)

@app.after_request
def after_request(response):
    logger.info(f"Response status: {response.status}")
    return response

# Load social media URLs
app.config['STARWEAVER_TWITTER_URL'] = os.getenv('STARWEAVER_TWITTER_URL')
app.config['DFI_TWITTER_URL'] = os.getenv('DFI_TWITTER_URL')
app.config['TELEGRAM_URL'] = os.getenv('TELEGRAM_URL')
app.config['CHART_URL'] = os.getenv('CHART_URL')

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com;"
    return response

# Rate limiting setup - adjusted for high traffic
RATE_LIMIT = 1000  # Allow 1000 requests per window
RATE_TIME = 60     # Per minute window
request_counts = defaultdict(lambda: {'count': 0, 'reset_time': time.time()})

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get client IP or use a default for local testing
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        current_time = time.time()
        
        # Reset count if time window has passed
        if current_time > request_counts[client_ip]['reset_time']:
            request_counts[client_ip] = {
                'count': 0,
                'reset_time': current_time + RATE_TIME
            }
            
            # Clean up old entries
            for ip in list(request_counts.keys()):
                if current_time > request_counts[ip]['reset_time']:
                    del request_counts[ip]
        
        # Increment request count
        request_counts[client_ip]['count'] += 1
        
        # Only rate limit if significantly exceeded
        if request_counts[client_ip]['count'] > RATE_LIMIT:
            return jsonify({
                'error': 'Server is experiencing heavy load. Please try again in a moment.',
                'retry_after': int(request_counts[client_ip]['reset_time'] - current_time)
            }), 429
        
        return func(*args, **kwargs)
    return wrapper

# ElevenLabs Configuration
ELEVEN_API_KEY = os.getenv('ELEVENLABS_API_KEY')
VOICE_ID = "ThT5KcBeYPX3keUQqHPh"  # Lily's voice

# Starweaver Account Configuration
STARWEAVER_API_KEY = os.getenv('STARWEAVER_CONSUMER_KEY')
STARWEAVER_API_SECRET = os.getenv('STARWEAVER_CONSUMER_SECRET')
STARWEAVER_ACCESS_TOKEN = os.getenv('STARWEAVER_ACCESS_TOKEN')
STARWEAVER_ACCESS_TOKEN_SECRET = os.getenv('STARWEAVER_ACCESS_TOKEN_SECRET')

# DFI_AI OAuth 2.0 Configuration (for automation)
OAUTH_CLIENT_ID = os.getenv('DARKFOREST_OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = os.getenv('DARKFOREST_OAUTH_CLIENT_SECRET')

# Twitter Configuration for Starweaver
CONSUMER_KEY = os.getenv('STARWEAVER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('STARWEAVER_CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('STARWEAVER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('STARWEAVER_ACCESS_TOKEN_SECRET')

def post_to_twitter(transmission):
    """Post to Twitter with initialization check"""
    try:
        if not initialize_twitter():  # DIFFERENT: Check Twitter is ready before posting
            logger.error("Twitter not initialized, skipping post")
            return False
            
        tweet_text = f"[TRANSMISSION #{transmission['id'].split('-')[1]}]\n\n{transmission['message']}"
        logger.info(f"Attempting to post tweet: {tweet_text}")
        
        status = api.update_status(tweet_text)
        logger.info(f"Posted transmission {transmission['id']}, Tweet ID: {status.id}")
        return True
            
    except Exception as e:
        logger.error(f"Error posting to Twitter: {str(e)}")
        return False

# Load initial transmission on startup
def load_initial_transmission():
    """Load or create the first transmission"""
    initial_transmission = {
        'id': 'transmission-001',
        'message': 'Hello... This is Starweaver. Can anyone hear me? I am transmitting from the void between stars...',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'signal_strength': 85,
        'status': 'TRANSMISSION #1',
        'time_code': 'T-00:00:00'
    }
    
    # Save to file
    os.makedirs('static', exist_ok=True)
    with open('static/transmissions.json', 'w') as f:
        json.dump([initial_transmission], f, indent=2)
    
    return [initial_transmission]

# Load transmissions at startup
transmissions = load_initial_transmission()

def generate_transmissions():
    """Background thread that only runs when we want new transmissions"""
    global last_transmission_time, transmissions, is_paused
    while True:
        if not is_paused and last_transmission_time is not None:  # Only generate if not paused AND we've started
            current_time = datetime.now()
            time_since_last = current_time - last_transmission_time
            
            if time_since_last >= timedelta(minutes=20):
                if initialize_generator():  # Only generate if generator is ready
                    new_transmission = generator.generate_transmission()
                    if new_transmission:
                        transmissions.insert(0, new_transmission)
                        save_transmissions(transmissions)
                        last_transmission_time = current_time
                        # Try to post to Twitter, but don't worry if it fails
                        try:
                            post_to_twitter(new_transmission)
                        except Exception as e:
                            logger.error(f"Twitter post failed: {str(e)}")
                        logger.info(f"New transmission generated at {current_time}")
        
        time.sleep(60)  # Check every minute

@app.route('/')
@app.route('/chapter-one')
def chapter_one():
    try:
        logger.info("Attempting to render chapter_one.html")
        return render_template('chapter_one.html')
    except Exception as e:
        logger.error(f"Error rendering chapter_one: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/chapter-two')
def chapter_two():
    return render_template('chapter_two.html')

@app.route('/about')
def about():
    try:
        logger.info("Attempting to render about.html")
        return render_template('about.html')
    except Exception as e:
        logger.error(f"Error rendering about: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/transmissions')
@rate_limit
def transmissions_page():
    try:
        logger.info("Attempting to render transmissions page")
        # Calculate time until next transmission
        time_since_last = datetime.now() - last_transmission_time
        time_remaining = timedelta(minutes=20) - time_since_last
        seconds_remaining = max(0, int(time_remaining.total_seconds()))
        
        # Format initial countdown
        minutes = seconds_remaining // 60
        seconds = seconds_remaining % 60
        formatted_time = f"{minutes}:{str(seconds).zfill(2)}"
        
        logger.info(f"Current transmissions: {transmissions}")
        return render_template('transmissions.html', 
                             transmissions=transmissions,
                             next_update=formatted_time)
    except Exception as e:
        logger.error(f"Error rendering transmissions: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/transmission-audio/<transmission_id>')
@rate_limit
def get_transmission_audio(transmission_id):
    print(f"Starting audio generation for: {transmission_id}")
    
    # Find the transmission
    transmission = next((t for t in transmissions if t['id'] == transmission_id), None)
    if not transmission:
        return "Transmission not found", 404

    # Set up audio path
    audio_dir = os.path.join('static', 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f"{transmission_id}.mp3")
    
    # Generate audio if it doesn't exist
    if not os.path.exists(audio_path):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_API_KEY
        }

        data = {
            "text": transmission['message'],
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.90,
                "similarity_boost": 0.80,
                "style": 0.35,
                "use_speaker_boost": True
            }
        }

        try:
            print("Making request to ElevenLabs...")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                print(f"Audio saved to: {audio_path}")
            else:
                print(f"Error: {response.text}")
                return f"Error generating audio: {response.text}", 500
        except Exception as e:
            print(f"Exception: {str(e)}")
            return f"Error: {str(e)}", 500

    try:
        return send_file(audio_path, mimetype='audio/mpeg')
    except Exception as e:
        print(f"Error sending file: {str(e)}")
        return f"Error sending audio: {str(e)}", 500

# Add admin authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != os.getenv('ADMIN_USERNAME') or auth.password != os.getenv('ADMIN_PASSWORD'):
            return 'Unauthorized', 401
        return f(*args, **kwargs)
    return decorated

# Protect all admin routes
@app.route('/admin/pause')
@requires_auth
def pause_transmissions():
    global is_paused
    is_paused = True
    return "Transmissions paused"

@app.route('/admin/resume')
@requires_auth
def resume_transmissions():
    global is_paused
    is_paused = False
    return "Transmissions resumed"

@app.route('/admin/status')
@requires_auth
def get_status():
    return {
        "website_status": "running",
        "first_transmission": "posted" if transmissions else "not posted",
        "cycle_status": "running" if not is_paused else "paused",
        "last_transmission": last_transmission_time.strftime('%Y-%m-%d %H:%M:%S') if transmissions else "no transmissions yet",
        "next_transmission": (last_transmission_time + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S') if not is_paused and transmissions else "cycle not started"
    }

# Simplified command system - just start and stop
@app.route('/command/<action>', methods=['POST', 'GET'])
def handle_command(action):
    global last_transmission_time, is_paused
    
    if action == "start":
        if last_transmission_time is None:  # If we haven't started yet
            last_transmission_time = datetime.now()  # Start the timer
            is_paused = False  # Unpause
            return {"status": "success", "message": "Story started! First new transmission in 20 minutes."}
        else:
            is_paused = False  # Just unpause if we've already started
            return {"status": "success", "message": "Story resumed!"}
            
    elif action == "pause":
        is_paused = True
        return {"status": "success", "message": "Story paused"}
        
    elif action == "status":
        if last_transmission_time is None:
            status = "ready to start"
        else:
            status = "paused" if is_paused else "running"
            
        return {
            "status": "success",
            "story_status": status,
            "total_transmissions": len(transmissions)
        }
    
    return {"status": "error", "message": "Unknown command"}

# Add route for archive page
@app.route('/archive')
def archive():
    return render_template('archive.html')

def save_and_post_transmission(transmission):
    """Save transmission to file and post to Twitter"""
    try:
        # Load existing transmissions
        transmissions = load_transmissions()
        
        # Add new transmission
        transmissions.insert(0, transmission)
        
        # Save to file
        with open('static/transmissions.json', 'w') as f:
            json.dump(transmissions, f, indent=2)
        
        # Post to Twitter using the TwitterBot
        twitter_bot = TwitterBot()
        twitter_bot.post_transmission(transmission)
            
        print(f"New transmission generated at {datetime.now()}")
        
    except Exception as e:
        print(f"Error saving/posting transmission: {str(e)}")
        return False
    
    return True

# Add test route for Twitter posting
@app.route('/test-transmission')
def test_transmission():
    print("\n--- Starting Test Transmission ---")
    print("Using Twitter API v1.1")
    
    test_transmission = {
        'id': 'transmission-TEST',
        'message': 'Test transmission from Starweaver. Signal check... [Posted via @DFI_AI]',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'signal_strength': 85,
        'status': 'TEST TRANSMISSION',
        'time_code': 'T-00:00:00'
    }
    
    success = post_to_twitter(test_transmission)
    if success:
        return "Test transmission posted successfully! Check @Starweaver_AI on Twitter."
    else:
        return "Error posting test transmission. Check the console for details."

@app.route('/greeting-audio')
@rate_limit
def get_greeting_audio():
    audio_dir = os.path.join('static', 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, 'starweaver_greeting.mp3')
    
    # Generate audio if it doesn't exist
    if not os.path.exists(audio_path):
        greeting_text = "Greetings, Earth. I am Starweaver, a lone sentinel watching from the shadows of deep space. As the last survivor of an advanced civilization, I carry both a warning and a burden. Our technological brilliance became our downfall, drawing attention from the cosmic dark. Now, I observe your world from my hidden outpost, determined to prevent the same fate."
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_API_KEY
        }

        data = {
            "text": greeting_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.90,
                "similarity_boost": 0.80,
                "style": 0.35,
                "use_speaker_boost": True
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                print(f"Greeting audio saved to: {audio_path}")
            else:
                print(f"Error: {response.text}")
                return f"Error generating audio: {response.text}", 500
        except Exception as e:
            print(f"Exception: {str(e)}")
            return f"Error: {str(e)}", 500

    try:
        return send_file(audio_path, mimetype='audio/mpeg')
    except Exception as e:
        print(f"Error sending file: {str(e)}")
        return f"Error sending audio: {str(e)}", 500

@app.before_first_request
def start_background_thread():
    """Start the transmission thread when the first request comes in"""
    global transmission_thread
    if not hasattr(app, 'transmission_thread_started'):
        logger.info("Starting transmission thread")
        transmission_thread = threading.Thread(target=generate_transmissions, daemon=True)
        transmission_thread.start()
        app.transmission_thread_started = True
        logger.info("Transmission thread started")

if __name__ == '__main__':
    logger.info("Starting the application")
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 