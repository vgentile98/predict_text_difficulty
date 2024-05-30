# Import necessary libraries
import torch
import streamlit as st
import requests
import os
from transformers import CamembertTokenizer, CamembertForSequenceClassification
import streamlit.components.v1 as components
from itertools import cycle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import isodate
from streamlit_navigation_bar import st_navbar
from googletrans import Translator
from PyDictionary import PyDictionary
import time
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import random
import numpy as np

# Page Config
st.set_page_config(layout='wide', page_title="OuiOui French Learning")

# Initialize user data and levels
cefr_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
default_user_data = {'default_user': {'level': 'A1', 'feedback_points': 0}}

# Initialize some initial tracking data to simulate evolution if not already initialized
if 'tracking_data' not in st.session_state:
    initial_dates = [datetime.today() - timedelta(days=i) for i in range(59, -1, -1)]
    initial_levels = ['A1']*29 + ['A2']*30 + ['B1']*1
    initial_words = ['tempête', 'engueuler', 'rigoler', 'jaune', 'dormir', 'bleu', 'voiture', 'ciseaux', 'souris', 'lapin']

    # Create a variable number of words learned per day
    words_per_day = [1, 2, 0, 1, 2, 1, 3, 2, 1, 0, 1, 2, 1, 3, 2, 2, 2, 0, 0, 2, 0, 3, 0, 0, 0, 1, 2, 1, 3, 2, 1, 2, 0, 1, 2, 1, 3, 1, 1, 0, 1, 2, 1, 1, 1, 1, 0, 0, 1, 2, 1, 2, 0, 0, 0, 1, 2, 1, 3, 2]
    words_learned = []
    word_index = 0
    for i, date in enumerate(initial_dates):
        for _ in range(words_per_day[i]):
            words_learned.append((date, initial_words[word_index % len(initial_words)]))
            word_index += 1

    # Create a variable number of articles and videos read per day
    categories = ['general', 'business', 'technology', 'entertainment', 'sports', 'science', 'health']
    articles_read = []
    videos_watched = []
    for date in initial_dates:
        for _ in range(random.randint(0, 3)):  # Variable number of articles per day
            articles_read.append((date, random.choice(categories)))
        for _ in range(random.randint(0, 2)):  # Variable number of videos per day
            videos_watched.append((date, random.choice(categories)))

    st.session_state['tracking_data'] = {
        'levels': list(zip(initial_dates, initial_levels)),
        'articles_read': articles_read,
        'videos_watched': videos_watched,
        'words_learned': words_learned
    }
    
# Function to ensure that user data is initialized in session state
def ensure_user_data():
    if 'users' not in st.session_state:
        st.session_state['users'] = default_user_data.copy()

# Fetch news articles from MediaStack
mediastack_api_key = '76ab282b82f324666ac2a5510fd7f9f2'
base_url = "http://api.mediastack.com/v1/news"

# Fetch news articles from mediastack API
def fetch_news(category):
    params = {
        'access_key': mediastack_api_key,
        'languages': "fr",
        'categories': category,
        'limit': 3
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['data']
    else:
        st.error('Failed to retrieve news articles.')
        return []

# Function to check if the image URL is valid
def is_valid_image_url(url):
    if url is None:
        return False
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200 and 'image' in response.headers['Content-Type']
    except requests.RequestException:
        return False
        
# Function to assign levels to articles
def assign_article_levels(articles):
     level_cycle = cycle(cefr_levels)  # Create a cycle iterator from CEFR levels
     valid_articles = [article for article in articles if is_valid_image_url(article.get('image'))]
     for article in valid_articles:
         article['level'] = next(level_cycle)  # Assign levels in a cyclic manner
     return valid_articles

# YouTube API key
youtube_api_key = 'AIzaSyCHIkxj1VdqAhzb9M3lSJPxzU9LKb1DXyQ'

# Define the list of allowed channel IDs
allowed_channels = [
    'UCYpRDnhk5H8h16jpS84uqsA', #lemondefr
    'UCCDz_XYeKWd0OIyjp95dqyQ', #LeFigaro
    'UCAcAnMF0OrCtUep3Y4M-ZPw', #HugoDécrypte
    'UCb4UAZwZqS4a35FrBcLlMXA', #Canalplus
    'UCdKTlsmvczkdvGjiLinQwmw', #Philoxime
    'UCNovJemYKcdKt7PDdptJZfQ', #jean-marcjancovici2537
    'UCah8C0gmLkdtvsy0b2jrjrw', #CyrusNorth
    'UC8ggH3zU61XO0nMskSQwZdA', #CanalplusSport
    'UCkkY_V2YSa_oln5CXm4zDzw', #Amideslobbies
    'UCSULDz1yaHLVQWHpm4g_GHA', # monsieurbidouille
    'UC1EacOJoqsKaYxaDomTCTEQ', #LeReveilleur
    'UCsT0YIqwnpJCM-mx7-gSA4Q', #TEDx
    'UCYxgidQYV3WPD0eeVGOgibg', #Startupfood
    'UCSmUdD2Dd_v5uqBuRwtEZug', #MarketingMania
    'UC4ii4_aeS8iOFzsHuhJTq2w', #poissonfecond
    'UCaNlbnghtwlsGF-KzAFThqA', #ScienceEtonnante
    'UCWnfDPdZw6A23UtuBpYBbAg', #DrNozman
    'UCeR8BYZS7IHYjk_9Mh5JgkA', #scilabus
    'UCS_7tplUgzJG4DhA16re5Yg', #BaladeMentale
    'UCOchT7ZJ4TXe3stdLW1Sfxw', #DansTonCorps
    'UC9BnGZLT4iPaJtDOXYwQuHQ', #PrimumNonNocereVideo
    'UCDqEttzOpPbDoeC05HRPPDQ', #AsclepiosYT
    'UCsE6tdKFV2oSHFyDll72rWg', #PsykoCouac
    'UCAkhrilzn2OWOp1AsB3VJmg', #Bananamo
    'UC8fgz_7wFO_APrt6LXcQ_iw', #JacksTeam
    'UC5WFSncb01pBfKcQw3mfO9A', #latribunetvevents
    'UCO6K_kkdP-lnSCiO3tPx7WA', #franceinfo
    'UCwI-JbGNsojunnHbFAc0M4Q', #arte
    'UCJy0lX8ThZ7lCtst7JnegWQ', #jojol
    'UC5Twj1Axp_-9HLsZ5o_cEQQ', #DocSeven
    'UC__xRB5L4toU9yYawt_lIKg' #blastinfo
]
        
# Fetch YouTube videos with transcripts from specific channels
def fetch_youtube_videos_with_transcripts(query, max_videos=3):
    try:
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        videos = []

        for channel_id in allowed_channels:
            if len(videos) >= max_videos:
                break

            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=1,
                type='video',
                relevanceLanguage='fr',
                channelId=channel_id
            ).execute()

            for item in search_response.get('items', []):
                if len(videos) >= max_videos:
                    break

                video_id = item['id']['videoId']
                video_url = f'https://www.youtube.com/watch?v={video_id}'

                # Get video details
                video_response = youtube.videos().list(
                    part='contentDetails',
                    id=video_id
                ).execute()

                duration = video_response['items'][0]['contentDetails']['duration']
                duration_seconds = isodate.parse_duration(duration).total_seconds()

                # Filter out videos not in the 2 to 15 minutes range
                if duration_seconds < 120 or duration_seconds > 900:
                    continue

                try:
                    # Get transcript
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr'])
                    full_text = " ".join([text['text'] for text in transcript])

                    videos.append({
                        'id': video_id,
                        'url': video_url,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'transcript': full_text,
                        'duration': duration
                    })
                except (NoTranscriptFound, TranscriptsDisabled):
                    continue

        return videos

    except HttpError as e:
        st.error("An error occurred with the YouTube API.")
        st.error(e)
        return []

        
# Dummy function to assign levels to videos based on the transcript
def assign_video_levels(videos):
    level_cycle = cycle(cefr_levels)
    for video in videos:
        video['level'] = next(level_cycle)
    return videos

# Load the model from GitHub
def download_file_from_github(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as f:
            f.write(response.content)
    else:
        st.error("Failed to download file. Check the URL and network connection.")

def setup_model():
    """Setup the model by ensuring all necessary files are downloaded and loaded."""
    model_dir = 'predict_text_difficulty/app'
    os.makedirs(model_dir, exist_ok=True)

    # Check if model files are already downloaded, else download them
    model_files = {
        'config.json': 'https://github.com/vgentile98/predict_text_difficulty/raw/main/app/config.json',
        'tokenizer_config.json': 'https://github.com/vgentile98/predict_text_difficulty/raw/main/app/tokenizer_config.json',
        'special_tokens_map.json': 'https://github.com/vgentile98/predict_text_difficulty/raw/main/app/special_tokens_map.json',
        'added_tokens.json': 'https://github.com/vgentile98/predict_text_difficulty/raw/main/app/added_tokens.json',
        'model.safetensors': 'https://github.com/vgentile98/predict_text_difficulty/raw/main/app/model.safetensors',
        'sentencepiece.bpe': 'https://github.com/vgentile98/predict_text_difficulty/raw/main/app/sentencepiece.bpe.model'
    }

    for file_name, url in model_files.items():
        file_path = os.path.join(model_dir, file_name)
        if not os.path.exists(file_path):
            download_file_from_github(url, file_path)

    # Load model and tokenizer
    #try:
        #tokenizer = CamembertTokenizer.from_pretrained(model_dir)
        #model = CamembertForSequenceClassification.from_pretrained(model_dir)
        #return model, tokenizer
    #except Exception as e:
        #st.exception(e)
        #raise

# Setup the model
#try:
    #model, tokenizer = setup_model()
#except Exception as e:
    #st.error("An error occurred while setting up the model.")

# Function to update user level based on feedback
def update_user_level(user_id, feedback):
    # Make sure user data is available
    ensure_user_data()

    # Access the user data safely from session state
    feedback_points = {'Too Easy': 1, 'Just Right': 0.5, 'Challenging': 0.5, 'Too Difficult': -1}
    user_data = st.session_state['users'][user_id]
    user_data['feedback_points'] += feedback_points[feedback]

    # Thresholds for level change
    upgrade_threshold = 3 # Points needed to move up a level
    downgrade_threshold = -3 # Points needed to move down a level

    # Accessing CEFR levels
    current_index = cefr_levels.index(user_data['level'])

    # Level Change
    if user_data['feedback_points'] >= upgrade_threshold:
        new_index = min(current_index + 1, len(cefr_levels) - 1)
        user_data['level'] = cefr_levels[new_index]
        user_data['feedback_points'] = 0 # Reset points after level change
    elif user_data['feedback_points'] <= downgrade_threshold:
        new_index = max(current_index - 1, 0)
        user_data['level'] = cefr_levels[new_index]
        user_data['feedback_points'] = 0 # Reset points after level change

    # Update the user data in session state
    st.session_state['users'][user_id] = user_data
    update_tracking_data('level')

    return user_data['level']

def predict_article_levels(articles, model, tokenizer):
    for article in articles:
        if is_valid_image_url(article.get('image')):
            text = article['title'] + " " + article['description']
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = outputs.logits.argmax(-1).item()
            # Assuming you've mapped the model's output indices to CEFR levels:
                article['level'] = cefr_levels[predictions]
    return articles

# Function for initial assessment
def initial_assessment():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title('Bonjour ! I\'m Baguette, your new French buddy')
        st.subheader("Let\'s start our adventure with a game")
        st.write("Read each sentence and choose the main idea from the options below. Let\'s see how much you already know!")
    with col2:
        st.image("https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/images/baguette_salut.png", width=200)
        
    questions = [
        ("Le restaurant 'Bon appétit' recherche des serveurs pour l'été.", ["A restaurant is closing for the summer.", "A restaurant is looking for summer staff.", "A restaurant is changing its menu."], 1, 'A1'),
        ("Dans le centre de la ville, il y a un très joli quartier, plein de magasins chics et de bons restaurants.", ["There is a park in the city center.", "There are many offices in the city center.", "There is a nice district with shops and restaurants."], 2, 'A1'),
        ("Chaque année, l'humanité consomme plus de ressources que la Terre ne peut en produire en un an.", ["Humans consume more resources than the Earth can produce annually.", "The Earth produces more resources than humans need.", "Resources are equally consumed and produced."], 0, 'A2'),
        ("Il y a des régions où les enfants ne vont pas à l'école le mercredi.", ["In some regions, children don't go to school on Wednesdays.", "In some regions, children have school only on Wednesdays.", "In some regions, children go to school every day."], 0, 'A2'),
        ("Le menu est imaginé chaque jour en fonction de ce que les chefs trouvent au marché de Lyon.", ["The menu is the same every day.", "The menu is changed weekly based on what chefs find at the market.", "The menu is changed daily based on what chefs find at the market."], 2, 'B1'),
        ("Lorsqu'il y a un éclair avec des nuages et de la pluie, il risque d'y avoir de la foudre et du tonnerre.", ["Thunderstorms often bring lightning.", "Rain never comes with lightning.", "Thunderstorms are not dangerous."], 0, 'B1'),
        ("La réduction du dioxyde de carbone par l'eau nécessite un apport d'énergie assez élevé.", ["Reducing carbon dioxide with water lowers the energy requirements.", "Reducing carbon dioxide with water requires a significant energy input.", "Reducing carbon dioxide with water is an energy-free process."], 1, 'B2'),
        ("Twitter va bannir les utilisateurs en cas de désinformation répétée sur les vaccins.", ["Twitter will warn users for repeated misinformation about vaccines.", "Twitter will ban users for repeated misinformation about vaccines.", "Twitter has no rules about vaccine misinformation."], 1, 'B2'),
        ("L'obésité frappe également l'Afrique subsaharienne, où vivent la plupart des populations sous-alimentées du monde (12,1 %), et l'Egypte (33%).", ["Obesity is only a problem in wealthy countries.", "Undernourishment is not an issue in Egypt.", "Obesity affects even undernourished regions."], 2, 'C1'),
        ("Lucien Neuwirth, pionnier de la contraception, est mort dans la nuit de lundi à mardi à 89 ans, des suites d'une infection pulmonaire, à l'hôpital Rossini-Sainte-Périne à Paris.", ["Lucien Neuwirth, a contraception pioneer, died of lung infection.", "Lucien Neuwirth invented a new contraception.", "Lucien Neuwirth is currently treated for lung infection."], 0, 'C1'),
        ("Le ministre de l'Education a lancé un appel d'offres aux associations pour introduire en primaire une initiation au code informatique, facultative, sur les temps périscolaires dégagés par la réforme des rythmes scolaires.", ["The Minister of Education wants to introduce optional coding classes in primary schools.", "The Minister of Education banned coding classes in high schools.", "The Minister of Education wants to introduce mandatory coding classes in primary schools."], 0, 'C2'),
        ("La duplication de l'ADN se faisait par clonage moléculaire : la séquence d'intérêt était insérée dans le génome d'une bactérie et l'on se servait du taux de croissance élevé du micro-organisme pour obtenir autant de clones de la séquence d'ADN.", ["DNA was duplicated by using viruses.", "DNA duplication was done through molecular cloning.", "Molecular cloning was used to modify DNA."], 1, 'C2')
    ]

    # CSS style for custom design
    st.markdown(
        """
        <style>
        .question-box {
            background-color: #cba181;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-top: 5px;
            color: #241000;
            min-height: 90px;
        }
        .question-text {
            font-size: 16px;
            margin-bottom: 0px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    responses = {}
    for j in range(0, len(questions), 2):
        cols = st.columns(2, gap="medium")
        for k, (sentence, choices, correct, level) in enumerate(questions[j:j+2]):
            with cols[k]:
                st.markdown(
                    f"""
                    <div class='question-box'>
                        <div class='question-text'><b>{j+k+1}. {sentence}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                responses[f"q_{j+k}"] = st.radio("", choices, key=f"q_{j+k}")
                
    st.markdown("<style>div.row-widget.stButton > button:first-child {margin: 0 auto; font-weight: bold; display: block;}</style>", unsafe_allow_html=True)
    if st.button("C'est parti !"):
        total_score = 0
        for i, (_, choices, correct, level) in enumerate(questions):
            selected = responses.get(f"q_{i}")
            if selected == choices[correct]:
                total_score += 1

        user_id = 'default_user'
        if total_score <= 2:
            st.session_state['users'][user_id]['level'] = 'A1'
        elif total_score <= 4:
            st.session_state['users'][user_id]['level'] = 'A2'
        elif total_score <= 6:
            st.session_state['users'][user_id]['level'] = 'B1'
        elif total_score <= 8:
            st.session_state['users'][user_id]['level'] = 'B2'
        elif total_score <= 10:
            st.session_state['users'][user_id]['level'] = 'C1'
        else:
            st.session_state['users'][user_id]['level'] = 'C2'
        
        st.session_state['initial_assessment'] = False

def learn_page():
    # User Data
    ensure_user_data()
    user_id = 'default_user'
    user_level = st.session_state['users'][user_id]['level']

    # Title
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title('Voilà ! My Top Picks Just for You 🗞️')
        st.subheader('Ready to Explore?')
        # Select options for the API request
        category = st.selectbox("What piques your curiosity in the world of French?", ['general', 'business', 'technology', 'entertainment', 'sports', 'science', 'health'], index=1)
    with col2:
        st.image("https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/images/baguette_news.png", width=250)

    st.markdown("---")

    # Sidebar elements
    with st.sidebar:
        logo_url = "https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/images/baguette_logo.png"
        st.image(logo_url, width=200)
        
        st.header("Your Progress")
        st.write(f"🚀 Current level: {user_level}")
        st.write("🌟 Badge: Beginner Explorer")

        st.markdown("---")

        st.header("Your Vocabulary")
        
        st.subheader("Word Details")
        check_word_sidebar = st.text_input("Not sure about a word?", key="check_word")
        if st.button("Check Word", key="check_word_button"):
            if check_word_sidebar:
                st.session_state['translation'] = translate_to_english(check_word_sidebar)
                st.session_state['definition'] = get_single_definition(check_word_sidebar)
                st.experimental_rerun()  # Rerun to display the results
            else:
                st.warning("Please enter a word before checking.")

        if 'translation' in st.session_state and 'definition' in st.session_state:
            st.write(f"**Translation:** {st.session_state['translation']}")
            st.write(f"**Definition:** {st.session_state['definition']}")

        st.subheader("Add to Vocabulary")      
        new_word_sidebar = st.text_input("Got a new word that's puzzling you?", key="new_word_sidebar")
        if st.button("Add Word", key="add_word_sidebar"):
            if new_word_sidebar:
                st.session_state['vocab_list'].append(new_word_sidebar.strip())
                st.success(f"'{new_word_sidebar}' added to vocabulary!")
                update_tracking_data('word', word=new_word_sidebar.strip())  # Update tracking data
                time.sleep(2)
                st.experimental_rerun()  # Rerun to clear the input field
            else:
                st.warning("Please enter a word before adding.")
                
    # Fetch and display news articles
    articles = fetch_news(category)
    if articles:
        articles = assign_article_levels(articles)
        articles = [article for article in articles if article.get('level') == user_level and is_valid_image_url(article.get('image'))] # Filter articles by user level
        for idx, article in enumerate(articles):
            with st.container():
                # First row for image and level
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.image(article['image'], width=300)
                with col2:
                    st.markdown(f"<div style='border: 1px solid gray; border-radius: 4px; padding: 10px; text-align: center;'><strong>{article['level']}</strong></div>", unsafe_allow_html=True)
                st.subheader(article['title'])
                st.write(article['description'])
                with st.expander("**Read Now**", expanded=False):
                    st.write("#### Full Article")  # Prompt for feedback
                    components.iframe(article['url'], height=450, scrolling=True)
                    st.write("#### How was it?")  # Prompt for feedback
                    cols = st.columns(7, gap="small")
                    feedback_options = [
                        ('Too Easy', '😌'),
                        ('Just Right', '😊'),
                        ('Challenging', '😅'),
                        ('Too Difficult', '😓')
                    ]
                    for i, (option, emoji) in enumerate(feedback_options):
                        if cols[i].button(f"{emoji} {option}", key=f"feedback_{idx}_{i}"):
                            new_level = update_user_level(user_id, option)
                            st.session_state['users'][user_id]['level'] = new_level
                            update_tracking_data('article', category=category)  # Update tracking data
                            update_tracking_data('level')  # Track level change
                            st.experimental_rerun()
                st.markdown("---")
    else:
        st.write("No articles found. Try adjusting your filters.")

    # Custom CSS for video width
    st.markdown(
     """
    <style>
    .custom-video {
        max-width: 100%;
        width: 600px;
        height: 280px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Fetch and display YouTube videos with transcripts
    videos = fetch_youtube_videos_with_transcripts(category)
    if videos:
        videos = assign_video_levels(videos)
        user_level_videos = [video for video in videos if video.get('level') == user_level]  # Filter videos by user level
        for idx, video in enumerate(user_level_videos):
            with st.container():
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    if 'id' in video and video['id']:
                        st.markdown(f'<iframe class="custom-video" src="https://www.youtube.com/embed/{video["id"]}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                        #video_url = f"https://www.youtube.com/embed/{video['id']}"
                        #st.components.v1.iframe(video_url, height=400, style="max-width: 500px; width: 100%;")
                    else:
                        st.error("Error: Video ID not found.")
                with col2:
                    st.markdown(f"<div style='border: 1px solid gray; border-radius: 4px; padding: 10px; text-align: center;'><strong>{video.get('level', 'Unknown')}</strong></div>", unsafe_allow_html=True)
                st.subheader(video.get('title', 'No Title'))
                with st.expander("**See Transcript**", expanded=False):
                    st.write("#### Transcript")  # Prompt for feedback
                    st.write(video.get('transcript', 'No transcript available.'))
                    st.write("#### How was it?")  # Prompt for feedback
                    cols = st.columns(7, gap="small")
                    feedback_options = [
                        ('Too Easy', '😌'),
                        ('Just Right', '😊'),
                        ('Challenging', '😅'),
                        ('Too Difficult', '😓')
                    ]
                    for i, (option, emoji) in enumerate(feedback_options):
                        if cols[i].button(f"{emoji} {option}", key=f"video_feedback_{idx}_{i}"):
                            new_level = update_user_level(user_id, option)
                            st.session_state['users'][user_id]['level'] = new_level
                            update_tracking_data('video', category=category)  # Update tracking data
                            update_tracking_data('level')  # Track level change
                            st.experimental_rerun()
                st.markdown("---")
    else:
        st.write("No videos found. Try adjusting your filters.")
        
# Initialize Translator and PyDictionary
translator = Translator()
dictionary = PyDictionary()

# Function to translate text from French to English
def translate_to_english(word):
    translation = translator.translate(word, src='fr', dest='en')
    return translation.text

# Function to get a single definition of a word
def get_single_definition(word):
    meaning = dictionary.meaning(word)
    if meaning:
        for pos, defs in meaning.items():
            if defs:
                return defs[0]
    return "No definition found."

# Initialize session state for vocab list if it doesn't exist
if 'vocab_list' not in st.session_state:
    st.session_state['vocab_list'] = []
if 'learned_words' not in st.session_state:
    st.session_state['learned_words'] = []
            
def rehearse_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Let's Rehearse Your French Vocabulary! 📚")

        st.subheader("Got a new word that's puzzling you?")
        new_word = st.text_input("Type in the French word here:", key="new_word")

        if st.button("Add to My List ✍️", key="add_word"):
            if new_word:
                st.session_state['vocab_list'].append(new_word.strip())
                st.success(f"Great! '{new_word}' has been added to your vocabulary list. 🎉")
                update_tracking_data('word', word=new_word.strip())  # Update tracking data
                time.sleep(2)
                st.experimental_rerun()  # Rerun to clear the input field
            else:
                st.warning("Oops! Don't forget to type a word before adding it. 📝")

    with col2:
        st.image("https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/images/baguette_vocab.png", width=300)

    st.markdown("---")

    st.subheader("Your Current Vocabulary List 🗒️")
    if st.session_state['vocab_list']:
        for idx, word in enumerate(st.session_state['vocab_list']):
            col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
            with col1:
                st.write(word)
            with col2:
                translation = translate_to_english(word)
                st.write(translation)
            with col3:
                definition = get_single_definition(translation)
                st.write(definition)
            with col4:
                if st.button(f"✅ Learned", key=f"learn_{idx}"):
                    st.session_state['learned_words'].append((word, translation, definition))
                    st.session_state['vocab_list'].pop(idx)
                    st.experimental_rerun()  # Refresh the page to reflect changes
            with col5:
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state['vocab_list'].pop(idx)
                    st.experimental_rerun()  # Refresh the page to reflect changes
    else:
        st.write("No words here yet. Add some new vocabulary to get started! ✨")

    st.markdown("---")

    st.subheader("Your Learned Words 🏅")
    if st.session_state['learned_words']:
        for idx, (word, translation, definition) in enumerate(st.session_state['learned_words']):
            col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
            with col1:
                st.write(word)
            with col2:
                st.write(translation)
            with col3:
                st.write(definition)
            with col4:
                if st.button(f"🔙 Rehearse", key=f"rehearse_{idx}_learned"):
                    st.session_state['vocab_list'].append(word)
                    st.session_state['learned_words'].pop(idx)
                    st.experimental_rerun()  # Refresh the page to reflect changes
            with col5:
                if st.button("🗑️ Remove", key=f"remove_{idx}_learned"):
                    st.session_state['learned_words'].pop(idx)
                    st.experimental_rerun()  # Refresh the page to reflect changes
    else:
        st.write("You haven't marked any words as learned yet. Keep up the great work! 💪")

    st.markdown("---")

# Tracking data update function
def update_tracking_data(type, category=None, word=None):
    date_today = datetime.today().strftime('%Y-%m-%d')
    
    if type == 'level':
        level = st.session_state['users']['default_user']['level']
        st.session_state['tracking_data']['levels'].append((date_today, level))
    
    if type == 'article':
        st.session_state['tracking_data']['articles_read'].append((date_today, category))
    
    if type == 'video':
        st.session_state['tracking_data']['videos_watched'].append((date_today, category))
    
    if type == 'word':
        st.session_state['tracking_data']['words_learned'].append((date_today, word))

def track_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Track Your Progress 📈")
        st.subheader("Bravo! You've been working hard - It's time to check where you're at!")
    with col2:
        st.image("https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/images/baguette_progress.png", width=300)

    sns.set_style("whitegrid", {'axes.facecolor': '#fdf1e1', 'figure.facecolor': '#fdf1e1'})

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("Language Level Evolution")
        level_evolution = pd.DataFrame(st.session_state['tracking_data']['levels'], columns=['Date', 'Level'])
        if not level_evolution.empty:
            level_evolution['Date'] = pd.to_datetime(level_evolution['Date'])
            level_evolution['Week'] = level_evolution['Date'].dt.to_period('W').apply(lambda r: r.start_time)
            level_evolution_grouped = level_evolution.groupby('Week')['Level'].agg(lambda x: x.value_counts().index[0]).reset_index()
            level_evolution_grouped['Level'] = pd.Categorical(level_evolution_grouped['Level'], categories=cefr_levels, ordered=True)
            
            plt.figure(figsize=(10, 5))
            plt.plot(level_evolution_grouped['Week'], level_evolution_grouped['Level'].cat.codes + 1, marker='o', color='#fda500')
            plt.xlabel('Date')
            plt.ylabel('Level')
            plt.yticks(ticks=range(1, len(cefr_levels) + 1), labels=cefr_levels)
            plt.grid(True)
            plt.gca().set_facecolor('#fdf1e1')
            plt.gcf().set_facecolor('#fdf1e1')
            plt.xticks(rotation=45)
            st.pyplot(plt)
        else:
            st.write("No data available yet.")

    with col2:
        st.subheader("Words Learned Over Time")
        words_learned = pd.DataFrame(st.session_state['tracking_data']['words_learned'], columns=['Date', 'Word'])
        if not words_learned.empty:
            words_learned['Date'] = pd.to_datetime(words_learned['Date'])
            words_learned['Week'] = words_learned['Date'].dt.to_period('W').apply(lambda r: r.start_time)
            words_learned_grouped = words_learned.groupby('Week').count().reset_index()
            words_learned_grouped.rename(columns={'Word': 'Count'}, inplace=True)
            
            plt.figure(figsize=(10, 5))
            plt.plot(words_learned_grouped['Week'], words_learned_grouped['Count'], marker='o', color='#fda500')
            plt.xlabel('Date')
            plt.ylabel('Count')
            plt.grid(True)
            plt.gca().set_facecolor('#fdf1e1')
            plt.gcf().set_facecolor('#fdf1e1')
            plt.xticks(rotation=45)
            st.pyplot(plt)
        else:
            st.write("No words learned yet.")

    articles_read = pd.DataFrame(st.session_state['tracking_data']['articles_read'], columns=['Date', 'Category'])
    videos_watched = pd.DataFrame(st.session_state['tracking_data']['videos_watched'], columns=['Date', 'Category'])

    if not articles_read.empty or not videos_watched.empty:
        combined_read = pd.concat([articles_read, videos_watched])
        combined_read['Date'] = pd.to_datetime(combined_read['Date'])
        combined_read['Week'] = combined_read['Date'].dt.to_period('W').apply(lambda r: r.start_time)
        combined_read['Count'] = 1
        combined_read_grouped = combined_read.groupby(['Week', 'Category']).count().reset_index()

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.subheader("Articles and Videos Read Over Time")
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=combined_read_grouped, x='Week', y='Count', hue='Category', marker='o', palette='tab10')
            plt.xlabel('Date')
            plt.ylabel('Count')
            plt.grid(True)
            plt.gca().set_facecolor('#fdf1e1')
            plt.gcf().set_facecolor('#fdf1e1')
            plt.xticks(rotation=45)
            st.pyplot(plt)

        with col2:
            st.subheader("Distribution of Types of Content Read")
            content_counts = combined_read['Category'].value_counts()
            plt.figure(figsize=(5, 2))
            plt.pie(content_counts, labels=content_counts.index, autopct='%1.1f%%', startangle=140, colors=['#fda500', '#fdaa00', '#fdac00', '#fdaf00', '#fdb100', '#fdb300', '#fdb500'], textprops={'fontsize': 5})
            plt.gca().set_facecolor('#fdf1e1')
            plt.gcf().set_facecolor('#fdf1e1')
            st.pyplot(plt)
    else:
        st.write("No articles or videos read yet.")

def main():
    ensure_user_data()

    if 'start' not in st.session_state:
        st.session_state['start'] = False  # This keeps track of whether the user has started the app

    if not st.session_state['start']:
        st.title('')
        st.markdown("<style>div.row-widget.stButton > button:first-child {margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            left_co, cent_co, last_co = st.columns(3)
            with cent_co:
                st.image("https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/images/baguette_logo.png")
            st.markdown("<h1 style='text-align: center; color: black;'>From 'Oui Oui' to Fluent</h1>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: black;'>Start your journey to master French now</h4>", unsafe_allow_html=True)
            if st.button("Je commence!"):
                st.session_state['start'] = True
                st.session_state['initial_assessment'] = True

    elif st.session_state.get('initial_assessment', False):
        initial_assessment()

    else:
        pages = ["Learn", "Rehearse", "Track"]
        page = st_navbar(pages)
        
        if page == "Learn":
            learn_page()
        elif page == "Rehearse":
            rehearse_page()
        elif page == "Track":
            track_page()

if __name__ == '__main__':
    main()

