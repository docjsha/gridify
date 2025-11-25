import streamlit as st
import requests
import math
from urllib.parse import urlparse

# Set page configuration to wide mode for a "large grid" feel
st.set_page_config(page_title="Shopify Image Grid", layout="wide")

def fetch_shopify_products(base_url):
    """
    Fetches products from a Shopify store's public JSON API.
    Handles basic URL formatting and error checking.
    """
    # Ensure URL ends with /products.json
    clean_url = base_url.rstrip('/')
    if not clean_url.endswith('products.json?limit=1000'):
        api_url = f"{clean_url}/products.json?limit=1000"
    else:
        api_url = clean_url

    # Add a limit param to get more products (max is usually 250)
    params = {'limit': 250}
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('products', [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []
    except ValueError:
        st.error("Invalid JSON response. Is this a Shopify site?")
        return []

def extract_images(products, base_url):
    """
    Extracts all image URLs from a list of products.
    Returns a list of tuples (image_url, product_title, product_url).
    """
    images = []
    for product in products:
        title = product.get('title', 'Unknown Product')
        handle = product.get('handle', '')
        product_url = f"{base_url}/products/{handle}"
        
        # Shopify products can have multiple images
        product_images = product.get('images', [])
        
        # Only take the first image if available
        if product_images:
            first_img = product_images[0]
            src = first_img.get('src')
            if src:
                images.append((src, title, product_url))
    return images

def clean_shopify_url(url):
    """
    Cleans the input URL by ensuring it has a scheme and removing path/query params.
    """
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    # Return only the scheme and netloc (domain)
    return f"{parsed.scheme}://{parsed.netloc}"
# --- UI ---

st.title("🛍️ Gridify")
st.markdown("Enter a Shopify store URL to visualize its product inventory.")

url_input = st.text_input("Shopify Store URL", placeholder="")

if url_input:
    # Clean the URL input
    cleaned_url = clean_shopify_url(url_input)
    
    with st.spinner(f"Fetching inventory from {cleaned_url} ..."):
        products = fetch_shopify_products(cleaned_url)
        
        if products:
            image_data = extract_images(products, cleaned_url)
            st.success(f"Found {len(products)} products.")
            
            # Grid Layout Settings
            # Let user choose columns or default to a responsive number
            cols_count = st.slider("Grid Columns", min_value=2, max_value=8, value=5)
            
            # Display images in a grid
            # We iterate through the images and place them in columns
            rows = math.ceil(len(image_data) / cols_count)
            
            for i in range(0, len(image_data), cols_count):
                cols = st.columns(cols_count)
                batch = image_data[i:i+cols_count]
                
                for idx, (img_url, title, product_url) in enumerate(batch):
                    with cols[idx]:
                          # Render clickable image with title directly below with no extra spacing
                        st.markdown(
                            f'<div style="text-align:center; margin:0; padding:0; font-size:0.9rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{title}">{title}</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<a href="{product_url}" target="_blank"><img src="{img_url}" style="width:100%; border-radius:6px;"></a>',
                            unsafe_allow_html=True,
                        )
        else:
            if url_input: # Only show warning if they tried to search
                st.warning("No products found. Ensure the URL is correct and the site is built on Shopify.")

# Footer / Style tweaks
st.markdown("""
<style>
    /* Simple CSS to make images look a bit cleaner if needed */
    img {
        border-radius: 8px;
        transition: transform 0.2s;
    }
    img:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)
