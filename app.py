import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os


def main():
    st.title("Narrato")
    st.subheader("Create your own story")

    container = st.empty()
    with open("intro.txt") as f:
        intro_text = f.read()

    container.markdown(intro_text)

    # Load API key from .env file
    load_dotenv()
    default_api_key = os.getenv("OPENAI_API_KEY")

    # Sidebar for OpenAI API key input and character input form
    st.sidebar.subheader("Input")
    story_theme = st.sidebar.text_input("Enter the story theme")

    with st.sidebar.form(key="character_form"):
        character_name = st.text_input("Character Name")
        character_description = st.text_area("Character Description")
        add_character = st.form_submit_button(label="Add Character")

        if add_character and character_name and character_description:
            st.session_state["characters"].append(
                {"Name": character_name, "Description": character_description}
            )

    # Initialize session state to keep track of characters
    if "characters" not in st.session_state:
        st.session_state["characters"] = []

    # Display characters
    if st.session_state["characters"]:
        st.sidebar.subheader("Characters")
        characters_df = pd.DataFrame(st.session_state["characters"])
        st.sidebar.table(characters_df)
        
    # Add a button to clear characters
    if st.sidebar.button("Clear Characters"):
        st.session_state["characters"] = []
        st.sidebar.success("All characters have been cleared.")

    # Generate Story button
    openai_api_key = st.sidebar.text_input(
        "Enter OpenAI API Key (if i'm out of funds)", type="password"
    )

    if st.sidebar.button("Generate Story"):
        if not openai_api_key:
            st.sidebar.error("Please enter your OpenAI API Key")
        else:
            # Prepare the prompt
            character_details = "\n".join(
                [
                    f"{c['Name']}: {c['Description']}"
                    for c in st.session_state["characters"]
                ]
            )
            system_instructions = (
                "You are a creative and imaginative story writer. Your task is to create an engaging and captivating story"
                "based on the provided theme and characters. Use vivid descriptions and emotional depth to bring the story to life. use markdown format for title and text"
            )

            messages = [
                {"role": "system", "content": system_instructions},
                {
                    "role": "user",
                    "content": f"Theme: {story_theme}\n\nCharacters:\n{character_details}",
                },
            ]

            # Call OpenAI API with streaming
            client = OpenAI(api_key=openai_api_key)
            stream = client.chat.completions.create(
                model="gpt-4o", messages=messages, stream=True, max_tokens=4096
            )

            # Display the story in the center
            streamed_text = ""
            for chunk in stream:
                chunk_content = chunk.choices[0].delta.content
                if chunk_content is not None:
                    streamed_text = streamed_text + chunk_content
                    container.markdown(streamed_text)


if __name__ == "__main__":
    main()
