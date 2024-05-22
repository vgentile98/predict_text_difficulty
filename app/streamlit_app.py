# Import necessary libraries
import torch
import streamlit as st
import requests
import os
from transformers import CamembertTokenizer, CamembertForSequenceClassification
import streamlit.components.v1 as components
from itertools import cycle

st.set_page_config(layout='wide', page_title="OuiOui French Learning")

# Initialize user data and levels
cefr_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
default_user_data = {'default_user': {'level': 'A1', 'feedback_points': 0}}

# Function to ensure that user data is initialized in session state
def ensure_user_data():
    if 'users' not in st.session_state:
        st.session_state['users'] = default_user_data.copy()

# Fetch news articles from MediaStack
mediastack_api_key = '2ecbc982b44e1ae0338fb33482fe8813'
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
    st.title('Initial French Level Assessment')
    st.write("Select the main idea of the following sentences:")

    questions = [
        ("Le restaurant 'Bon appétit' recherche des serveurs pour l'été.", ["A restaurant is looking for summer staff.", "A restaurant is closing for the summer.", "A restaurant is changing its menu."], 0, 'A1'),
        ("Dans le centre de la ville, il y a un très joli quartier, plein de magasins chics et de bons restaurants.", ["There is a nice district with shops and restaurants.", "There is a park in the city center.", "There are many offices in the city center."], 0, 'A1'),
        ("Chaque année, l'humanité consomme plus de ressources que la Terre ne peut en produire en un an.", ["Humans consume more resources than the Earth can produce annually.", "The Earth produces more resources than humans need.", "Resources are equally consumed and produced."], 0, 'A2'),
        ("Il y a des régions où les enfants ne vont pas à l'école le mercredi.", ["In some regions, children don't go to school on Wednesdays.", "In some regions, children have school only on Wednesdays.", "In some regions, children go to school every day."], 0, 'A2'),
        ("Le menu est imaginé chaque jour en fonction de ce que les chefs trouvent au marché de Lyon.", ["The menu is created daily based on what chefs find at the market.", "The menu is the same every day.", "The menu changes weekly."], 0, 'B1'),
        ("Lorsqu'il y a un éclair avec des nuages et de la pluie, il risque d'y avoir de la foudre et du tonnerre.", ["Thunderstorms often bring lightning.", "Rain never comes with lightning.", "Thunderstorms are not dangerous."], 0, 'B1'),
        ("Tous ces bouleversements impliquent des conséquences tragiques comme l'augmentation de l'effet de serre et le réchauffement climatique.", ["Changes lead to greenhouse effect and climate warming.", "Changes have no impact on the environment.", "Climate warming is unrelated to greenhouse effect."], 0, 'B2'),
        ("Twitter va bannir les utilisateurs en cas de désinformation répétée sur les vaccins.", ["Twitter will ban users for repeated misinformation about vaccines.", "Twitter encourages misinformation.", "Twitter has no rules about vaccine misinformation."], 0, 'B2'),
        ("L'obésité frappe également l'Afrique subsaharienne, où vivent la plupart des populations sous-alimentées du monde (12,1 %), et l'Egypte (33%).", ["Obesity affects even undernourished regions.", "Obesity is only a problem in wealthy countries.", "Undernourishment is not an issue in Africa."], 0, 'C1'),
        ("Lucien Neuwirth, pionnier de la contraception, est mort dans la nuit de lundi à mardi à 89 ans, des suites d'une infection pulmonaire, à l'hôpital Rossini-Sainte-Périne à Paris.", ["Lucien Neuwirth, a contraception pioneer, died of a lung infection.", "Lucien Neuwirth invented a new vaccine.", "Lucien Neuwirth was a famous actor."], 0, 'C1'),
        ("Le ministre de l'Education a lancé un appel d'offres aux associations pour introduire en primaire une initiation au code informatique, facultative, sur les temps périscolaires dégagés par la réforme des rythmes scolaires.", ["The Minister of Education called for introducing optional coding classes in primary schools.", "The Minister of Education banned coding classes.", "The Minister of Education made coding mandatory in high schools."], 0, 'C2'),
        ("Auparavant, la duplication de l'ADN se faisait par clonage moléculaire : la séquence d'intérêt était insérée dans le génome d'une bactérie et l'on se servait du taux de croissance élevé du micro-organisme pour obtenir autant de clones de la séquence d'ADN.", ["DNA duplication was done through molecular cloning.", "DNA was duplicated by using viruses.", "Molecular cloning was used to destroy DNA."], 0, 'C2')
    ]

    responses = {}

    for j in range(0, len(questions), 2):
        cols = st.columns(2)
        for k, (sentence, choices, correct, level) in enumerate(questions[j:j+2]):
            with cols[k]:
                st.markdown(
                    f"<div style='background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px; min-height: 200px;'>"
                    f"<b>{j+k+1}. {sentence}</b></div>",
                    unsafe_allow_html=True
                )
                responses[f"q_{j+k}"] = st.radio(
                    "",
                    choices,
                    key=f"q_{j+k}"
                )

    if st.button("Submit"):
        total_score = 0
        for i, (_, choices, correct, level) in enumerate(questions):
            if responses.get(f"q_{i}") == choices[correct]:
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


def main():
    ensure_user_data()

    if 'start' not in st.session_state:
        st.session_state['start'] = False  # This keeps track of whether the user has started the app

    if not st.session_state['start']:
        st.title('')
        st.title('')
        st.title('')
        st.markdown("<style>div.row-widget.stButton > button:first-child {margin: 0 auto; display: block;}</style>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            left_co, cent_co, last_co = st.columns(3)
            with cent_co:
                st.image("https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/baguette_logo.png")
            st.markdown("<h1 style='text-align: center; color: black;'>From 'Oui Oui' to Fluent</h1>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center; color: black;'>Start your journey to master French now</h4>", unsafe_allow_html=True)
            if st.button("Je commence!"):
                st.session_state['start'] = True
                st.session_state['initial_assessment'] = True

    # Initial Assessment
    elif st.session_state.get('initial_assessment', False):
        initial_assessment()

    else:
        # Title
        st.title('Curated articles just for you')
        st.subheader('Read, learn, and grow at your own pace!')

        # Select options for the API request
        category = st.selectbox("What do you want to read about?", ['general', 'business', 'technology', 'entertainment', 'sports', 'science', 'health'], index=1)
        st.markdown("---")

        # Sidebar elements
        with st.sidebar:
            logo_url = "https://raw.githubusercontent.com/vgentile98/predict_text_difficulty/main/app/baguette_logo.png"
            st.image(logo_url, width=200)
            user_id = 'default_user'
            ensure_user_data()
            user_level = st.session_state['users'][user_id]['level']
            st.subheader(f"Your current level: {user_level}")

        ensure_user_data()

        user_id = 'default_user'
        user_level = st.session_state['users'][user_id]['level']

        articles = fetch_news(category)
        if articles:
            articles = assign_article_levels(articles)
            articles = [article for article in articles if article.get('level') == user_level and is_valid_image_url(article.get('image'))]
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
                    with st.expander("Read Now"):
                        components.iframe(article['url'], height=450, scrolling=True)
                        cols = st.columns(4)
                        feedback_options = ['Too Easy', 'Just Right', 'Challenging', 'Too Difficult']
                        for i, option in enumerate(feedback_options):
                            if cols[i].button(option, key=f"feedback_{idx}_{i}"):
                                new_level = update_user_level(user_id, option)
                                st.session_state['users'][user_id]['level'] = new_level
                                st.experimental_rerun()
                    st.markdown("---")
        else:
            st.write("No articles found. Try adjusting your filters.")

if __name__ == '__main__':
    main()
