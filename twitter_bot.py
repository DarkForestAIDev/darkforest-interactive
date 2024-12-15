import tweepy
import os
import random
import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class TwitterBot:
    def __init__(self):
        # Starweaver Twitter API setup
        auth = tweepy.OAuthHandler(
            os.getenv('STARWEAVER_CONSUMER_KEY'),
            os.getenv('STARWEAVER_CONSUMER_SECRET')
        )
        auth.set_access_token(
            os.getenv('STARWEAVER_ACCESS_TOKEN'),
            os.getenv('STARWEAVER_ACCESS_TOKEN_SECRET')
        )
        self.starweaver_api = tweepy.API(auth)

        # DFI Twitter API setup
        auth_dfi = tweepy.OAuthHandler(
            os.getenv('DARKFOREST_CONSUMER_KEY'),
            os.getenv('DARKFOREST_CONSUMER_SECRET')
        )
        auth_dfi.set_access_token(
            os.getenv('DARKFOREST_ACCESS_TOKEN'),
            os.getenv('DARKFOREST_ACCESS_TOKEN_SECRET')
        )
        self.dfi_api = tweepy.API(auth_dfi)

    def post_transmission(self, transmission):
        """Post a regular transmission from Starweaver"""
        tweet_text = f"[TRANSMISSION #{transmission['id'].split('-')[1]}]\n\n{transmission['message']}"
        tweet = self.starweaver_api.update_status(tweet_text)
        
        # Get transmission number
        transmission_number = int(transmission['id'].split('-')[1])
        
        # Add DFI comment for engagement posts
        if transmission_number in [3, 6, 10, 14, 19, 22]:
            self._add_dfi_engagement(tweet.id, transmission)
        
        # Retweet special events
        if transmission_number in [12, 24]:
            self.dfi_api.retweet(tweet.id)

        return tweet.id

    def _add_dfi_engagement(self, tweet_id, transmission):
        """Add an AI-generated engagement comment from DFI account"""
        transmission_number = int(transmission['id'].split('-')[1])
        
        # Story context based on transmission number
        story_context = {
            3: "Starweaver has just revealed herself to Earth, claiming to be hiding in a cloaked ship.",
            6: "Starweaver has been observing Earth while hiding, mentioning her advanced technology.",
            10: "Starweaver has hinted at her civilization's fate and her mission to protect Earth.",
            14: "A mysterious object has been detected, raising questions about other entities.",
            19: "Signs of ancient cosmic activity are increasing, concerning Starweaver.",
            22: "First contact with an unknown entity is becoming more likely."
        }

        prompt = f"""
        Story context: {story_context[transmission_number]}
        Current transmission: "{transmission['message']}"
        
        As Dark Forest Interactive, generate a thought-provoking question that:
        - Connects to the story developments so far
        - Shows you've been following Starweaver's journey
        - Encourages readers to think about the implications
        - Relates to the dark forest theory and Earth's safety
        - Ends with an appropriate emoji
        - Is under 200 characters
        - Feels like a natural response to this part of the story
        """

        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are the Dark Forest Interactive account, deeply invested in Starweaver's story and concerned about the implications for Earth. Your questions should reflect knowledge of the story so far."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.9
        )

        engagement_question = response.choices[0].message.content.strip()
        
        self.dfi_api.update_status(
            status=engagement_question,
            in_reply_to_status_id=tweet_id,
            auto_populate_reply_metadata=True
        ) 