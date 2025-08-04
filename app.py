import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get the Google Gemini LLM response
def get_gemini_response(input_prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt)
    return response.text

# Function to extract text from uploaded PDF resume
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Function to clean the response and ensure it's valid JSON
def clean_response(response):
    json_pattern = r'({.*})'
    match = re.search(json_pattern, response, re.DOTALL)
    if match:
        cleaned_response = match.group(1)
        return cleaned_response
    else:
        return None

# Prompt template for resume extraction
input_prompt_template = """
Hey, act like a highly experienced ATS (Application Tracking System) with deep knowledge of various fields such as technology, finance, healthcare, engineering, science, education, law, and other professions. Your task is to evaluate the resume and extract data into the following structure:

- Personal Information (name, email, contact number, etc.)
- Professional Summary
- Professional Experience
- All Skills from the resume.

Resume: {resume_text}

I want the response **only in JSON format** with the following structure:
{{
  "Personal Information": {{}} ,
  "Professional Summary": "",
  "Professional Experience": [],
  "All Skills": []
}}
"""

# Prompt template for ATS matching
input_prompt_ats = """
Hey, act like a highly experienced ATS (Application Tracking System) with deep knowledge of various fields such as technology, finance, healthcare, engineering, science, education, law, and other professions. Your task is to evaluate the resume based on the given job description. You must consider the job market is very competitive across multiple industries, and you should provide the best assistance for improving resumes. Assign the percentage matching based on JD and identify the missing keywords with high accuracy.

Resume: {text}
Description: {jd}

I want the response **only in JSON format** with the following structure:
{{
  "JD Match":"%",
  "Missing Keywords":[],
  "Resume Improvement Suggestions":""
}}
"""

# Streamlit app UI with background and logo
# Apply a custom background color and add a logo at the top of the page
st.markdown("""
    <style>
    body {
        background-color: #f0f4f8;
    }
    .stButton button {
        background-color: #007BFF;
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
    }
    .stTextInput textarea, .stTextInput input {
        border-radius: 10px;
        padding: 10px;
    }
    .stFileUploader div {
        border-radius: 10px;
        padding: 10px;
    }
    .sidebar .sidebar-content {
        background-color: #e0ebeb;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Insert the logo and title at the top
col1, col2 = st.columns([1, 9])  # Adjust the column ratio as needed
with col1:
    st.image(r"C:\Users\RK\Desktop\Panzer_Task\Images\logo.jpg", width=50)  # Smaller logo

with col2:
    st.markdown("""
        <h1 style='font-size: 36px; font-weight: bold; color: #000040;'>LLM Powered Resume Data Extraction and Smart ATS System</h1>
         <p style='font-size: 18px; color: #333;'>The LLM Powered Resume Data Extraction and Smart ATS System tool, powered by Gemini Pro LLM, automates resume data extraction and ATS evaluation. It leverages advanced Gen AI to accurately extract relevant information and match candidates information to job descriptions. This tool streamlines the hiring process, saving time and enhancing efficiency for recruiters and candidates alike.</p>
        """, unsafe_allow_html=True)

# Add a sidebar for navigation
st.sidebar.header("Navigation")
options = st.sidebar.radio("Select a feature:", ("Resume Data Extraction", "ATS Matching"))

# File uploader (common for both features)
uploaded_file = st.file_uploader("Upload Your Resume (PDF only)", type="pdf", help="Upload resume in PDF format.")

# Section for resume extraction
if options == "Resume Data Extraction":
    st.subheader("Resume Data Extraction")
    st.markdown("<p style='font-size: 18px;'>Upload a resume to extract personal information, professional experience, and skills using AI.</p>", unsafe_allow_html=True)
    if uploaded_file:
        if st.button("Extract Resume Data"):
            resume_text = input_pdf_text(uploaded_file)
            input_prompt = input_prompt_template.format(resume_text=resume_text)
            response = get_gemini_response(input_prompt)
            cleaned_response = clean_response(response)
            
            if cleaned_response:
                try:
                    structured_data = json.loads(cleaned_response)

                    st.markdown("<h3 style='color: #f39c12;'>Personal Information</h3>", unsafe_allow_html=True)
                    st.json(structured_data["Personal Information"])

                    st.markdown("<h3 style='color: #f39c12;'>Professional Summary</h3>", unsafe_allow_html=True)
                    st.write(structured_data["Professional Summary"])

                    st.markdown("<h3 style='color: #f39c12;'>Professional Experience</h3>", unsafe_allow_html=True)
                    st.json(structured_data["Professional Experience"])

                    st.markdown("<h3 style='color: #f39c12;'>All Skills</h3>", unsafe_allow_html=True)
                    st.json(structured_data["All Skills"])

                except json.JSONDecodeError:
                    st.error("Error parsing the response. The model did not return valid JSON.")
            else:
                st.error("Failed to extract valid JSON from the response. Please try again.")
    else:
        st.warning("Please upload a resume first.")

# Section for ATS functionality
if options == "ATS Matching":
    st.subheader("Smart ATS System")
    st.markdown("<p style='font-size: 18px;'>Evaluate your resume against a job description for better keyword matching and suggestions.</p>", unsafe_allow_html=True)
    jd = st.text_area("Paste the Job Description", placeholder="Copy and paste the job description here...")
    if uploaded_file:
        if st.button("Evaluate Resume Against Job Description"):
            text = input_pdf_text(uploaded_file)
            input_prompt_ats_formatted = input_prompt_ats.format(text=text, jd=jd)
            response_ats = get_gemini_response(input_prompt_ats_formatted)
            
            st.markdown("<h3 style='color: #f39c12;'>ATS Evaluation Result</h3>", unsafe_allow_html=True)
            st.text(response_ats)
    else:
        st.warning("Please upload a resume first.")
