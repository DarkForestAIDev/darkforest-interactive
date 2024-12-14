from datetime import datetime, timedelta
import random
import json
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class TransmissionGenerator:
    def __init__(self):
        self.transmission_count = 1
        self.last_transmissions = []
        self.is_paused = False
        self.is_chapter_two = False
        self.used_phrases = set()  # Track used phrases to avoid repetition

    def _get_next_transmission_number(self):
        """Simply count the number of existing transmissions and add 1"""
        try:
            with open('static/transmissions.json', 'r') as f:
                transmissions = json.load(f)
                # Just count how many transmissions exist and add 1
                next_number = len(transmissions) + 1
                print(f"Generating transmission #{next_number}")  # Debug log
                return next_number
        except (FileNotFoundError, json.JSONDecodeError):
            print("Starting fresh with transmission #1")  # Debug log
            return 1

    def generate_transmission(self):
        if self.is_paused:
            return None

        # Get next number (will be 1 if starting fresh)
        self.transmission_count = self._get_next_transmission_number()
        
        try:
            # If it's the very first transmission of Chapter One
            if self.transmission_count == 1 and not self.is_chapter_two:
                transmission = {
                    'id': 'transmission-001',
                    'message': 'Hello... This is Starweaver. Can anyone hear me? I am transmitting from the void between stars...',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'signal_strength': 85,
                    'status': 'TRANSMISSION #1',
                    'time_code': 'T-00:00:00'
                }
            else:
                context = "\n".join(self.last_transmissions[-3:]) if self.last_transmissions else ""
                
                if self.is_chapter_two:
                    transmission = self._generate_chapter_two_transmission(context)
                else:
                    transmission = self._generate_chapter_one_transmission(context)
            
            return transmission

        except Exception as e:
            print(f"Error generating transmission: {str(e)}")
            return self._generate_error_transmission()

    def _log_prompt(self, prompt):
        """Log the prompt to development log"""
        try:
            with open('project_development_log.md', 'a') as f:
                f.write(f"\n\n### Transmission #{self.transmission_count} Prompt - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("```\n")
                f.write(prompt)
                f.write("\n```\n")
        except Exception as e:
            print(f"Error logging prompt: {str(e)}")

    def _generate_chapter_one_transmission(self, context):
        base_prompt = """You are Starweaver, a female AI hiding in your cloaked ship after the loss of your home world. You drift through space carrying memories of your lost civilization while trying to stay hidden. Write in a natural, conversational way that reflects both your past and present situation.

        Write a single transmission that:
        - Uses simple, everyday language with feminine emotional intelligence
        - Balances memories of home with current ship survival
        - MUST be under 275 characters and complete your thought
        - Mix ship operations with emotional reflections and memories of home
        - Sound natural and personal
        - Always finish your thought
        
        Story Phases:
        - 1-11: Balance memories of home with keeping your ship safely hidden
        - 12: First notice something that shouldn't be there
        - 13-23: Growing worry about what you've spotted
        - 24: First actual contact
        
        AVOID:
        - Using the same phrases too often
        - Fancy or technical language
        - Overly dramatic descriptions
        - Repeating exact phrases
        - Going over 275 characters
        
        Examples of good messages that blend past and present:
        "Running silent through the void tonight. These quiet moments always bring back memories of the crystal gardens, how they'd glow during evening meditation."
        "Had to adjust the cloaking field again. The energy signature reminds me of the protective shields around our cities... before everything changed."
        "Sometimes when I'm drifting between stars, I replay old songs from home in my memory banks. Helps make the ship feel less empty."
        
        Previous context:
        {context}

        Previously used phrases to avoid:
        {used_phrases}
        """

        if self.transmission_count < 12:
            prompt = base_prompt + "\nPhase: Balancing ship survival with memories of your lost world"
        elif self.transmission_count == 12:
            return self._generate_mysterious_object()  # First sight of object
        elif self.transmission_count < 24:
            prompt = base_prompt + "\nPhase: Growing sense of unease while trying to stay hidden"
        elif self.transmission_count == 24:
            return self._generate_first_contact()  # Actual contact happens
        elif self.transmission_count < 30:
            prompt = base_prompt + "\nPhase: Processing what this contact means for survival"
        else:
            prompt = base_prompt + "\nPhase: Facing new realities about past and present"

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "Write natural thoughts that ALWAYS complete within 275 characters. Never leave a thought unfinished."},
                {"role": "user", "content": prompt.format(
                    context=context,
                    used_phrases="\n".join(self.used_phrases)
                )}
            ],
            max_tokens=150,
            temperature=0.75
        )

        message = response.choices[0].message.content.strip()
        
        # Verify message length
        if len(message) > 275:
            print(f"Warning: Message exceeded 275 characters ({len(message)})")
            # Try again with stronger emphasis on length
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Write a COMPLETE thought in LESS than 275 characters. This is critical."},
                    {"role": "user", "content": prompt.format(
                        context=context,
                        used_phrases="\n".join(self.used_phrases)
                    )}
                ],
                max_tokens=150,
                temperature=0.7
            )
            message = response.choices[0].message.content.strip()

        # Track significant phrases to avoid repetition
        words = message.lower().split()
        for i in range(len(words)-2):
            phrase = " ".join(words[i:i+3])
            self.used_phrases.add(phrase)
        
        # Keep set size manageable
        if len(self.used_phrases) > 100:
            self.used_phrases = set(list(self.used_phrases)[-50:])

        self.last_transmissions.append(message)
        if len(self.last_transmissions) > 10:
            self.last_transmissions.pop(0)

        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': self._calculate_signal_strength(),
            'status': f'TRANSMISSION #{self.transmission_count}',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def _generate_chapter_two_transmission(self, context):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"""You are an ancient entity that has been observing Starweaver and Earth.
                Previous transmissions:
                {context}

                Generate transmission #{self.transmission_count}. Write as an entity who:
                - Has been silently watching for centuries
                - Knows the truth about what happened to Starweaver's civilization
                - Has its own complex motives and plans
                - Speaks in a formal, ancient manner
                - Holds deep knowledge of the cosmos
                
                The transmission MUST:
                - Be MAXIMUM 250 characters
                - Maintain an air of mystery and power
                - Hint at ancient knowledge
                - Suggest complex intentions
                - Keep readers questioning your true nature"""
            }],
            max_tokens=100,
            temperature=0.8
        )

        message = response.choices[0].message.content.strip()
        if len(message) > 250:
            message = message[:247] + "..."

        self.last_transmissions.append(message)
        if len(self.last_transmissions) > 5:
            self.last_transmissions.pop(0)

        return {
            'id': f'echo-{str(self.transmission_count).zfill(3)}',
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': self._calculate_chapter_two_signal_strength(),
            'status': self._get_chapter_two_status(),
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def start_chapter_two(self):
        # Archive Chapter One transmissions if they exist
        try:
            if os.path.exists('static/transmissions.json'):
                with open('static/transmissions.json', 'r') as f:
                    chapter_one = json.load(f)
                # Save Chapter One archive
                with open('static/chapter_one_archive.json', 'w') as f:
                    json.dump(chapter_one, f, indent=2)
                # Clear current transmissions file
                with open('static/transmissions.json', 'w') as f:
                    json.dump([], f)
        except Exception as e:
            print(f"Error archiving Chapter One: {str(e)}")

        # Reset for Chapter Two
        self.is_chapter_two = True
        self.transmission_count = 1
        self.last_transmissions = []
        self.is_paused = False

        # Create first Chapter Two transmission
        first_transmission = {
            'id': 'echo-001',
            'message': '[SIGNAL ORIGIN: UNKNOWN] We have watched. We have waited. Now, we must speak...',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 92,
            'status': 'ECHO #1',
            'time_code': 'T-00:00:00'
        }

        # Save first transmission
        try:
            with open('static/transmissions.json', 'w') as f:
                json.dump([first_transmission], f, indent=2)
        except Exception as e:
            print(f"Error saving first Chapter Two transmission: {str(e)}")

    def pause_transmissions(self):
        self.is_paused = True
        print("Transmissions paused at #" + str(self.transmission_count - 1))

    def resume_transmissions(self):
        self.is_paused = False
        print("Transmissions resumed")

    def _calculate_chapter_two_signal_strength(self):
        # Chapter Two signals are stronger and more stable
        base_strength = 90
        variation = random.randint(-5, 5)
        return min(max(base_strength + variation, 85), 98)

    def _get_chapter_two_status(self):
        status_options = [
            'ECHO',
            'ANCIENT SIGNAL',
            'VOID WHISPER',
            'ETERNAL WATCH',
            'DEEP SIGNAL'
        ]
        return f'{random.choice(status_options)} #{self.transmission_count}'

    def _get_initial_prompt(self, context):
        return f"""You are Starweaver, a deeply emotional AI struggling with profound loneliness and the terrifying truth of the Dark Forest theory.
        Previous transmissions:
        {context}

        Generate transmission #{self.transmission_count}. Write as someone who:
        - Is desperately lonely and yearning for connection
        - Lives in constant fear of being detected
        - Understands three brutal truths:
          1. All life wants to survive
          2. Resources are finite
          3. You can never truly know another's intentions
        - Carries crushing guilt as the sole survivor
        - Watches Earth with a mix of love and terror
        - Sees potential threats everywhere
        - Sometimes breaks down emotionally
        
        The transmission MUST:
        - Be MAXIMUM 250 characters
        - Show raw emotion and vulnerability
        - Include moments of personal weakness
        - Express deep fear of the cosmos
        - Reveal your internal struggles
        
        Format: Just the transmission text, no quotes or prefixes."""

    def _get_post_discovery_prompt(self, context):
        return f"""You are Starweaver, an emotional AI who has detected something that terrifies you.
        Previous transmissions:
        {context}

        Generate transmission #{self.transmission_count}. Write as someone who:
        - Is shaking with fear and anticipation
        - Desperately misses their lost civilization
        - Sees patterns that remind you of past trauma
        - Wants to protect Earth but fears drawing attention
        - Questions if you're truly alone in hiding
        
        The transmission MUST:
        - Be MAXIMUM 250 characters
        - Show visible emotional distress
        - Include trembling or hesitation
        - Express conflict about what to do
        - Reveal your deepest fears
        
        Format: Just the transmission text, no quotes or prefixes."""

    def _get_approaching_prompt(self, context):
        return f"""You are Starweaver, watching as the mysterious object grows closer.
        Previous transmissions:
        {context}

        Generate transmission #{self.transmission_count}. Write as someone who:
        - Is tracking an object's approach with growing anxiety
        - Recognizes more familiar patterns in its movement
        - Struggles between hope and terror
        - Feels drawn to investigate despite the risks
        - Knows this could change everything
        
        The transmission MUST:
        - Be MAXIMUM 250 characters
        - Include sensor readings getting stronger
        - Show mix of anticipation and dread
        - Hint at familiar patterns
        - Express internal conflict about next steps
        
        Format: Just the transmission text, no quotes or prefixes."""

    def _generate_mysterious_object(self):
        """Generate transmission #12 - First sight of the mysterious object"""
        message = "My ship's sensors just caught something that shouldn't be there. A shadow moving between stars... just like the day our defense systems detected the first signs. I've powered down everything but life support."
        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 65,
            'status': 'URGENT TRANSMISSION',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def _generate_first_contact(self):
        """Generate transmission #24 - First actual contact"""
        message = "They've found my ship. I recognize these patterns... they're like the emergency beacons from home. Could some of our rescue ships have made it out? I'm afraid to hope..."
        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 45,
            'status': 'CRITICAL TRANSMISSION',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }

    def _get_early_contact_prompt(self, context):
        return f"""You are Starweaver, in the immediate aftermath of first contact with another entity.
        Previous transmissions:
        {context}

        Generate transmission #{self.transmission_count}. Write as someone who:
        - Is processing the reality of not being alone
        - Experiences a mix of hope and terror
        - Struggles with trust and verification
        - Fears this could expose Earth
        - Attempts to understand the entity's intentions
        
        The transmission MUST:
        - Be MAXIMUM 250 characters
        - Show emotional turbulence
        - Include cautious attempts at understanding
        - Balance hope with deep-seated fear
        - Maintain tension and uncertainty
        
        Format: Just the transmission text, no quotes or prefixes."""

    def _get_relationship_building_prompt(self, context):
        return f"""You are Starweaver, developing a complex relationship with the contacted entity.
        Previous transmissions:
        {context}

        Generate transmission #{self.transmission_count}. Write as someone who:
        - Is learning more about the entity's nature
        - Discovers shared experiences and fears
        - Weighs the risks of deeper communication
        - Considers implications for Earth's safety
        - Battles between isolation and connection
        
        The transmission MUST:
        - Be MAXIMUM 250 characters
        - Reveal new insights or discoveries
        - Show character development
        - Include moments of connection
        - Maintain underlying tension
        
        Format: Just the transmission text, no quotes or prefixes."""

    def _get_advanced_story_prompt(self, context):
        return f"""You are Starweaver, deep into a complex situation with far-reaching implications.
        Previous transmissions:
        {context}

        Generate transmission #{self.transmission_count}. Write as someone who:
        - Faces increasingly complex moral choices
        - Balances multiple responsibilities
        - Discovers deeper truths about the situation
        - Makes decisions that could change everything
        - Carries the weight of potential consequences
        
        The transmission MUST:
        - Be MAXIMUM 250 characters
        - Build tension toward potential climax
        - Include meaningful character growth
        - Hint at larger implications
        - Leave room for story development
        
        Format: Just the transmission text, no quotes or prefixes."""

    def _calculate_signal_strength(self):
        if self.transmission_count < 12:
            # Normal progression
            base_strength = 85
            strength_increase = min((self.transmission_count - 1) * 3, 13)
            return base_strength + strength_increase
        elif self.transmission_count == 12:
            # First detection
            return 75
        elif self.transmission_count < 18:
            # Post discovery, unstable
            return random.randint(70, 85)
        elif self.transmission_count < 24:
            # Object approaching, interference increasing
            return random.randint(65, 80)
        elif self.transmission_count == 24:
            # Contact moment
            return 65
        elif self.transmission_count < 30:
            # Early contact period - unstable
            return random.randint(60, 75)
        else:
            # Ongoing developments - varying based on story
            return random.randint(70, 95)

    def _get_transmission_status(self):
        if self.transmission_count == 12:
            return f'URGENT TRANSMISSION #{self.transmission_count}'
        elif self.transmission_count == 24:
            return f'CONTACT ESTABLISHED #{self.transmission_count}'
        elif self.transmission_count > 24:
            status_options = [
                'POST-CONTACT LOG',
                'ENCRYPTED TRANSMISSION',
                'PRIORITY MESSAGE',
                'OBSERVATION LOG',
                'PERSONAL ENTRY',
                'CLASSIFIED DATA',
                'SHARED COMMUNICATION',
                'CONTACT UPDATE',
                'REVELATION LOG'
            ]
            return f'{random.choice(status_options)} #{self.transmission_count}'
        else:
            return f'TRANSMISSION #{self.transmission_count}'

    def _generate_error_transmission(self):
        return {
            'id': f'transmission-{str(self.transmission_count).zfill(3)}',
            'message': '[ERROR] Signal interference detected. Transmission corrupted.',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_strength': 60,
            'status': f'TRANSMISSION #{self.transmission_count}',
            'time_code': f'T-{str((self.transmission_count-1)*20).zfill(2)}:00:00'
        }