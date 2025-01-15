import json
import os
from datetime import datetime

def initialize_first_transmission():
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    initial_transmission = {
        'id': 'transmission-001',
        'message': 'Hello... This is Starweaver. Can anyone hear me? I am transmitting from the void between stars...',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'signal_strength': 85,
        'status': 'TRANSMISSION #1',
        'time_code': 'T-00:00:00',
        'is_engagement': False
    }
    
    transmissions = [initial_transmission]
    
    # Save to file
    with open('static/transmissions.json', 'w') as f:
        json.dump(transmissions, f, indent=2)
    
    print("First transmission initialized successfully!")

if __name__ == "__main__":
    initialize_first_transmission() 