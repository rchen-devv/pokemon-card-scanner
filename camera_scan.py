import cv2
import pytesseract
import numpy as np
import requests
from PIL import Image

# Configuration
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows only (comment out on Mac/Linux)
API_KEY = "YOUR API KEY"  # Replace with your actual API key

def capture_card():
    """Capture image from webcam and save as 'pokemon_card.jpg'"""
    cap = cv2.VideoCapture(0)
    
    print("Press 'S' to scan card, 'Q' to quit...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        cv2.imshow("Pokémon Card Scanner", frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return None
        elif key == ord('s'):
            cv2.imwrite("pokemon_card.jpg", frame)
            cap.release()
            cv2.destroyAllWindows()
            return "pokemon_card.jpg"

def preprocess_image(image_path):
    """Enhance image for better OCR results"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

def extract_card_name(image_path):
    """Extract text from card image using OCR"""
    # Set Tesseract path (Windows only)
    if TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img)
    
    # Get the most likely card name (first non-empty line)
    for line in text.split('\n'):
        if line.strip():
            return line.strip()
    return "Unknown"

def get_card_price(card_name):
    """Fetch card price from Pokémon TCG API"""
    url = f"https://api.pokemontcg.io/v2/cards?q=name:{card_name}"
    headers = {"X-Api-Key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data['data']:
            card = data['data'][0]  # Get first matching card
            prices = card.get('cardmarket', {}).get('prices', {})
            return {
                'name': card['name'],
                'set': card['set']['name'],
                'avg_price': prices.get('averageSellPrice', 'N/A'),
                'trend_price': prices.get('trendPrice', 'N/A')
            }
        return None
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

def main():
    # Step 1: Capture card image
    image_path = capture_card()
    if not image_path:
        return
    
    # Step 2: Extract card name
    card_name = extract_card_name(image_path)
    print(f"\nDetected Card: {card_name}")
    
    # Step 3: Get price data
    price_data = get_card_price(card_name)
    
    if price_data:
        print("\n=== Card Details ===")
        print(f"Name: {price_data['name']}")
        print(f"Set: {price_data['set']}")
        print(f"Average Price: ${price_data['avg_price']}")
        print(f"Trend Price: ${price_data['trend_price']}")
