import streamlit as st
from scrape import (
    scrape_website,
    scrape_ranch,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
import json
from parse import parse_with_ollama

# Streamlit UI
st.title("Rahmat Wibowo's AI Web Scraper")
url = st.text_input("Enter Website URL", value="https://shorthorn.digitalbeef.com/")
name = st.text_input("Enter Ranch Name")
city = st.text_input("Enter Ranch City")
location = st.text_input("Enter Ranch Member Location")
# url = "https://www.amgr.org/frm_directorySearch.cfm"
# Step 1: Scrape the Website
if st.button("Scrape Website"):
    if url:
        st.write("Scraping the website...")

        # Scrape the website
        dom_content = scrape_ranch(url,name,city,location)
        body_content = extract_body_content(dom_content)
        cleaned_content = clean_body_content(body_content)

        # Store the DOM content in Streamlit session state
        st.session_state.dom_content = cleaned_content

        # Display the DOM content in an expandable text box
        with st.expander("View DOM Content"):
            st.text_area("DOM Content", cleaned_content, height=300)


# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = """Please make a json file containing all the results of the search with format
    {
    "headers": [
        "Action",
        "State",
        "Name",
        "Farm",
        "Phone",
        "Website",
    ],
    "data": [
        [
        "View",
        "Joy Hurlburt",
        "Range Ready Savanna - Hulburt Ranch ltd - RRS",
        "(403) 330-5399",
        ""
        ]
    ]
}"""

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")

            # Parse the content with Ollama
            dom_chunks = split_dom_content(st.session_state.dom_content)
            parsed_result = parse_with_ollama(dom_chunks, parse_description)

            st.write(parsed_result)
