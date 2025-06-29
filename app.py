# Import necessary libraries
import streamlit as st
import base64
import httpx
import config
from openai import OpenAI
import json
import os

import streamlit_agent.utils

# Load general configuration variables
ssl_cert_file = config.SSL_CERT_FILE

# Azure DevOps configuration
organization = config.ORGANIZATION
personal_access_token = config.PERSONAL_ACCESS_TOKEN

# OpenAI configuration
openai_api_key = config.OPENAI_API_KEY
proxy_url = config.OPENAI_PROXY_URL
model = config.MODEL
temperature = config.TEMPERATURE

# Initialize OpenAI client with or without proxy
client = OpenAI(api_key=openai_api_key) if proxy_url is None or proxy_url == "" else OpenAI(http_client=httpx.Client(proxy=proxy_url))


def load_labels(lang="he"):
    path = os.path.join("languages", f"lang_{lang}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# Function to read an image and return its base64 representation
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Convert background image to base64
bg_image_base64 = get_base64_of_image("streamlit_agent\\background.jpg")

# Apply custom CSS styles to the Streamlit app
def apply_direction_css(lang: str, bg_image_base64: str):
    css = f"""
    <style>
    /* Make the language selectbox in the sidebar smaller */
    [data-testid="stSidebar"] .stSelectbox {{
        margin-top: 0.25rem;
        margin-bottom: 0.25rem;
        font-size: 0.50rem;
        width: 100px;
    }}

    [data-testid="stSidebar"] .stSelectbox div[data-testid="stSelectbox"] {{
        padding-top: 0.25rem;
        padding-bottom: 0.25rem;
    }}

    [data-testid="stSidebar"] .stSelectbox label {{
        display: none;
    }}

    /* Set background image for main app page */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Semi-transparent white background for content */
    .main > div {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 10px;
    }}
    """

    # Add RTL only if Hebrew
    if lang == "he":
        css += """
        /* Right-to-left layout direction */
        .reportview-container, .main, [data-testid="stVerticalBlock"] {
            direction: rtl;
            text-align: right;
        }

        .sidebar .sidebar-content {
            direction: rtl;
            text-align: right;
        }

        /* Move sidebar to the right */
        [data-testid="stSidebar"] {
            float: right;
            border-left: 1px solid #ddd;
            border-right: none;
        }
        """

    css += """
    /* Sidebar buttons */
    [data-testid="stSidebar"] div.stButton button {
        background-color: white;
        width: 220px;
    }
    </style>
    """

    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    # Removing the streamlit debug line. If you are working on the code, set this line to 'False'
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Get list of all projects from Azure DevOps
all_projects = streamlit_agent.utils.get_projects(organization, personal_access_token)


# Function to render the main task generation UI
def show_generate_tasks_page():
    st.title(labels["app_title"])
    st.write(labels["instructions_text"])

    # Project selection
    selected_project = st.selectbox(labels["select_project"], all_projects, key="project_selectbox")

    # Get features from the selected project
    features = streamlit_agent.utils.get_work_items_by_type(
        organization, selected_project, personal_access_token,
        work_item_type="Feature", area_path=f"{selected_project}"
    )

    # Extract feature titles
    titles = [feature["title"] for feature in features]

    if selected_project:
        selected_feature_title = st.selectbox(labels["select_feature"], titles, key="feature_selectbox")

    # Get the selected feature details
    selected_feature = next((item for item in features if item["title"] == selected_feature_title), None)

    if selected_feature is not None:
        if selected_feature:
            feature_id = selected_feature["id"]
            feature_description = selected_feature["description"]

        # Convert HTML text to plain text
        plain_description = streamlit_agent.utils.extract_plain_text(feature_description)

        # Display the description in a disabled text area
        if feature_description:
            st.text_area(labels["feature_description"], value=plain_description, disabled=True, height=200)

        # Generate sub-tasks when the button is clicked
        if feature_id and feature_description:
            if st.button(labels["generate_subtasks"]):
                # Load the prompt from a file
                prompt = streamlit_agent.utils.prompt_text('prompt.txt')
                selected_lang = lang_map[lang_choice]
                
                if selected_lang == "he":
                    prompt = prompt + "You must respond **only in Hebrew**."
                else:
                    prompt = prompt + "You must respond **only in English**."

                # Generate tasks using OpenAI
                tasks = streamlit_agent.utils.request_to_openai(client, prompt, feature_description, model, temperature)

                # Create tasks in TFS under the selected feature
                streamlit_agent.utils.create_work_items_in_tfs(
                    organization, selected_project, personal_access_token, work_item_type = "Product Backlog Item", work_items = tasks, feature_id = feature_id
                )
                st.success(labels[f"success_message_tasks"])


# Function to render the feature creation page
def show_feature_builder_page():

    st.title(labels["create_feature_title"])

    selected_project = st.selectbox(labels["select_project"], all_projects, key="project_selectbox")
    if selected_project:

        feature_title = st.text_input(labels["feature_title_input"])
        feature_description = st.text_area(labels["feature_description"])


        col1, col2 = st.columns(2)

        with col1:
            feature_effort = st.number_input(labels["select_effort"], 
            min_value=1, 
            max_value=99, 
            step=1, 
            format="%d", # Displays whole numbers only
            key="effort")

        with col2:
            feature_priority = st.number_input(labels["select_priority"], 
            min_value=1, 
            max_value=4, 
            step=1, 
            format="%d", # Displays whole numbers only
            key="priority")


        work_items = []
        work_items.append({ "title": feature_title, "description": feature_description , "effort": feature_effort, "priority": feature_priority})


        if st.button(labels["generate"]):
            if feature_title == "":
                st.error(labels["error_message"])
            else:
                # Create new feature
                streamlit_agent.utils.create_work_items_in_tfs(
                    organization, selected_project, personal_access_token, work_item_type = "Feature", work_items= work_items
                )
                st.success(labels[f"success_message_feature"])




# Set default page on first load
if "page" not in st.session_state:
    st.session_state.page = "Generate Tasks"


lang_map = {"IL": "he", "EN": "en"}
lang_choice = st.sidebar.selectbox(" ", options=list(lang_map.keys()), index=0)
lang = lang_map[lang_choice]
labels = load_labels(lang)

apply_direction_css(lang, bg_image_base64)

# Sidebar navigation menu
st.sidebar.title(labels["sidebar_title"])
if st.sidebar.button(labels["nav_create_tasks"]):
    st.session_state.page = "Generate Tasks"
if st.sidebar.button(labels["nav_create_features"]):
    st.session_state.page = "Feature Builder"


# Show the selected page
if st.session_state.page == "Generate Tasks":
    show_generate_tasks_page()
elif st.session_state.page == "Feature Builder":
    show_feature_builder_page()

