"""
Utility helpers for Sizu.
"""
import random
import re
import time
from datetime import datetime, timezone
from typing import Optional


# ── Human-like typing delay ───────────────────────────────────────────────────

async def get_human_delay(text: str) -> float:
    """
    Simulate realistic typing delay based on response length.
    Shorter texts feel snappier, longer ones have a small natural lag.
    """
    base = len(text) * 0.03          # 30ms per character base
    variance = random.uniform(0.2, 0.9)
    return min(max(base + variance, 1.0), 4.5)


# ── Elapsed time ──────────────────────────────────────────────────────────────

def time_ago(timestamp: float) -> str:
    """Human-readable time ago string."""
    diff = time.time() - timestamp
    if diff < 60:
        return f"{int(diff)}s ago"
    elif diff < 3600:
        return f"{int(diff / 60)}m ago"
    elif diff < 86400:
        return f"{int(diff / 3600)}h ago"
    else:
        return f"{int(diff / 86400)}d ago"


def parse_time(text: str) -> Optional[int]:
    """
    Parse human time strings into seconds.
    Supports: 30s, 5m, 2h, 1d
    """
    text = text.strip().lower()
    match = re.fullmatch(r"(\d+)\s*([smhd]?)", text)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2) or "m"
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return value * multipliers.get(unit, 60)


# ── Name utilities ────────────────────────────────────────────────────────────

def mention(user_id: int, name: str) -> str:
    """Create a Telegram mention string."""
    return f"[{name}](tg://user?id={user_id})"


def get_name(user) -> str:
    """Get the best display name from a Pyrogram User object."""
    if not user:
        return "Someone"
    full = (user.first_name or "").strip()
    if user.last_name:
        full += f" {user.last_name.strip()}"
    return full or user.username or "Someone"


# ── Menu formatting ───────────────────────────────────────────────────────────

def box(title: str, content: str, width: int = 30) -> str:
    """Draw a pretty box around menu content."""
    line = "─" * width
    return f"╭{line}╮\n│  **{title}**\n├{line}┤\n{content}\n╰{line}╯"


# ── Escape ────────────────────────────────────────────────────────────────────

def escape_md(text: str) -> str:
    """Escape MarkdownV2 special characters."""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT POOLS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Truth & Dare ──────────────────────────────────────────────────────────────

TRUTHS = [
    'What is your biggest fear about the future? 🥺',
    "Have you ever broken someone's heart? What happened? 💔",
    "What is a secret you've never told anyone in your life?",
    'If you could change one decision from your past, what would it be?',
    'What is the most painful lesson you have learned in life?',
    'Who is the one person you wish you could apologize to right now?',
    'What does love mean to you in one sentence? ❤️',
    'Have you ever felt completely lonely even in a crowd?',
    "What is the biggest sacrifice you've made for someone else?",
    'If you died today, what would be your biggest regret?',
    'Do you believe people can actually change, or do they just hide who they are?',
    'What is the most vulnerable moment of your life so far?',
    'Have you ever lied to protect your self-respect?',
    'What is something you are holding onto that you need to let go of?',
    "If money didn't matter, what would you do with your life?",
    'What memory always makes you cry no matter how much time passes? 😭',
    'Who in your life do you feel most misunderstood by?',
    'When was the last time you felt truly appreciated and loved?',
    'What is a dream you had to give up on? 🌟',
    "Has anyone ever made you feel like you weren't good enough?",
    'What makes you feel most insecure about your personality?',
    'What is the nicest thing anyone has ever done for you?',
    'Do you think you are easy or difficult to love?',
    'What is a compliment you received that you will never forget?',
    'If you could have one conversation with someone who is no longer in your life, who would it be?',
    "What is the hardest truth you've had to accept about yourself?",
    'When was the last time you cried yourself to sleep?',
    'What do you look for in a true friend?',
    "If you could see a map of everyone you've ever loved, who would be the brightest spot?",
    'What is the ultimate definition of happiness for you?',
    'Have you ever pretended to be fine when you were falling apart inside?',
    "What's the loneliest you've ever felt?",
    "Is there something you've forgiven but never forgotten?",
    "What's the one thing you wish someone had told you years ago?",
    'Do you trust people easily, or do they have to earn it?',
    "What is the weirdest thing you've done when you were alone in a room? 😂",
    'Have you ever practiced an argument in front of the mirror?',
    "What is the most useless thing you've ever spent money on?",
    'Have you ever peed in a swimming pool? 🏊\u200d♂️',
    "What is the dumbest way you've ever gotten injured?",
    'If you could be any animal for a day, which one would it be and why?',
    'What is the most embarrassing nickname you had as a kid? 😭',
    'Have you ever eaten something off the floor after the 5-second rule expired?',
    'What is your most cringe-worthy habit?',
    "Have you ever fake-laughed at a joke you didn't understand?",
    "What is the worst haircut you've ever had?",
    'If you were a ghost, who would you haunt first just to annoy them? 👻',
    'Have you ever walked into a glass door or wall?',
    'What is the most ridiculous lie you told to get out of a chore?',
    "What's your secret guilty pleasure song that you sing in the shower?",
    'Have you ever sent a text to the wrong person? What happened?',
    "What's the most embarrassing thing saved on your phone right now?",
    "Have you ever stalked someone's social media so deep you accidentally liked an old post?",
    "What's the weirdest food combination you secretly enjoy?",
    'Have you ever blamed a fart on someone else?',
    'Who in this group would you trust with a huge secret?',
    'If you had to pick one person here to be stuck on an island with, who?',
    "What's the most annoying habit of your best friend that you tolerate?",
    "Have you ever had a crush on a friend's sibling?",
    "What's the most romantic thing you've ever done for someone?",
    'Have you ever ghosted someone? Why?',
    "What's the biggest red flag you've ignored in a relationship?",
    "Would you read your partner's messages if you had the chance?",
    "Have you ever been jealous of a friend's success?",
    "What's one thing your friends don't know about you?",
    'What is the funniest thing that has ever happened to you in this chat?',
    'If you had to delete one person from this group (besides me), who would it be?',
    'Who do you think has the best sense of humor in this group?',
    'What was your first impression of the person who dared you?',
    'If you could trade lives with anyone in this group for a day, who would it be?',
]

DARES = [
    'Send a voice note laughing uncontrollably for 15 seconds. 😂',
    'Send the weirdest selfie you can take right now, no filters.',
    'Type your next three messages using only your non-dominant hand.',
    "Draft a message saying 'I believe in aliens 👽' and send it to the 3rd person in your DM list, then screenshot their reply.",
    'Send a voice note mimicking a chicken laying an egg. 🐔',
    "Change your Telegram bio to 'Staring at a blank wall is my hobby' for the next 15 minutes.",
    "Text a random contact: 'I know your secret...' and screenshot the reaction.",
    "For the next 10 minutes, you must start every message in this chat with 'Beep boop 🤖'.",
    'Send a voice note of you reciting a tongue twister as fast as you can.',
    'Draw a quick caricature of someone in this group on a piece of paper and post it.',
    'Post a voice note of you trying to beatbox for 10 seconds. 🎤',
    "Record yourself saying 'I am the queen/king of comedy' in a dramatic voice note.",
    'Send the 5th photo in your gallery with no context. 🖼️',
    "Change your Telegram name to 'Pineapple Pizza Lover' for 1 hour.",
    "Draft a text saying 'I just ate raw onions and they were delicious' and send it to your best friend.",
    'Do your best impression of a news anchor and send a voice note.',
    'Send a screenshot of your last 3 Google searches. No deleting!',
    'Write a haiku about your laziest quality and share it.',
    'Talk like a robot for the next 5 messages in this chat.',
    'Send a selfie making the ugliest face you can.',
    "Text your crush/partner: 'I have a confession...' and wait 2 minutes before telling them it was a dare. Screenshot the reaction! 😏",
    'Explain your ideal date using only emojis. 💘',
    'Write a short, highly dramatic love poem about the person above you in this chat.',
    'Send a voice note describing your very first crush in detail.',
    'Confess what you find most attractive about the person you are replying to.',
    "What's the best relationship advice you've ever received? Send it as a voice note.",
    "Send a text to your partner or crush saying 'You look extra cute today' and show the reply.",
    'Describe your worst date experience in 3 sentences.',
    'If you had to go on a date with anyone in this group, who would it be and why?',
    'Send a heart emoji to the first person on your chat list.',
    'Write a breakup text for a relationship that never existed.',
    'Rank the top 3 qualities you need in a partner. No cop-outs.',
    'Post a screenshot of your search history from today. No editing! 💀',
    'Record a 10-second voice note of you singing a pop song off-key.',
    'Send a photo of the messiest room or spot in your house right now.',
    'Show a screenshot of your screen time stats for this week. 📱',
    'Type a message to the group explaining why you still sleep with a stuffed animal/light on.',
    'Record a voice note explaining your most embarrassing school memory in a dramatic voice.',
    "Text a coworker or classmate: 'I accidentally drank your coffee' and show the reply.",
    'Send a voice note of you making loud yawning noises.',
    'Reveal the last thing you searched on YouTube.',
    'Confess the dumbest thing you did to impress someone you liked.',
    'Share the worst photo of yourself from your gallery.',
    'Tell us about the time you embarrassed yourself in public.',
    'Give a genuine, heartfelt compliment to the person who dared you. 🌸',
    'Mention three things you appreciate about this group.',
    'Tag someone in this group and tell them why they are the funniest person here.',
    "Write a 4-line rhyme praising Sizu's intelligence. 💅",
    'Ask the group to vote on your best quality, and accept the result.',
    'Agree with everything said in this chat for the next 5 minutes.',
    'Send a voice note thanking everyone in this chat for being awesome.',
    "Tag your closest friend in this group and say 'You're stuck with me forever'.",
    'Describe the vibe of this group in 3 emojis.',
    'Declare yourself as the official assistant of Sizu in this chat.',
    'Give everyone in the group a one-word nickname. Right now.',
    'Tell us the funniest inside joke from this group.',
    'Send a voice note singing your favorite childhood rhyme. 🎶',
    "Message a random group member saying 'You owe me 500 rupees' and show their response.",
    "Change your profile name to 'I am a potato 🥔' for the next 10 minutes.",
    'For the next 5 minutes, you can only reply with emojis.',
    'Type your next message using only your nose. 👃',
    'Post the most recent screenshot in your gallery.',
    'Send a voice note of you whispering a secret (fake or real).',
    'Tag a random person in this chat and tell them they have cool hair.',
    'Describe your current outfit in extremely dramatic, fashion-runway terms.',
]


# ── Puzzles Database ──────────────────────────────────────────────────────────

PUZZLES_QS = [
    {'q': "What's the smallest country in the world?", 'a': ['vatican city', 'vatican', 'वेटिकन सिटी', 'वेटिकन'], 'hint': "It's inside Rome"},
    {'q': 'How many bones does an adult human body have?', 'a': ['206', 'two hundred and six', 'दो सौ छह'], 'hint': 'More than 200'},
    {'q': 'Which planet has the most moons?', 'a': ['saturn', 'शनि'], 'hint': 'Known for its rings'},
    {'q': 'What year did the Titanic sink?', 'a': ['1912', '१९१२'], 'hint': 'Early 20th century'},
    {'q': 'How many sides does a dodecagon have?', 'a': ['12', 'twelve', 'बारह'], 'hint': 'More than 10'},
    {'q': "What's the fastest land animal?", 'a': ['cheetah', 'चीता'], 'hint': 'A big spotted cat'},
    {'q': 'Who painted the Mona Lisa?', 'a': ['leonardo da vinci', 'da vinci', 'लियोनार्डो दा विंची', 'दा विंची'], 'hint': 'Italian Renaissance master'},
    {'q': 'What element is represented by the symbol Au?', 'a': ['gold', 'सोना', 'gold element'], 'hint': 'A precious yellow metal'},
    {'q': 'How many continents are there on Earth?', 'a': ['7', 'seven', 'सात'], 'hint': 'Less than 10'},
    {'q': "What's the longest river in the world?", 'a': ['nile', 'नाइल', 'नील नदी', 'नील'], 'hint': 'Flows through Egypt'},
    {'q': 'In what year did World War 2 end?', 'a': ['1945', '१९४५'], 'hint': 'Mid 1940s'},
    {'q': 'What is the hardest natural substance on Earth?', 'a': ['diamond', 'हीरा'], 'hint': 'Used in jewelry and cutting tools'},
    {'q': 'How many strings does a standard guitar have?', 'a': ['6', 'six', 'छह'], 'hint': 'Less than 10'},
    {'q': "What's the capital of Japan?", 'a': ['tokyo', 'टोक्यो'], 'hint': 'Hosted the Olympics'},
    {'q': 'Which gas do plants absorb from the atmosphere for photosynthesis?', 'a': ['carbon dioxide', 'co2', 'कार्बन डाइऑक्साइड'], 'hint': 'We exhale it'},
    {'q': 'What is the capital of France?', 'a': ['paris', 'पेरिस'], 'hint': 'City of Love'},
    {'q': 'Who is known as the father of computer science?', 'a': ['alan turing', 'turing', 'एलन ट्यूरिंग'], 'hint': 'He cracked the Enigma code'},
    {'q': 'Which country is home to the Kangaroo?', 'a': ['australia', 'ऑस्ट्रेलिया'], 'hint': 'Down Under'},
    {'q': 'How many colors are there in a rainbow?', 'a': ['7', 'seven', 'सात'], 'hint': 'VIBGYOR'},
    {'q': 'What is the primary source of energy for the Earth?', 'a': ['sun', 'सूर्य', 'सूरज'], 'hint': 'A star'},
    {'q': 'I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?', 'a': ['echo', 'गूंज', 'प्रतिध्वनि'], 'hint': 'You hear it in mountains'},
    {'q': 'The more you take, the more you leave behind. What am I?', 'a': ['footsteps', 'कदम', 'पैर के निशान'], 'hint': 'Look at the ground behind you'},
    {'q': 'I have cities but no houses, forests but no trees, and water but no fish. What am I?', 'a': ['map', 'नक्शा', 'a map'], 'hint': 'Found on paper or screens'},
    {'q': "What has keys but can't open locks?", 'a': ['piano', 'keyboard', 'पियानो', 'कीबोर्ड'], 'hint': 'A musical instrument'},
    {'q': 'What can travel around the world while staying in a corner?', 'a': ['stamp', 'डाक टिकट', 'a stamp', 'postage stamp'], 'hint': 'Found on letters'},
    {'q': "I'm tall when I'm young and short when I'm old. What am I?", 'a': ['candle', 'मोमबत्ती'], 'hint': 'Made of wax'},
    {'q': 'What has a head and a tail but no body?', 'a': ['coin', 'सिक्का', 'a coin'], 'hint': 'You flip it'},
    {'q': 'What gets wetter the more it dries?', 'a': ['towel', 'तौलिया', 'a towel'], 'hint': 'Found in bathrooms'},
    {'q': "What has hands but can't clap?", 'a': ['clock', 'घड़ी', 'a clock', 'watch'], 'hint': 'Tells you the time'},
    {'q': 'What breaks but never falls, and what falls but never breaks?', 'a': ['day and night', 'dawn and dusk', 'din aur raat'], 'hint': 'Think about the sun cycle'},
    {'q': 'What is the chemical formula for water?', 'a': ['h2o', 'H2O'], 'hint': 'Two elements combined'},
    {'q': 'How many teeth does an adult human have?', 'a': ['32', 'thirty two', 'बत्तीस'], 'hint': 'More than 30'},
    {'q': 'What planet is known as the Red Planet?', 'a': ['mars', 'मंगल'], 'hint': 'Named after a Roman god of war'},
    {'q': 'What is the speed of light approximately in km/s?', 'a': ['300000', '3 lakh', 'three hundred thousand', '3,00,000'], 'hint': '3 followed by five zeros'},
    {'q': 'What is the largest organ in the human body?', 'a': ['skin', 'त्वचा'], 'hint': 'It covers your entire body'},
    {'q': 'How many chromosomes do humans have?', 'a': ['46', 'forty six', 'छियालीस'], 'hint': '23 pairs'},
    {'q': "What gas makes up about 78% of Earth's atmosphere?", 'a': ['nitrogen', 'नाइट्रोजन'], 'hint': 'Not oxygen'},
    {'q': 'What is the square root of 144?', 'a': ['12', 'twelve', 'बारह'], 'hint': '12 × 12'},
    {'q': 'What is the boiling point of water in Celsius?', 'a': ['100', 'hundred', 'सौ'], 'hint': 'A round number'},
    {'q': 'Who developed the theory of relativity?', 'a': ['einstein', 'albert einstein', 'आइंस्टीन'], 'hint': 'E = mc²'},
    {'q': 'Who was the first person to walk on the moon?', 'a': ['neil armstrong', 'armstrong', 'नील आर्मस्ट्रांग'], 'hint': 'One small step for man...'},
    {'q': 'In which year did India gain independence?', 'a': ['1947', '१९४७'], 'hint': 'August 15'},
    {'q': 'What is the national animal of India?', 'a': ['tiger', 'bengal tiger', 'बाघ', 'शेर'], 'hint': 'A big striped cat'},
    {'q': 'Who wrote Romeo and Juliet?', 'a': ['shakespeare', 'william shakespeare', 'शेक्सपियर'], 'hint': 'English playwright'},
    {'q': 'What is the currency of Japan?', 'a': ['yen', 'japanese yen', 'येन'], 'hint': 'Symbol: ¥'},
    {'q': 'Which ocean is the largest?', 'a': ['pacific', 'pacific ocean', 'प्रशांत महासागर'], 'hint': 'Borders Asia and the Americas'},
    {'q': 'What is the tallest mountain in the world?', 'a': ['mount everest', 'everest', 'एवरेस्ट', 'माउंट एवरेस्ट'], 'hint': 'On the Nepal-Tibet border'},
    {'q': 'How many players are there in a cricket team?', 'a': ['11', 'eleven', 'ग्यारह'], 'hint': 'Same as football'},
    {'q': 'Who invented the telephone?', 'a': ['alexander graham bell', 'graham bell', 'bell', 'ग्राहम बेल'], 'hint': 'His last name is a sound'},
    {'q': 'What is the national flower of India?', 'a': ['lotus', 'कमल'], 'hint': 'Grows in water'},
    {'q': 'Who founded Microsoft?', 'a': ['bill gates', 'gates', 'बिल गेट्स'], 'hint': 'One of the richest people ever'},
    {'q': 'What year was the first iPhone released?', 'a': ['2007'], 'hint': 'Late 2000s'},
    {'q': "What programming language is known as the 'language of the web'?", 'a': ['javascript', 'js', 'जावास्क्रिप्ट'], 'hint': 'Not Java'},
    {'q': "What does 'HTML' stand for?", 'a': ['hypertext markup language'], 'hint': 'Used to build web pages'},
    {'q': 'Who is the CEO of Tesla?', 'a': ['elon musk', 'musk', 'एलन मस्क'], 'hint': 'Also owns SpaceX and X'},
    {'q': 'What starts with T, ends with T, and has T in it?', 'a': ['teapot', 'टीपॉट', 'केतली'], 'hint': 'Used for serving hot tea'},
    {'q': "I have keys but no locks. I have space but no room. You can enter but can't go outside. What am I?", 'a': ['keyboard', 'कीबोर्ड'], 'hint': "You're probably typing on it right now"},
    {'q': 'What is full of holes but still holds water?', 'a': ['sponge', 'स्पंज'], 'hint': 'Used in kitchen cleaning or bath'},
    {'q': 'What has a thumb and four fingers, but is not a hand?', 'a': ['glove', 'दस्ताना', 'gloves'], 'hint': 'Worn in winter or for safety'},
    {'q': 'Which is the largest ocean on Earth?', 'a': ['pacific', 'pacific ocean', 'प्रशांत महासागर'], 'hint': 'Same as the one bordering Asia and America'},
    {'q': 'Which planet is known for its beautiful rings?', 'a': ['saturn', 'शनि'], 'hint': 'Sixth planet from the Sun'},
    {'q': 'Which country invented tea?', 'a': ['china', 'चीन'], 'hint': 'An East Asian country with the Great Wall'},
    {'q': 'How many seconds are there in an hour?', 'a': ['3600', 'thirty six hundred', '३६००'], 'hint': '60 times 60'},
    {'q': 'What is the capital city of Australia?', 'a': ['canberra', 'कैनबरा'], 'hint': 'Starts with C, not Sydney or Melbourne'},
    {'q': 'What goes up but never comes down?', 'a': ['age', 'उम्र', 'आयु'], 'hint': 'It increases every year'},
]


# ── Quotes Database (150+) ───────────────────────────────────────────────────

QUOTES = [
    "People don't leave when they stop loving you. They leave when they stop needing you.",
    'The saddest thing about betrayal is that it never comes from strangers.',
    "It hurts to let go, but it hurts more to hold onto something that isn't there.",
    'The hardest part about walking away is not looking back.',
    "Sometimes the person you'd take a bullet for is behind the trigger.",
    "You can't start the next chapter of your life if you keep re-reading the last one.",
    "What breaks you is not the goodbye. It's the flashbacks that follow.",
    "Some people are going to leave, but that's not the end of your story. That's the end of their part in your story.",
    'Dil ka tootna bhi zaroori hota hai, tabhi toh khud se mulaqat hoti hai. 💔',
    'Sabse zyada dard tab hota hai jab apna hi paraya lagne lage.',
    'Waqt badal jata hai, log badal jate hain, bas yaadein wahin reh jati hain.',
    'Rishte kanch ki tarah hote hain, ek baar toot jayein toh jodte waqt chubhte hain.',
    'Kabhi kabhi hum kisi ke liye itne bhi zaroori nahi hote jitna hum soch lete hain. 😭',
    'Toota hua insaan sabse khoobsurat muskurata hai, kyunki woh jaanta hai dard kya hota hai.',
    'Jo log aapke liye roye nahi, unke liye aapka rona bekar hai.',
    'Trust is like an eraser — it gets smaller with every mistake.',
    "The worst thing about being lied to is knowing you weren't worth the truth.",
    'Everyone shows you their real face eventually. You just have to be patient enough to see it.',
    'Bharosa ek baar tootne ke baad jodna, toote sheeshe mein apna chehra dekhne jaisa hai.',
    'Dhoka dene wale ko maaf karna aasan hai, par dobara bharosa karna namumkin.',
    'Jo insaan aapko dhoka de sake, wahi aapko sabak bhi sikha sakta hai.',
    'Vishwas karna galat nahi hai, galat insaan par karna galat hai.',
    'Log woh nahi hote jo kehte hain, log woh hote hain jo karte hain.',
    'Sach sunne ki himmat rakhna, kyunki jhooth sunne ki aadat pad jayegi.',
    'The older you grow, the more you realise silence speaks louder than explanations.',
    "Loneliness is not about being alone. It's about feeling alone in a room full of people.",
    'Sometimes you need to be alone. Not to be lonely, but to enjoy your free time being yourself.',
    'Silence is the most powerful scream.',
    "The loneliest moment in someone's life is when they are watching their whole world fall apart.",
    'Khamoshi mein bahut kuch chhupa hota hai, bas sunne wala chahiye.',
    'Akela hona aur akela mehsoos karna, dono alag baatein hain.',
    'Tanha rehna seekh lo, kyunki sab apne waqt par chhod dete hain.',
    'Kuch log itne akele hote hain ki unhe khud ki awaaz bhi sunai nahi deti.',
    'Chup rehna kamzori nahi, sabr hai. Har koi nahi samajh sakta.',
    'Society teaches people how to earn money, not how to survive loneliness.',
    'The world is not dangerous because of those who do harm, but because of those who look on.',
    "We buy things we don't need, with money we don't have, to impress people we don't like.",
    'People will judge you no matter what you do. So you might as well do what you want.',
    'Monsters are real, and ghosts are real too. They live inside us, and sometimes, they win.',
    'The most common form of despair is not being who you are.',
    'Log chehra dekhkar baat karte hain, kirdar toh bas kitabon mein reh gaya hai. 🤌',
    'Zaroorat padne par sab yaad karte hain, par zaroorat khatam hote hi pehchante nahi.',
    'Logon ki baaton par dhyan mat do, unka toh kaam hi hai bolna.',
    'Duniya mein sabse sasta mashwara hai, aur sabse mehengi madad.',
    'Kalyug ki sabse badi haqeeqat: Yahan log madad karne wale ko hi sabse pehle rote hain.',
    'Har insaan sach sunna chahta hai, jab tak sach uske khilaaf na ho.',
    'Samaj ne sikhaya kamaana, par akele rehna koi nahi sikhata.',
    "People don't change. They reveal who they really are.",
    'Everyone wants to be remembered, but few are willing to be genuine.',
    'The ones who are hardest to love are the ones who need it the most.',
    'We are all strangers to our past selves.',
    'You can be a good person with a kind heart and still say no.',
    'Insaan ki sabse badi kamzori yeh hai ki woh wahi karta hai jo log chahte hain.',
    'Jab tak insaan khud na badle, duniya nahi badlegi.',
    'Jo log doosron ko girate hain, woh khud kabhi uthh nahi paate.',
    'Har chehra ek kahaani chhupaata hai, par sab sunane wale nahi hote.',
    "Your value doesn't decrease based on someone's inability to see your worth.",
    'Never make someone a priority when all you are to them is an option.',
    'If you respect yourself, others will respect you.',
    'Value your peace over proving your point.',
    'Be proud of how you handled these past few months. You survived.',
    'Some of the most beautiful paths cannot be discovered without getting lost.',
    'The master has failed more times than the beginner has even tried.',
    'Your direction is much more important than your speed.',
    'Success is a collection of small steps taken consistently every single day.',
    'Zindagi mein khud ki izzat sabse badi hai, use kabhi kisi ke liye girne mat dena. 👑',
    'Apni khushi ke liye kisi aur par nirbhar mat raho, tum khud mein hi ek poori duniya ho.',
    'Jo shaqs aapki khamoshi ko na samajh sake, woh aapke shabdon ko bhi kabhi nahi samjhega.',
    'Akele chalna seekho yaar, kyunki sath dene wale bhi ek na ek din sath chhod dete hain.',
    'Apne kirdar ko aisa banao ki agar koi aapka sath chhode toh use afsos ho.',
    'Kamyabi tab milti hai jab aapke sapne aapke bahano se bade ho jate hain. ✨',
    'Zindagi mein agar kuch bada karna hai, toh bheed se hatkar chalna seekho.',
    'Mushkilein toh aani hi hain zindagi mein, par ladkar jeetne ka maza hi kuch aur hai.',
    'Thak kar mat baitho mere dost, abhi toh poori udaan baaki hai.',
    "Overthinking is the art of creating problems that weren't even there.",
    "You can't heal in the same environment that made you sick.",
    "Some wounds don't show on the body. They are deeper and more hurtful than anything that bleeds.",
    'The worst battle is between what you know and what you feel.',
    'Pain changes people. Some become rude, some become silent.',
    'Sochna band karo, kyunki jitna sochoge, utna uljhoge.',
    'Dard insaan ko badal deta hai, kuch log sakht ho jaate hain, kuch chup.',
    'Jo dard tumne chhupaaya hai, wahi tumhara sabse bada saathi hai.',
    'Overthinking se zyada koi nahi todta insaan ko.',
    'Khud se ladna sabse mushkil hai, kyunki haarne wala bhi tum ho aur jeetne wala bhi.',
    "In a room full of art, I'd still stare at you.",
    'Pyar woh nahi jo do din ki baatein karein, pyar toh woh hai jo zindagi bhar sath nibhae. ❤️',
    'Love is not about possession, it is about appreciation.',
    'Tum mil gaye toh sab mil gaya, jaise poori kayanaat ek pal mein simat gayi.',
    'To love and be loved is to feel the sun from both sides.',
    'Mohabbat toh bas ek ehsaas hai, jise labzon mein bayaan karna mushkil hai.',
    'You are my favorite notification in the middle of a chaotic day.',
    'Saccha pyar wahi hai jo door rehkar bhi dilon ko kareeb rakhta hai.',
    'Ishq mein shartein nahi hoti, bas ek pyaari si khamoshi hoti hai.',
    'A friend is someone who knows all about you and still loves you.',
    'Dost toh bahut milte hain zindagi mein, par sacche dost kismat se milte hain. 🤝',
    "True friendship is not about being inseparable, it's being separated and nothing changes.",
    'Dosti mein shartein nahi hoti, bas ek doosre ke liye beintehaan bharosa hota hai.',
    "Good friends are like stars. You don't always see them, but they are always there.",
    'Zindagi adhuri hai doston ke bina, unki ek hasi saare gham bhula deti hai.',
    'A single loyal friend is worth more than ten thousand acquaintances.',
    'Dost wahi jo mushkil mein sath de, baaki toh khushiyon mein mehfil sajate hain.',
    "Don't wish it were easier. Wish you were better.",
    'Hard work beats talent when talent fails to work hard.',
    'Society rewards appearance before character. Build character anyway.',
    'The only person you should try to be better than is the person you were yesterday.',
    "Courage isn't having the strength to go on — it is going on when you don't have strength.",
    'Girega toh sambhalega bhi, bas girna band mat karna.',
    'Sapne woh nahi jo neend mein aaye, sapne woh hain jo neend hi na aane dein.',
    'Haar maan lena aasan hai, jeena mushkil hai. Mushkil raasta chuno.',
    'The truth is, everyone is going to hurt you. You just got to find the ones worth suffering for.',
    'It is better to be hated for what you are than to be loved for what you are not.',
    'The only way to deal with an unfree world is to become so absolutely free that your very existence is an act of rebellion.',
    'Never depend on anyone in this world, because even your own shadow leaves you when you are in darkness.',
    'We are all in the gutter, but some of us are looking at the stars.',
    'To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.',
    'The wound is the place where the Light enters you.',
    'Sometimes you have to destroy a part of your life to let the next part grow.',
    "If you tell the truth, you don't have to remember anything.",
    'Pain is inevitable. Suffering is optional.',
    'What is done cannot be undone, but one can prevent it from happening again.',
    'We accept the love we think we deserve.',
    "The worst part of holding the memories is not the pain. It's the loneliness of it.",
    'Sometimes the questions are complicated and the answers are simple.',
    'You cannot find peace by avoiding life.',
    'Zindagi jeene ke do hi tareeqe hain: ek jo ho raha hai use hone do, ya phir zimmedari uthao use badalne ki.',
    'Kuch rishte isliye toot jaate hain kyunki ek likhna nahi chahta aur doosra padhna nahi chahta.',
    'Sabse bada rog, kya kahenge log.',
    'Insaan ki qadar uske chale jaane ke baad hi hoti hai, tab tak toh log sirf galtiyan dhundte hain.',
    'Waqt sabko milta hai zindagi badalne ke liye, par zindagi dobara nahi milti waqt badalne ke liye.',
    'Dheere dheere hi sahi par chalte raho, kyunki thama hua paani bhi badboo dene lagta hai.',
    'Mehnat ka phal aur samasya ka hal, der se hi sahi par milta zaroor hai. ✨',
    'Aadatein badal lo, kismat apne aap badal jayegi.',
    'Zindagi tab behtar hoti hai jab aap khud ko doosron se compare karna band kar dete hain.',
    'Khaali hath aaye the, khaali hath jaoge, bas yaadein hi peeche chhod jaoge.',
    "Silence isn't empty, it's full of answers.",
    'Be kind, for everyone you meet is fighting a harder battle.',
    "No one is busy in this world, it's all about priorities.",
    "Growth is painful. Change is painful. But nothing is as painful as staying stuck somewhere you don't belong.",
    'Accept what is, let go of what was, and have faith in what could be.',
    'A heart that loves is always young.',
    'If you want to live a happy life, tie it to a goal, not to people or things.',
    'Nothing lasts forever, not even your troubles.',
    'Dil bada hona chahiye, baatein toh sab badi badi karte hain.',
    'Mushkil waqt mein hi log aur rishton ki pehchan hoti hai.',
    'Gussa hamesha akela aata hai par jaate jaate saari acchi baatein le jata hai.',
    'Har cheez ka waqt hota hai, aur jab waqt aayega toh sab samajh aa jayega.',
    'Apne kal ko apne aaj par haavi mat hone do.',
    'Sometimes you just have to close your eyes and trust that things will work out.',
    "Real friends don't talk behind your back; they tell you your faults to your face.",
    'Zindagi ek kitab ki tarah hai, har din ek naya panna hai.',
    'Kismat par nahi, apni mehnat par bharosa rakho.',
    'A single lie has the power to destroy a thousand truths.',
    'Forgive others, not because they deserve forgiveness, but because you deserve peace.',
    "The biggest lie we tell ourselves is: 'I'll do it tomorrow.'",
]


# ── Compliments Pool (100+) ──────────────────────────────────────────────────

COMPLIMENTS = [
    'Honestly, people who stay kind after being hurt deserve more credit than they get. Like you.',
    "You're the type of person who notices things others ignore. That's rare.",
    'Your vibe feels like the friend everyone secretly trusts.',
    "There's something about your energy that makes people feel safe. That's a superpower.",
    'You have the kind of personality that makes boring conversations interesting.',
    'The way you handle things would make most people crumble. Respect.',
    "You're proof that being genuine never goes out of style.",
    "If good vibes were a currency, you'd be the richest person in the room.",
    "You make people feel heard without even trying. That's genuinely rare.",
    "You carry a quiet kind of strength that most people don't notice — but the right ones do.",
    "You're the kind of person people write gratitude journal entries about.",
    "Your patience is actually legendary. Most people would've snapped ages ago.",
    'The effort you put into things, even small ones, says a lot about who you are.',
    "You're one of those people who make the world feel a little less cold.",
    'Your ability to stay calm under pressure is lowkey impressive.',
    'Tum jaise log bahut kam hote hain duniya mein — genuine aur real. ✨',
    'Tumhara sabr dekhke lagta hai ki tum andar se bahut strong ho.',
    'Tum log ko accha feel karate ho bina kuch kiye bhi.',
    "Your sense of humor is the kind that actually makes people's day better, not worse.",
    "You're way smarter than you give yourself credit for.",
    'The way you see things differently is what makes you special.',
    'Your mind works in ways that are genuinely fascinating.',
    'You explain things in a way that makes everyone feel included. That takes real intelligence.',
    "You're the type who finds solutions while everyone else is still panicking.",
    'Your wit is the kind people wish they had at 3 AM thinking of comebacks.',
    "Tumhara dimag aur tumhara dil — dono ek saath kaam karte hain. That's rare.",
    "You're the person people think of when they need someone they can count on.",
    'The kindness you show when nobody is watching is what defines you.',
    'You make people smile without even realizing it.',
    'Being around you feels like a warm cup of chai on a cold night. ☕',
    "You don't just listen — you actually hear people. There's a big difference.",
    "Your heart is way too big for this world, and that's your greatest gift.",
    'You remember the little things about people. That means more than you know.',
    'Tum jaise dost milna kismat ki baat hai, sab ko naseeb nahi hota.',
    'Tumhari ek smile se pura room light up ho jata hai. ❤️',
    'Tum apne aap mein ek comfort zone ho doosron ke liye.',
    "The fact that you're still going after everything you've been through? That's real strength.",
    "You handle chaos like it's just another Tuesday. That's admirable.",
    "Most people would've given up by now. You're built different.",
    "Your resilience isn't loud, but it's powerful.",
    "You've survived 100% of your worst days. Remember that.",
    'Tum haar maanoge toh kaun ladega? Keep going. 🔥',
    'Tum itna sab jhel ke bhi muskurate ho — yeh takat hai.',
    'You have the kind of vibe that makes people want to stick around.',
    "There's a warmth about you that's impossible to fake.",
    'Your energy walks into a room before you do.',
    "You've got this effortless cool that most people try too hard for.",
    'You look like the main character of a really good coming-of-age movie.',
    'Your presence makes any place feel a little more alive.',
    'Tumhare baare mein kuch hai jo log bhool nahi paate — in a good way.',
    "You're not perfect and that's what makes you real. Real is always better.",
    'You make imperfection look beautiful.',
    "You treat people the way the world should but doesn't.",
    'You have a maturity about you that has nothing to do with age.',
    "People might not always say it, but you've probably saved someone just by being yourself.",
    "The world needs more people who genuinely mean what they say. You're one of them.",
    "You're the plot twist in someone's story that actually made things better.",
    'If everyone had even half your empathy, the world would be unrecognizable.',
    'Tumhare andar ka insaan bahar ki duniya se bahut alag hai — better hai.',
    'Tum ek aisi kitaab ho jise padh ke log khud ko samajhne lagte hain.',
    "You're not just a friend. You're the kind of person people are grateful to have met.",
    'Having you around is like having a permanent mood booster.',
    "You're the person everyone hopes to become friends with someday.",
    "You don't just show up — you show up when it matters.",
    'Tumse baat karke lagta hai ki sab theek ho jayega.',
    'Tumhara saath hona matlab tension ka half ho jaana. ✨',
    "Whatever you're going through right now, know that you're handling it better than you think.",
    "You don't need validation from anyone. Your existence is already enough.",
    "You're closer to your goals than you think. Don't stop now.",
    'The effort you put in, even when no one notices, will pay off. Trust that.',
    'Tum bahut door aaye ho. Ruko mat, abhi bahut kuch baaki hai. 🚀',
    'Agar tum khud par believe karo, toh duniya ko bhi karna padega.',
    'Your taste in things is immaculate. Just saying.',
    "You've got main character energy and you don't even know it.",
    "I'm convinced you were designed in a lab to make people feel good.",
    "If confidence was contagious, you'd be a public health crisis. In a good way.",
    "You're the notification people actually want to see.",
    "You're like a human version of a perfectly brewed cup of coffee. ☕",
    'If good things happen to good people, your life is about to get real interesting.',
    'Tum internet pe ho, but tumhara energy real life wala hai.',
    'Tumse baat karna free therapy jaisa hai. 😂❤️',
    'Honestly, people who stay kind after being hurt deserve more credit than they get. Like you.',
    'You have a really good way of explaining things so they make perfect sense.',
    "You're one of those rare people who actually live by their principles.",
    'Your positive outlook is like a breath of fresh air when everyone else is complaining.',
    'You always find a way to bring out the best in people around you.',
    'Your creativity is honestly inspiring. You think of things nobody else does.',
    'You make the room feel warmer just by being in it.',
    'The passion you have for the things you care about is really admirable.',
    'You have an incredibly kind eyes and a welcoming presence.',
    'Your ability to see the good in bad situations is a rare quality.',
    'You are more capable than you realize, and it shows in how you handle tough times.',
    "You're the kind of person who leaves a positive mark on everyone you meet.",
    "You have a natural style and grace that doesn't need to try too hard.",
    "Your enthusiasm is contagious; it's hard not to feel motivated around you.",
    "You're an incredibly thoughtful listener, and it makes people feel valued.",
    'You have a beautiful way of putting things into perspective.',
    'Your laugh is one of the best sounds in the world.',
    "You're the person people are always happy to see walk through the door.",
    'You have a quiet confidence that is really attractive.',
    'The world would be a lot better if there were more people like you in it.',
    "You're a true original, and that is your greatest strength.",
]


# ── Roasts Pool (100+) ───────────────────────────────────────────────────────

ROASTS = [
    'Your luck is so bad, even autocorrect gives up on helping you. 😭',
    'You bring a calculator to count your mistakes and still run out of memory. 💀',
    'Google must be exhausted from answering your questions.',
    "If common sense was a superpower, you'd be a civilian.",
    "You're like a cloud — when you disappear, it's a beautiful day.",
    "Your brain has too many tabs open and they're all buffering.",
    "You're the reason 'instructions included' is printed on shampoo bottles.",
    'If ignorance is bliss, you must be the happiest person alive.',
    'Your ideas are like your WiFi — they never connect properly.',
    "You're not stupid, you just have bad luck when thinking. 😭",
    'Tera dimag itna tez hai ki khud se bhi aage nikal gaya — galat direction mein. 💀',
    "Tu Google pe 'how to be smart' search karta hai na? Bas samajh ja.",
    'Tere logic se toh calculator bhi confuse ho jaye.',
    "You're like a Monday — nobody looks forward to seeing you.",
    "If you were a spice, you'd be flour.",
    'Your personality has the excitement of a loading screen.',
    "You're the human equivalent of a participation trophy.",
    "If boring was a competition, you wouldn't even win that.",
    'Your charisma is like my phone battery — always at 1%.',
    "You're the reason group chats go silent.",
    "If you were a song, you'd be on hold music.",
    'Your vibe check came back negative.',
    'Tera swag dekhkar mirror ne bhi muh mod liya. 😂',
    'Tu itna boring hai ki neend ki goli bhi tujhse seekhti hai.',
    'Tere jokes pe hasna bhi ek dare hai.',
    'Tu party mein aata hai toh DJ bhi gaana band kar deta hai. 💀',
    'Your selfies come with a terms and conditions warning.',
    'Even your mirror needs therapy after looking at you. 😂',
    'You look like you were drawn from memory by someone who met you once.',
    'Your fashion sense is proof that confidence can carry anything.',
    "You put the 'try' in trying too hard.",
    'Tera profile photo dekh ke filter bhi ro deta hai. 😭',
    'Tere selfie se phone ka camera bhi PTSD mein chala gaya.',
    "Your social media presence has the same energy as a 'seen' without a reply.",
    'You post like you have a big audience but your mom is your only follower.',
    "Your online bio says 'living my best life' but your screen time says otherwise.",
    'Your Instagram grid looks like it was curated by a random number generator.',
    'Your tweets have less engagement than a traffic cone.',
    'Tere status update se zyada toh newspaper padhi jaati hai. 😂',
    "Tera WhatsApp status dekhkar log 'skip' karte hain. 💀",
    'You bring everyone so much joy — when you leave.',
    "If life gave you lemons, you'd probably lose them.",
    "You're living proof that evolution can go in reverse.",
    'Your existence is a plot twist nobody asked for.',
    "You're like a software update — nobody wants you, but you keep showing up.",
    'You have the survival instincts of a lemming.',
    'Even your GPS gives up on giving you directions.',
    'Your life is like a Wi-Fi connection — unstable and drops without warning.',
    'Teri kismat itni buri hai ki free mein bhi kuch nahi milta. 😭',
    'Tu lottery jeetega toh ticket gum ho jayega. 💀',
    'Tere plans toh barish mein bhi cancel ho jaate hain.',
    'Your love life has the consistency of weather in Mumbai.',
    "Your crush has a restraining order and they don't even know your name yet.",
    'You flirt like a toaster — shocking and outdated.',
    "If rizz was money, you'd owe people. 😂",
    'Your dating profile is the reason people choose cats.',
    'Teri love story se zyada sad toh electricity ka bill hai. 😭',
    'Tu propose karega toh ladki number block kar degi. 💀',
    "You try so hard and achieve so little. It's almost inspiring.",
    'Your ambition is like your alarm — always going off but never waking you up.',
    'You have the energy of a phone at 2% battery.',
    "You're the participation award of people.",
    "If effort was measured in naps, you'd be a champion.",
    'You have the attention span of a goldfish on energy drinks.',
    'Tere mehnat dekhkar toh aalsi log bhi mehnat karne lagte hain — taaki tere jaisa na banein. 😂',
    'Tu kaam karta hai toh lagta hai rest le raha hai, aur rest leta hai toh lagta hai coma mein hai. 💀',
    "You're like a human speed bump — slowing everyone down.",
    "If you were a vegetable, you'd be a plain boiled potato. No seasoning.",
    "Your aura reads 'buffering...'",
    "You're the reason aliens don't visit Earth.",
    'You have the decision-making skills of a magic 8-ball.',
    'Your cooking is the reason delivery apps exist.',
    "You're like the letter 'G' in lasagna — unnecessary but somehow there.",
    "If you were a font, you'd be Comic Sans. On a resume.",
    'You have the punctuality of Indian railways. 😂',
    'Teri planning dekhkar toh calendar bhi confuse hai.',
    'Tu itna unique hai ki teri copy bhi koi nahi kar sakta — karna chahta bhi nahi. 💀',
    'Tere baare mein sochke AI bhi crash ho gaya.',
    'Tu padhai karta hai ya padhai tujhse darta hai? 😭',
    'Tera time management dekhkar ghadi ne bhi resign de diya.',
    'Tu itna late aata hai ki tera welcome bhi expire ho jaata hai. 😂',
    "You're like a dictionary in a landfill — full of words but completely out of place.",
    "You're the human equivalent of a papercut: minor but extremely annoying.",
    "I'd agree with you, but then we'd both be wrong.",
    "Your life is like a movie, but it's the kind that goes straight to DVD.",
    "If you were a color, you'd be beige.",
    'You have the aura of someone who claps when the plane lands.',
    'Your arguments have the stability of a Jenga tower in an earthquake.',
    "You're not a complete idiot, some parts are missing.",
    "I'd explain it to you, but I don't have the time or the crayons.",
    'Your cooking is so bad, even the trash can would spit it out.',
    'Tu itna seedha hai ki jalebi bhi tujhe dekh ke sharma jaye. 😂',
    'Tere ideas toh humesha badhiya hote hain, bas chalte nahi hain.',
    'Tu single hai ya tera nature hi aisi safety check hai? 💀',
    'Tu chalta hai toh lagta hai slow-motion video chal rahi hai.',
    'Tere memes dekh kar log hanste nahi, bas report kar dete hain.',
    'Tu toh aalu jaisa hai, jahan jata hai bas space waste karta hai. 😂',
    'Tere advice lene se accha toh flips coins karna hai.',
    'Tu internet speed ki tarah hai, jab sabse zyada zaroorat hoti hai tabhi gayab.',
    'Tera status padh ke lagta hai ki keyboard pe billi chal gayi thi.',
    'Tu aalsi nahi hai, bas energy conservation mode pe rehta hai.',
]


# ── Helper Functions ──────────────────────────────────────────────────────────

def random_truth() -> str:
    return random.choice(TRUTHS)


def random_dare() -> str:
    return random.choice(DARES)


def random_puzzles() -> dict:
    return random.choice(PUZZLES_QS)


def random_quote() -> str:
    return random.choice(QUOTES)


def random_compliment(name: str = "") -> str:
    """Get a random curated compliment, optionally personalized with a name."""
    c = random.choice(COMPLIMENTS)
    if name:
        prefix = random.choice([f"{name}, ", f"Hey {name}, ", f"{name} - ", ""])
        if prefix:
            first_word = c.split()[0] if c else ""
            if first_word and first_word[0].isupper() and first_word not in ("I", "I'm", "Honestly", "Tum", "Tumhara", "Tumhari", "Tumse"):
                c = c[0].lower() + c[1:]
            return f"{prefix}{c}"
    return c


def random_roast(name: str = "") -> str:
    """Get a random curated roast, optionally personalized with a name."""
    r = random.choice(ROASTS)
    if name:
        prefix = random.choice([f"{name}, ", f"Hey {name}, ", f"{name} - ", ""])
        if prefix:
            first_word = r.split()[0] if r else ""
            if first_word and first_word[0].isupper() and first_word not in ("I", "I'd", "Google", "Tera", "Tere", "Teri", "Tu", "Toto"):
                r = r[0].lower() + r[1:]
            return f"{prefix}{r}"
    return r


# Legacy compatibility wrappers (used by fun.py before — kept for safety)
def random_roast_prompt(name: str) -> str:
    return random.choice([
        f"Give a brutal but funny 1-2 sentence roast for someone named {name}. Make it clever, not mean-spirited. No asterisks, no formatting.",
        f"Roast {name} in 1-2 sentences. Be witty and playful, like a friend who knows them too well. Keep it short.",
        f"Write a short savage roast for {name}. Funny, punchy, nothing hateful. Just vibe-check energy.",
    ])


def random_compliment_prompt(name: str) -> str:
    return random.choice([
        f"Give {name} a genuinely warm, specific compliment in 1-2 sentences. Sound real, not like a greeting card.",
        f"Say something really sweet and real to {name}. 1-2 sentences max. No formatting.",
        f"Compliment {name} in a way that actually feels personal and sincere. Short and punchy.",
    ])


async def get_target_user(client, message, default_to_sender: bool = True):
    """
    Centralized helper to resolve target user for commands.
    Resolution order:
    1. message.reply_to_message.from_user
    2. Mentioned user (via text_mention or mention entity)
    3. Username/ID argument in the message
    4. Sender (only if default_to_sender is True)
    
    If the target was explicitly requested but resolution failed, returns None.
    """
    from pyrogram import enums

    # 1. Reply to another message
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            return message.reply_to_message.from_user
        return None  # explicit target: reply message exists but no sender user

    # 2. Check entities for mentions
    if message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.TEXT_MENTION:
                return entity.user
            elif entity.type == enums.MessageEntityType.MENTION:
                mention_text = (message.text or message.caption or "")[entity.offset:entity.offset + entity.length]
                username = mention_text.lstrip("@")
                try:
                    return await client.get_users(username)
                except Exception:
                    return None  # explicit target mention failed to resolve

    # 3. Check command arguments
    if hasattr(message, "command") and len(message.command) > 1:
        arg = message.command[1].strip()
        if arg.startswith("@"):
            arg = arg[1:]

        # Try resolving as user ID or username
        try:
            if arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
                return await client.get_users(int(arg))
            else:
                return await client.get_users(arg)
        except Exception:
            return None  # explicit target argument failed to resolve

    # 4. Fallback to sender
    if default_to_sender:
        return message.from_user

    return None


async def handle_bot_target(client, message, target) -> bool:
    """
    Check if target is a bot or Sizu herself.
    If so, replies with a specific message and returns True (indicating handled).
    Otherwise returns False.
    """
    if target and target.is_bot:
        if target.id == client.me.id:
            playful = random.choice([
                "Nice try 😏",
                "Better luck next time 😂",
                "Aaj mujhe hi target kar diya?",
                "Mujhe target karke kya milega? 😂",
                "Trying to target me? Cute. 😏",
                "Mujhpe use karna hai? Bold move. 😂",
                "Main khud pe roast karun? Nah fam 💀",
                "Apne aap ko compliment de lun? Self-love goals 😭",
            ])
            await message.reply(playful)
        else:
            await message.reply("🤖 Specified user is a bot.")
        return True
    return False
