import os
import time
import re
from supabase import create_client, Client
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Set these in your .env file or export them
SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

STATE_DISTRICTS = {
    "Andhra Pradesh": [
        "Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", 
        "Kakinada", "Rajahmundry", "Kadapa", "Tirupati", "Anantapur", 
        "Vizianagaram", "Eluru", "Ongole", "Nandyal", "Machilipatnam",
        "Chittoor", "Srikakulam", "Bhimavaram", "Gudivada", "Tenali"
    ],
    "Telangana": [
        "Hyderabad", "Warangal", "Nizamabad", "Khammam", "Karimnagar", 
        "Ramagundam", "Mahbubnagar", "Nalgonda", "Adilabad", "Suryapet",
        "Miryalaguda", "Jagtial"
    ]
}

CATEGORIES = {
  "All in 1": [
    "Kirana Store", "Fruits & Vegetables", "Meat Shop", "Dairy Booth", "Bakery", "Sweet Shop",
    "Restaurant", "Cafe", "Fast Food", "Juice Shop", "Clothing Store", "Boutique", "Footwear Shop",
    "Jewellery", "Beauty Store", "Spa", "Salon", "Tailor", "Furniture Store", "Hardware Store",
    "Paints", "Plumbing", "Laundry", "Real Estate", "Electronics Store", "Mobile Shop", "Computer Repair",
    "Internet Cafe", "Factory", "CA", "Advocate", "Travel Agency", "Garage", "Car Wash", "Tyre Shop",
    "Stationery", "Coaching", "Photography", "Electrician", "Pest Control", "Petrol Pump",
    "Hospitals", "Pharmacies", "Blood Donations"
  ]
}

def generate_leads(job_id, state, main_category, sub_category, target_count):
    print(f"[{job_id}] Deep Scraping {target_count} leads for {sub_category or main_category} in {state}...")
    
    leads_to_insert = []
    
    # Determine categories to search
    categories_to_search = []
    if sub_category:
        categories_to_search.append(sub_category)
    elif main_category in CATEGORIES and CATEGORIES[main_category]:
        categories_to_search.extend(CATEGORIES[main_category])
    elif main_category == "All in 1":
        categories_to_search.extend(CATEGORIES["All in 1"])
    else:
        categories_to_search.append(main_category)
        
    # Determine districts
    districts_to_search = STATE_DISTRICTS.get(state, [state])
    
    # 1. Fetch existing leads for deduplication before we start scraping
    existing_leads_res = supabase.table('leads').select('phone_number').execute()
    archived_leads_res = supabase.table('archived_leads').select('phone_number').execute()
    
    existing_numbers = set([l['phone_number'] for l in existing_leads_res.data])
    archived_numbers = set([l['phone_number'] for l in archived_leads_res.data])
    all_blacklisted = existing_numbers.union(archived_numbers)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Nested Loop: Districts -> Categories
            for district in districts_to_search:
                if len(leads_to_insert) >= target_count:
                    break
                    
                for category in categories_to_search:
                    if len(leads_to_insert) >= target_count:
                        break
                        
                    query = f"{category} in {district}, {state}"
                    print(f"[{job_id}] Searching Google Maps: {query}")
                    
                    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
                    page.goto(search_url, timeout=60000)
                    
                    try:
                        page.wait_for_selector('a[href*="/maps/place/"]', timeout=10000)
                    except Exception as e:
                        print(f"[{job_id}] No results loaded for {query}")
                        continue
                        
                    scraped_data = set()
                    attempts = 0
                    
                    # Scroll loop for THIS query
                    while len(leads_to_insert) < target_count and attempts < 15:
                        elements = page.query_selector_all('a[href*="/maps/place/"]')
                        
                        added_in_attempt = 0
                        for el in elements:
                            if len(leads_to_insert) >= target_count:
                                break
                                
                            label = el.get_attribute('aria-label')
                            if not label or label in scraped_data:
                                continue
                                
                            scraped_data.add(label)
                            
                            try:
                                el.scroll_into_view_if_needed()
                                el.click(force=True)
                                page.wait_for_timeout(3000)
                                
                                phone_btn = page.query_selector('button[data-item-id^="phone:tel:"]')
                                if phone_btn:
                                    phone = phone_btn.get_attribute('data-item-id').replace('phone:tel:', '')
                                    if len(phone) >= 10:
                                        b_name = label.split(',')[0].strip() if ',' in label else label
                                        
                                        if phone not in all_blacklisted:
                                            lead_data = {
                                                "business_name": b_name,
                                                "phone_number": phone,
                                                "main_category": main_category,
                                                "sub_category": category,
                                                "state": state,
                                                "district": district,
                                                "status": "NEW"
                                            }
                                            
                                            supabase.table('leads').insert([lead_data]).execute()
                                            all_blacklisted.add(phone)
                                            leads_to_insert.append(lead_data)
                                            added_in_attempt += 1
                                            
                                            print(f"✅ Found & Inserted: {b_name} - {phone} ({len(leads_to_insert)}/{target_count})")
                                            supabase.table("scrape_jobs").update({"status": f"PROCESSING (Found {len(leads_to_insert)}/{target_count})"}).eq("id", job_id).execute()
                            except Exception as ex:
                                pass

                        # If we didn't add anything new and tried scrolling a few times, assume end of list
                        if added_in_attempt == 0 and attempts > 2:
                            print(f"[{job_id}] Exhausted results for {query}")
                            break
                            
                        # Scroll to load more
                        try:
                            page.evaluate('document.querySelector("div[role=\'feed\']").scrollTo(0, document.querySelector("div[role=\'feed\']").scrollHeight)')
                            time.sleep(2)
                        except:
                            break
                            
                        # Check cancellation
                        check_res = supabase.table("scrape_jobs").select("status").eq("id", job_id).execute()
                        if check_res.data and check_res.data[0]['status'] == 'CANCELLED':
                            print(f"[{job_id}] Job cancelled.")
                            browser.close()
                            return len(leads_to_insert)
                            
                        attempts += 1
                        
            browser.close()
    except Exception as e:
        print(f"[{job_id}] Playwright Scraper Error: {e}")
        
    if leads_to_insert:
        print(f"[{job_id}] Successfully inserted {len(leads_to_insert)} unique leads.")
    else:
        print(f"[{job_id}] No unique leads were scraped.")
        
    return len(leads_to_insert)

def poll_jobs():
    print("Worker started. Listening for scrape jobs...")
    while True:
        try:
            # Check for PENDING jobs
            response = supabase.table("scrape_jobs") \
                .select("*") \
                .eq("status", "PENDING") \
                .order("created_at") \
                .limit(1) \
                .execute()
            
            jobs = response.data
            
            if jobs:
                job = jobs[0]
                job_id = job['id']
                print(f"\n--- Found new job: {job_id} ---")
                
                # Mark as PROCESSING
                supabase.table("scrape_jobs").update({"status": "PROCESSING"}).eq("id", job_id).execute()
                
                try:
                    # Run the scraper
                    found_count = generate_leads(
                        job_id=job_id,
                        state=job['state'],
                        main_category=job['main_category'],
                        sub_category=job['sub_category'],
                        target_count=job['target_count']
                    )
                    
                    # If it was cancelled, generate_leads returns None
                    if found_count is None:
                        continue
                    
                    # Determine final status based on how many were found vs requested
                    target = job['target_count']
                    if found_count >= target:
                        final_status = f"COMPLETED (Found {found_count}/{target})"
                    elif found_count > 0:
                        final_status = f"EXHAUSTED (Found {found_count}/{target})"
                    else:
                        final_status = f"COMPLETELY EXHAUSTED (Found 0)"
                        
                    supabase.table("scrape_jobs").update({"status": final_status}).eq("id", job_id).execute()
                    print(f"[{job_id}] Job Finished: {final_status}")
                    
                except Exception as e:
                    print(f"[{job_id}] Error during scraping: {e}")
                    # Mark as FAILED
                    supabase.table("scrape_jobs").update({"status": "FAILED"}).eq("id", job_id).execute()
            
            # Wait before polling again
            time.sleep(5)
            
        except Exception as e:
            print(f"Database error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    import threading
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Worker is running 24/7!"
        
    # Start the worker loop in a background thread
    worker_thread = threading.Thread(target=poll_jobs, daemon=True)
    worker_thread.start()
    
    # Start the Flask web server (Required by Render to keep service alive)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
