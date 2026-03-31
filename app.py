import streamlit as st
import numpy as np
from PIL import Image
import os
import tempfile
import requests
import base64
import json

# Page configuration
st.set_page_config(
    page_title="Urban Roof - Wall Defect Identifier",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ... (keep all your CSS exactly the same) ...

API_KEY = "iyPThwgorhL35k1j1t76"
MODEL_ID = "urabn-roof/1"

def run_inference(image_path):
    """Call Roboflow API directly without inference_sdk"""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    url = f"https://detect.roboflow.com/{MODEL_ID}?api_key={API_KEY}"
    
    response = requests.post(
        url,
        data=image_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()

# ... (keep all your hero section, form, and disclaimer HTML the same) ...

# Only change the inference call section:
if submit_button and uploaded_image:
    with st.spinner("Analyzing your wall image..."):
        image = Image.open(uploaded_image)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image.save(tmp_file.name, format='JPEG')
            temp_path = tmp_file.name
        
        try:
            result = run_inference(temp_path)  # ← replaces CLIENT.infer(...)
            
            st.success("Analysis Complete")
            st.markdown("### Detection Results")
            st.json(result)
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
elif submit_button:
    st.warning("Please upload an image before analyzing")
