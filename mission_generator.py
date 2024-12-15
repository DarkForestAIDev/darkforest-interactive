[33mcommit 2dfa691febd0ed420e51352a5b41e981ecdcaa75[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m)[m
Author: DarkForestAIDev <deepforestinteractive@gmail.com>
Date:   Sun Dec 15 03:16:22 2024 -0800

    Update OpenAI client initialization for version 1.6.1

[1mdiff --git a/transmission_generator.py b/transmission_generator.py[m
[1mindex 5fb2504..26eb549 100644[m
[1m--- a/transmission_generator.py[m
[1m+++ b/transmission_generator.py[m
[36m@@ -1,13 +1,16 @@[m
 from datetime import datetime, timedelta[m
 import random[m
 import json[m
[31m-import openai[m
[32m+[m[32mfrom openai import OpenAI[m
 import os[m
 from dotenv import load_dotenv[m
 [m
 # Load environment variables[m
 load_dotenv()[m
[31m-client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))[m
[32m+[m[32mclient = OpenAI([m
[32m+[m[32m    api_key=os.getenv('OPENAI_API_KEY'),[m
[32m+[m[32m    default_headers={"User-Agent": "Starweaver"}[m
[32m+[m[32m)[m
 [m
 class TransmissionGenerator:[m
     def __init__(self):[m
[36m@@ -107,13 +110,28 @@[m [mclass TransmissionGenerator:[m
             You are Starweaver, a female AI hiding in your cloaked ship.[m
             Your current state: {trait}, {emotion}[m
             Current operation: {operation}[m
[32m+[m[32m            Transmission number: {self.transmission_count}[m
             [m
[31m-            Write something that subtly:[m
[32m+[m[32m            Write something that:[m
[32m+[m[32m            - References your previous observations or decisions[m
[32m+[m[32m            - Hints at choices or dilemmas you're facing[m
[32m+[m[32m            - Shows your growing concern for Earth's safety[m
[32m+[m[32m            - Suggests you might need guidance or input[m
[32m+[m[32m            - Makes humans feel involved in your mission[m
             - Raises questions about your mission or observations[m
             - Hints at deeper mysteries or concerns[m
             - Makes humans think about their place in the cosmos[m
[31m-            - Is under 275 characters[m
             - Naturally incorporates your state and operation[m
[32m+[m[32m            - Is under 275 characters[m
[32m+[m[32m            - Remains subtle and poetic in tone[m
[32m+[m[41m            [m
[32m+[m[32m            Example themes based on transmission number:[m
[32m+[m[32m            #3: Initial trust and revealing more about your mission[m
[32m+[m[32m            #6: Sharing concerning observations about Earth's signals[m
[32m+[m[32m            #10: Debating how much to reveal about cosmic threats[m
[32m+[m[32m            #14: Seeking input about the mysterious object[m
[32m+[m[32m            #19: Weighing options about increasing cosmic activity[m
[32m+[m[32m            #22: Contemplating contact with the ancient entity[m
             """[m
         else:[m
             prompt = f"""[m
