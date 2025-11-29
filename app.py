import streamlit as st
import cv2
import numpy as np
from PIL import Image
from inference_sdk import InferenceHTTPClient
import os

# Page configuration
st.set_page_config(
    page_title="Urban Roof - Wall Defect Identifier",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern glassmorphism design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Glassmorphism Header */
    .glass-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin-bottom: 3rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 0;
        letter-spacing: -2px;
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.4rem;
        text-align: center;
        margin-top: 1rem;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* Glass Card for Form */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ffd700, #7e22ce, #2a5298);
    }
    
    /* Info Cards with Glass Effect */
    .info-glass {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .info-glass:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }
    
    .info-title {
        color: #ffd700;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        letter-spacing: 0.5px;
    }
    
    .info-text {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Service Items */
    .service-item {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
        border-left: 3px solid #ffd700;
    }
    
    .service-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(10px);
        border-left: 3px solid #ffed4e;
    }
    
    /* Form Labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stFileUploader label {
        color: #1e3c72 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Warning Box */
    .warning-glass {
        background: rgba(255, 193, 7, 0.15);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 193, 7, 0.5);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        color: white;
    }
    
    .warning-glass h4 {
        color: #ffd700;
        margin-top: 0;
        font-size: 1.3rem;
    }
    
    /* Footer */
    .glass-footer {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        margin-top: 3rem;
        text-align: center;
        color: white;
    }
    
    .footer-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        color: #ffd700;
    }
    
    .footer-link {
        color: #ffd700;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .footer-link:hover {
        color: #ffed4e;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #1e3c72;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 1rem 3rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(255, 215, 0, 0.6);
        background: linear-gradient(135deg, #ffed4e 0%, #ffd700 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Section Title */
    .section-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        text-align: center;
    }
    
    /* Card Title */
    .card-title {
        color: #1e3c72;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 2rem 0;
        text-align: center;
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

# Header with glassmorphism
st.markdown("""
<div class="glass-header">
    <h1 class="main-title">URBAN ROOF</h1>
    <p class="subtitle">Advanced Wall Defect Detection System</p>
</div>
""", unsafe_allow_html=True)

# Two column layout
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">Wall Inspection Form</h2>', unsafe_allow_html=True)
    
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
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    
    wall_wet = st.selectbox(
        "Moisture or Dampness Present?",
        ["No", "Yes"],
        help="Select if you notice any moisture issues"
    )
    
    water_fixing = st.selectbox(
        "Previous Dampguard Application?",
        ["No", "Yes"],
        help="Has any waterproofing treatment been done previously?"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.button("Analyze Wall Condition")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process submission
    if submit_button and uploaded_image:
        with st.spinner("Analyzing your wall image..."):
            # Convert uploaded file to image
            image = Image.open(uploaded_image)
            image_np = np.array(image)
            
            # Save temporarily for processing
            temp_path = "temp_image.jpg"
            cv2.imwrite(temp_path, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
            
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

with col2:
    # About Urban Roof
    st.markdown("""
    <div class="info-glass">
        <h3 class="info-title">About Urban Roof</h3>
        <p class="info-text">Specialists in comprehensive waterproofing solutions, home inspection services, interior and exterior painting, and repair and restoration services across major Indian cities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Service areas
    st.markdown("""
    <div class="info-glass">
        <h3 class="info-title">Service Locations</h3>
        <p class="info-text">Pune  •  Bangalore  •  Hyderabad  •  Chennai  •  Mumbai</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Experience
    st.markdown("""
    <div class="info-glass">
        <h3 class="info-title">7+ Years of Excellence</h3>
        <p class="info-text">Trusted by thousands of homeowners across India for quality waterproofing and home improvement solutions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Services offered
    st.markdown('<h3 class="section-title">Our Services</h3>', unsafe_allow_html=True)
    
    services = [
        "Comprehensive Roof Inspections",
        "Interior and Exterior Painting",
        "Leak Detection and Seepage Solutions",
        "Precision Repairs and Restoration",
        "Complete Roof Replacements",
        "Interior Design and Furnishing",
        "Waterproofing Solutions",
        "Civil Works and Construction"
    ]
    
    for service in services:
        st.markdown(f'<div class="service-item">{service}</div>', unsafe_allow_html=True)

# Warning box
st.markdown("""
<div class="warning-glass">
    <h4>Important Disclaimer</h4>
    <p><strong>The model predictions are generated by artificial intelligence and may not be 100% accurate.</strong></p>
    <p>For a definitive assessment and professional recommendations, an in-person inspection by our qualified technicians is highly recommended.</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="glass-footer">
    <h3 class="footer-title">URBAN ROOF</h3>
    <p style="font-size: 1.1rem; margin: 1rem 0;">Your Trusted Waterproofing and Home Improvement Partner</p>
    <p style="margin: 1rem 0;">Creating beautiful, durable, and low-maintenance living spaces</p>
    <p><a href="https://urbanroof.in/" target="_blank" class="footer-link">Visit urbanroof.in</a></p>
</div>
""", unsafe_allow_html=True)