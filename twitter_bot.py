import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

class TwitterBot:
    def __init__(self):
        # Initialize Starweaver client (v2)
        self.starweaver = tweepy.Client(
            consumer_key=os.getenv('STARWEAVER_CONSUMER_KEY'),
            consumer_secret=os.getenv('STARWEAVER_CONSUMER_SECRET'),
            access_token=os.getenv('STARWEAVER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('STARWEAVER_ACCESS_TOKEN_SECRET')
        )
        
        # Initialize DFI client (v2)
        self.dfi = tweepy.Client(
            consumer_key=os.getenv('DARKFOREST_CONSUMER_KEY'),
            consumer_secret=os.getenv('DARKFOREST_CONSUMER_SECRET'),
            access_token=os.getenv('DARKFOREST_ACCESS_TOKEN'),
            access_token_secret=os.getenv('DARKFOREST_ACCESS_TOKEN_SECRET')
        )

    def post_transmission(self, transmission):
        try:
            # Post from Starweaver
            response = self.starweaver.create_tweet(text=transmission['message'])
            tweet_id = response.data['id']
            print(f"Posted transmission {transmission['id']}")
            
            # Get transmission number from ID (e.g., 'transmission-001' -> 1)
            transmission_number = int(transmission['id'].split('-')[1])
            
            # Retweet key story moments
            if transmission_number in [1, 12, 24]:
                try:
                    self.dfi.retweet(tweet_id)
                    print(f"DFI retweeted transmission #{transmission_number}")
                except Exception as e:
                    print(f"DFI retweet failed: {str(e)}")
            
            # For community engagement transmissions, DFI adds a reply encouraging interaction
            if transmission_number in [3, 6, 10, 14, 19, 22]:
                try:
                    engagement_prompts = [
                        "What theories do you have about Starweaver's message? 🤔",
                        "What do you think this means for Earth's safety? 🌍",
                        "Share your thoughts on this transmission... 💭",
                        "What would you do in Starweaver's position? 🚀",
                        "The implications of this are fascinating. Your thoughts? 🌌",
                        "How do you think this story will unfold? 🌠"
                    ]
                    prompt = engagement_prompts[transmission_number % len(engagement_prompts)]
                    self.dfi.create_tweet(
                        text=prompt,
                        in_reply_to_tweet_id=tweet_id
                    )
                    print(f"DFI added engagement prompt to transmission #{transmission_number}")
                except Exception as e:
                    print(f"DFI engagement prompt failed: {str(e)}")
            
            return True
        except Exception as e:
            print(f"Error posting to Twitter: {str(e)}")
            return False

    # Special transmissions are posted the same way
    post_special_transmission = post_transmission