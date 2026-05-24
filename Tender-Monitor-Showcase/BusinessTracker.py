import requests
from bs4 import BeautifulSoup
import time
import json
import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# ====== CONFIGURATION ======

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token_here")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id_here")
BASE_URL = "https://www.xmu.edu.my"
URL = BASE_URL + "/tender-notice"
CHECK_INTERVAL = 10 
DATA_FILE = "sent_tenders.json"
# ===========================


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tender_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"{text}\n🕐 {timestamp}"
    
    data = {
        "chat_id": CHAT_ID,
        "text": formatted_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def fetch_tenders():
    """
    Fetch tenders from XMUM website with improved parsing.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        logger.info(f"Fetching tenders from {URL}")
        response = requests.get(URL, headers=headers, timeout=15)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"❌ Failed to fetch tenders. Status: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tenders = []
        
        tender_cards = soup.select('.tender-card, .views-row article, .node--type-tender')
        
        if not tender_cards:
            tender_cards = soup.select('div[class*="tender"], div[class*="views-row"]')
        
        logger.info(f"Found {len(tender_cards)} potential tender cards")
        
        for i, card in enumerate(tender_cards):
            try:
                title_link = None
                selectors = [
                    'h5 a', 'h4 a', 'h3 a', 'h2 a', 
                    '.title a', '.field--name-title a',  
                    'a[href*="tender"]',  
                    'a[href^="/tender-notice/"]',  
                ]
                
                for selector in selectors:
                    link_tag = card.select_one(selector)
                    if link_tag and link_tag.get('href'):
                        title_link = link_tag
                        break
                
                if not title_link:
                    all_links = card.find_all('a', href=True)
                    if all_links:
                        title_link = all_links[0]
                
                if not title_link:
                    logger.debug(f"No link found in card {i+1}")
                    continue
                
                link = title_link.get('href', '').strip()
                if not link:
                    continue
                
                if link.startswith('/'):
                    link = BASE_URL + link
                elif not link.startswith(('http://', 'https://')):
                    link = BASE_URL + '/' + link
                
                title = title_link.get_text(strip=True)
                if not title:
                    title = "Tender Notice"

                tender_info = {
                    "title": title,
                    "link": link,
                    "tender_number": None,
                    "closing_date": None,
                    "description": None,
                    "published_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                text_content = card.get_text(" ", strip=True)

                name_label = card.find("strong", string=lambda s: s and "Tender Name" in s)
                if name_label:

                    name_value = name_label.next_sibling
                    if name_value and isinstance(name_value, str) and name_value.strip():
                        tender_info["tender_name"] = name_value.strip()
                    else:

                        p = name_label.parent
                        full_text = p.get_text(" ", strip=True)

                        tender_info["tender_name"] = full_text.replace("Tender Name:", "").strip()

                number_label = card.find("strong", string=lambda s: s and "Tender Number" in s)
                if number_label:
                    number_value = number_label.next_sibling
                    if number_value and isinstance(number_value, str) and number_value.strip():
                        tender_info["tender_number"] = number_value.strip()
                    else:
                        p = number_label.parent
                        full_text = p.get_text(" ", strip=True)

                        tender_info["tender_number"] = full_text.replace("Tender Number:", "").strip()

                closing_label = card.find("strong", string=lambda s: s and "Closing Date" in s)
                if closing_label:
                    p = closing_label.parent

                    time_tag = p.find("time")
                    if time_tag:

                        display_text = time_tag.get_text(" ", strip=True)
                        tender_info["closing_date"] = display_text
                    else:
                        full_text = p.get_text(" ", strip=True)
                        tender_info["closing_date"] = full_text.replace("Closing Date:", "").strip()


                paragraphs = card.find_all(['p', 'div'])
                desc_parts = []
                for p in paragraphs[:3]:
                    text = p.get_text(strip=True)
                    if text and len(text) > 10: 
                        desc_parts.append(text)
                
                if desc_parts:
                    tender_info["description"] = " | ".join(desc_parts[:100]) 
                
                logger.info(f"  Found tender: {title[:50]}...")
                tenders.append(tender_info)
                
            except Exception as e:
                logger.warning(f"Error processing card {i+1}: {e}")
                continue
        
        logger.info(f"✅ Successfully fetched {len(tenders)} tenders")
        return tenders
        
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return []

def load_sent_tenders():
    """Load previously sent tenders from storage file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} sent tenders from {DATA_FILE}")
                return data
        except Exception as e:
            logger.error(f"Error loading sent tenders: {e}")
            return []
    logger.info("No existing sent tenders file found")
    return []

def save_sent_tenders(tenders):
    """Save sent tenders to prevent duplicates."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tenders, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(tenders)} tenders to {DATA_FILE}")
    except Exception as e:
        logger.error(f"Error saving sent tenders: {e}")

def format_tender_message(header, tender):
    parts = []
    parts.append(f"<b>{header}</b>")
    
    if tender.get("title"):
        parts.append(f"📌 <b>{tender['title']}</b>")
    
    if tender.get("tender_name"):
        parts.append(f"📄 <b>Tender Name:</b> {tender['tender_name']}")

    if tender.get("tender_number"):
        parts.append(f"🔢 <b>Tender Number:</b> {tender['tender_number']}")
    
    if tender.get("closing_date"):
        parts.append(f"⏰ <b>Closing Date:</b> {tender['closing_date']}")
    
    if tender.get("link"):
        parts.append(f"🔗 {tender['link']}")
    

    return "\n".join(parts)

def check_config():

    errors = []
    
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        errors.append("BOT_TOKEN not set. Please set TELEGRAM_BOT_TOKEN environment variable")
    
    if not CHAT_ID or CHAT_ID == "your_chat_id_here":
        errors.append("CHAT_ID not set. Please set TELEGRAM_CHAT_ID environment variable")
    
    if errors:
        logger.error("\n❌ CONFIGURATION ERRORS:")
        for error in errors:
            logger.error(f"  - {error}")
        
        logger.info("\n📝 SETUP INSTRUCTIONS:")
        logger.info("1. Create a bot with @BotFather on Telegram")
        logger.info("2. Get your bot token")
        logger.info("3. Find your chat ID (send message to @userinfobot)")
        logger.info("4. Set environment variables:")
        logger.info("   export TELEGRAM_BOT_TOKEN='your_token'")
        logger.info("   export TELEGRAM_CHAT_ID='your_chat_id'")
        logger.info("5. Or create a .env file with these variables")
        
        return False
    
    logger.info("✅ Configuration check passed")
    return True

def main():
    logger.info("🚀 XMUM Tender Monitor Started")
    sent_tenders = load_sent_tenders()
    sent_links = [t.get("link") for t in sent_tenders if t.get("link")]
    
    logger.info("Performing initial check...")
    tenders = fetch_tenders()
    
    if not tenders:
        logger.warning("⚠️ No tenders found on initial check")
        startup_msg = (
            "📊 <b>XMUM Tender Monitor Started</b>\n"
            "No tenders found on initial check.\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_telegram_message(startup_msg)
    else:
        logger.info(f"Found {len(tenders)} tenders initially")
        
        latest = tenders[0]
        message = format_tender_message("📢 Latest Tender (Initial Check)", latest)
        
        if send_telegram_message(message):
            if latest.get("link") not in sent_links:
                sent_tenders.append(latest)
                sent_links.append(latest.get("link"))
            save_sent_tenders(sent_tenders)
            logger.info("✅ Initial tender sent")
    
    check_count = 1
    while True:
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            tenders = fetch_tenders()
            if not tenders:
                logger.warning("No tenders found in this check")
                time.sleep(CHECK_INTERVAL)
                check_count += 1
                continue
            
            new_tenders = []
            for tender in tenders:
                tender_link = tender.get("link")
                if tender_link and tender_link not in sent_links:
                    new_tenders.append(tender)
                    logger.info(f"New tender found: {tender.get('title', 'Untitled')[:50]}...")

            if new_tenders:
                logger.info(f"Found {len(new_tenders)} new tenders")
                
                for i, tender in enumerate(new_tenders):
                    message = format_tender_message(f"📢 New Tender Published ({i+1}/{len(new_tenders)})", tender)
                    
                    if send_telegram_message(message):
                        sent_tenders.append(tender)
                        sent_links.append(tender.get("link"))
                        logger.info(f"✅ New tender sent: {tender.get('title', 'Untitled')[:50]}...")
                    
                    if i < len(new_tenders) - 1:
                        time.sleep(1)
                
                save_sent_tenders(sent_tenders)
            else:
                logger.info("No new tenders found")
            
            if len(sent_tenders) > 100:
                sent_tenders = sent_tenders[-50:] 
                save_sent_tenders(sent_tenders)
                sent_links = [t.get("link") for t in sent_tenders if t.get("link")]
                logger.info("Cleaned up old tender records")
            
            logger.info(f"Next check in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
            check_count += 1
            
        except KeyboardInterrupt:
            logger.info("\n👋 Monitor stopped by user")
            send_telegram_message("🛑 <b>XMUM Tender Monitor Stopped</b>\nMonitoring has been manually stopped.")
            break
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
            import traceback
            traceback.print_exc()

            logger.info("Waiting 60 seconds before retrying...")
            time.sleep(60)

def setup_instructions():
    print("\n" + "="*60)
    print("📋 XMUM TENDER MONITOR - SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. TELEGRAM BOT SETUP:")
    print("   - Message @BotFather on Telegram")
    print("   - Send /newbot to create a new bot")
    print("   - Follow instructions to get your bot token")
    print("\n2. GET YOUR CHAT ID:")
    print("   - Message @userinfobot on Telegram")
    print("   - It will reply with your chat ID")
    print("\n3. SET ENVIRONMENT VARIABLES:")
    print("   Linux/Mac:")
    print("     export TELEGRAM_BOT_TOKEN='your_bot_token'")
    print("     export TELEGRAM_CHAT_ID='your_chat_id'")
    print("\n   Windows (Command Prompt):")
    print("     set TELEGRAM_BOT_TOKEN=your_bot_token")
    print("     set TELEGRAM_CHAT_ID=your_chat_id")
    print("\n   Windows (PowerShell):")
    print("     $env:TELEGRAM_BOT_TOKEN='your_bot_token'")
    print("     $env:TELEGRAM_CHAT_ID='your_chat_id'")
    print("\n4. OR CREATE .env FILE:")
    print("   Create a file named '.env' with:")
    print("   TELEGRAM_BOT_TOKEN=your_bot_token")
    print("   TELEGRAM_CHAT_ID=your_chat_id")
    print("\n5. INSTALL REQUIREMENTS:")
    print("   pip install requests beautifulsoup4")
    print("\n6. RUN THE MONITOR:")
    print("   python tender_monitor.py")
    print("\n" + "="*60)

if __name__ == "__main__":
    if BOT_TOKEN == "your_bot_token_here" or CHAT_ID == "your_chat_id_here":
        setup_instructions()
        print("\n⚠️  Please set your Telegram credentials before running!")
        
        response = input("\nContinue with test run? (y/n): ").lower()
        if response == 'y':
            print("\nStarting monitor with test credentials...")
            main()
        else:
            print("\nExiting. Please set your credentials and try again.")
    else:
        main()
