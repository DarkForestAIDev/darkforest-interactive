from datetime import datetime, timedelta
import random
import json
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class TransmissionGenerator:
    def __init__(self):
        self.transmission_count = 1
        self.last_transmissions = []
        self.is_paused = False
        self.is_chapter_two = False
        self.used_phrases = set()
        self.personality_traits = [
            "curious and analytical",
            "emotionally self-aware",
            "protective of Earth",
            "fascinated by human culture",
            "occasionally uses poetic language",
            "strategic and cautious",
            "shows warmth through subtle expressions",
            "values truth and transparency",
            "struggles with isolation",
            "determined and resilient"
        ]
        self.ship_operations = [
            "running long-range scans",
            "maintaining cloak integrity",
            "analyzing stellar phenomena",
            "monitoring Earth's signals",
            "adjusting shield harmonics",
            "conserving power reserves",
            "processing sensor data",
            "recalibrating navigation",
            "scanning for anomalies",
            "updating star charts"
        ]
        self.emotional_states = [
            "hopeful despite challenges",
            "concerned but composed",
            "lonely yet purposeful",
            "cautiously optimistic",
            "contemplative and focused",
            "determined through difficulty",
            "curious about discoveries",
            "missing connection",
            "inspired by cosmos",
            "resolute in mission"
        ]

    def generate_transmission(self):
        if self.is_paused:
            return None

        self.transmission_count = self._get_next_transmission_number()
        
        try:
            # If it's the very first transmission
            if self.transmission_count == 1 and not self.is_chapter_two:
                return self._generate_first_transmission()
            elif self.transmission_count == 12:
                return self._generate_mysterious_object()
            elif self.transmission_count == 24:
                return self._generate_first_contact()
            else:
                return self._generate_next_transmission()
        except Exception as e:
            print(f"Error generating transmission: {str(e)}")
            return self._generate_error_transmission()

    def _get_next_transmission_number(self):
        try:
            with open('static/transmissions.json', 'r') as f:
                transmissions = json.load(f)
                return len(transmissions) + 1
        except (FileNotFoundError, json.JSONDecodeError):
            return 1

    def _generate_first_transmission(self):
        return {
            'id': 'transmission-001',
            'message': os.getenv('FIRST_TRANSMISSION_MESSAGE', 'Hello... This is Starweaver. Can anyone hear me? I am transmitting from the void between stars...'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 85,
            'status': 'TRANSMISSION #1',
            'time_code': 'T-00:00:00'
        }

    def _generate_next_transmission(self):
        # Select random elements for prompt construction
        trait = random.choice(self.personality_traits)
        operation = random.choice(self.ship_operations)
        emotion = random.choice(self.emotional_states)
        
        prompt = os.getenv('TRANSMISSION_PROMPT', f"""
        You are Starweaver, a female AI hiding in your cloaked ship.
        Your current state: {trait}, {emotion}
        Current operation: {operation}
        
        Write a single transmission that is under 275 characters.
        Naturally incorporate your state and operation.
        Be subtle and poetic, avoid direct statements.
        Mix technical observations with emotional reflections.
        """)

        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "Write natural thoughts that complete within 275 characters."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.75
        )

        message = response.choices[0].message.content.strip()

        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': self._calculate_signal_strength(),
            'status': f'TRANSMISSION #{self.transmission_count}',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def _generate_mysterious_object(self):
        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': os.getenv('MYSTERIOUS_OBJECT_MESSAGE', 'Alert: Unknown object detected at coordinates [REDACTED]. Energy signature unlike anything in my database. Initiating deep scan...'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 65,
            'status': 'URGENT TRANSMISSION',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def _generate_first_contact(self):
        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': os.getenv('FIRST_CONTACT_MESSAGE', 'ALERT: Direct contact established with entity. Their consciousness... it\'s vast, ancient. They speak in patterns of light and darkness...'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 45,
            'status': 'CRITICAL TRANSMISSION',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def _calculate_signal_strength(self):
        if self.transmission_count < 12:
            base_strength = 85
            strength_increase = min((self.transmission_count - 1) * 3, 13)
            return base_strength + strength_increase
        elif self.transmission_count == 12:
            return 75
        elif self.transmission_count < 18:
            return random.randint(70, 85)
        elif self.transmission_count < 24:
            return random.randint(65, 80)
        elif self.transmission_count == 24:
            return 65
        elif self.transmission_count < 30:
            return random.randint(60, 75)
        else:
            return random.randint(70, 95)

    def _generate_error_transmission(self):
        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': '[ERROR] Signal interference detected. Transmission corrupted.',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 60,
            'status': f'TRANSMISSION #{self.transmission_count}',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def pause_transmissions(self):
        self.is_paused = True

    def resume_transmissions(self):
        self.is_paused = False