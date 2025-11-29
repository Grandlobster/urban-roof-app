import streamlit as st
import numpy as np
from PIL import Image
from inference_sdk import InferenceHTTPClient
import os
import tempfile

# Page configuration
st.set_page_config(
    page_title="Urban Roof - Wall Defect Identifier",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for sleek, modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-attachment: fixed;
    }
    
    /* Floating particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(126, 34, 206, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(42, 82, 152, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    .main > div {
        padding-top: 3rem;
        position: relative;
        z-index: 1;
    }
    
    /* Hero Title */
    .hero-section {
        text-align: center;
        margin-bottom: 4rem;
        animation: fadeInDown 1s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-title {
        font-size: 5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -3px;
        text-shadow: 0 0 80px rgba(255, 215, 0, 0.3);
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.3rem;
        margin-top: 1rem;
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    /* Main Form Container */
    .form-wrapper {
        max-width: 600px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Sleek Form Card */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 3rem;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Input Fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        color: white !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border: 1px solid rgba(255, 215, 0, 0.5) !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Labels */
    .stNumberInput label,
    .stSelectbox label,
    .stFileUploader label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: 0.5px !important;
    }
    
    /* File Uploader Styling */
    .stFileUploader > div {
        border: 2px dashed rgba(255, 215, 0, 0.3) !important;
        border-radius: 20px !important;
        background: rgba(255, 215, 0, 0.02) !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div:hover {
        border-color: rgba(255, 215, 0, 0.6) !important;
        background: rgba(255, 215, 0, 0.05) !important;
        transform: scale(1.01);
    }
    
    /* Uploaded Image */
    [data-testid="stImage"] {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        margin: 1.5rem 0;
    }
    
    /* Submit Button */
    .stButton > button {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #0f0c29;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 1.2rem 3rem;
        border-radius: 50px;
        border: none;
        box-shadow: 
            0 10px 30px rgba(255, 215, 0, 0.4),
            0 0 60px rgba(255, 215, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        margin-top: 2rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(255, 215, 0, 0.6),
            0 0 80px rgba(255, 215, 0, 0.3);
        background: linear-gradient(135deg, #ffed4e 0%, #ffd700 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(1.01);
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 1rem 1.5rem !important;
        margin: 1.5rem 0 !important;
    }
    
    /* JSON Results */
    [data-testid="stJson"] {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 215, 0, 0.2) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-top: 2rem !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #ffd700 !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Disclaimer */
    .disclaimer {
        max-width: 800px;
        margin: 4rem auto 2rem;
        padding: 2rem;
        background: rgba(255, 193, 7, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 20px;
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.8;
    }
    
    .disclaimer strong {
        color: #ffd700;
    }
    
    /* Selectbox dropdown */
    [data-baseweb="select"] > div {
        background: rgba(15, 12, 41, 0.95) !important;
        border-color: rgba(255, 215, 0, 0.3) !important;
    }
    
    [data-baseweb="select"] li {
        background: transparent !important;
        color: white !important;
    }
    
    [data-baseweb="select"] li:hover {
        background: rgba(255, 215, 0, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the client
@st.cache_resource
def get_client():
    return InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="iyPThwgorhL35k1j1t76"
    )

CLIENT = get_client()

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">URBAN ROOF</h1>
    <p class="hero-subtitle">WALL DEFECT DETECTION SYSTEM</p>
</div>
""", unsafe_allow_html=True)

# Center the form
st.markdown('<div class="form-wrapper">', unsafe_allow_html=True)

# Form inputs
wall_age = st.number_input(
    "Wall Age (Years)",
    min_value=0,
    max_value=100,
    value=5,
    help="Enter the approximate age of the wall"
)

uploaded_image = st.file_uploader(
    "Upload Wall Image",
    type=['jpg', 'jpeg', 'png'],
    help="Choose a clear image of the wall for analysis"
)

if uploaded_image:
    st.image(uploaded_image, use_container_width=True)

wall_wet = st.selectbox(
    "Moisture or Dampness Present?",
    ["No", "Yes"]
)

water_fixing = st.selectbox(
    "Previous Dampguard Application?",
    ["No", "Yes"]
)

submit_button = st.button("Analyze Wall Condition")

# Process submission
if submit_button and uploaded_image:
    with st.spinner("Analyzing your wall image..."):
        # Convert uploaded file to image
        image = Image.open(uploaded_image)
        
        # Save temporarily for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image.save(tmp_file.name)
            temp_path = tmp_file.name
        
        # Perform inference
        try:
            result = CLIENT.infer(temp_path, model_id="urabn-roof/1")
            
            st.success("Analysis Complete")
            st.markdown("### Detection Results")
            st.json(result)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
elif submit_button:
    st.warning("Please upload an image before analyzing")

st.markdown('</div>', unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <strong>Important Notice:</strong> The model predictions are generated by AI and may not be 100% accurate. 
    For a definitive assessment, an in-person inspection by a qualified technician is recommended.
</div>
""", unsafe_allow_html=True)
