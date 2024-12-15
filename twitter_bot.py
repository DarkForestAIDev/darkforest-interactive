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
        
        # If it's an engagement transmission, add DFI comment
        transmission_number = int(transmission['id'].split('-')[1])
        if transmission_number in [3, 6, 10, 14, 19, 22]:
            self._add_dfi_engagement(tweet.id, transmission)
        
        # If it's a special event (12 or 24), retweet from DFI
        if transmission_number in [12, 24]:
            self.dfi_api.retweet(tweet.id)

        return tweet.id

    def _add_dfi_engagement(self, tweet_id, transmission):
        """Add an AI-generated engagement comment from DFI account"""
        prompt = f"""
        Based on Starweaver's transmission: "{transmission['message']}"
        
        Generate a single engaging question that:
        - Encourages discussion about the story implications
        - Feels natural and conversational
        - Ends with an emoji
        - Is under 200 characters
        - Doesn't reveal it's AI-generated
        - Relates directly to what Starweaver just said
        - Encourages theories and speculation
        """

        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are the Dark Forest Interactive account, engaging with the community about Starweaver's story."},
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