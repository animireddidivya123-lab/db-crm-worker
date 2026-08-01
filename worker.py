import os
import time
import re
import urllib.parse
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
        "Anantapur",
        "Chittoor",
        "East Godavari",
        "Guntur",
        "Krishna",
        "Kurnool",
        "Nellore",
        "Prakasam",
        "Srikakulam",
        "Visakhapatnam",
        "Vizianagaram",
        "West Godavari",
        "YSR Kadapa"
    ],
    "Arunachal Pradesh": [
        "Tawang",
        "West Kameng",
        "East Kameng",
        "Papum Pare",
        "Kurung Kumey",
        "Kra Daadi",
        "Lower Subansiri",
        "Upper Subansiri",
        "West Siang",
        "East Siang",
        "Siang",
        "Upper Siang",
        "Lower Siang",
        "Lower Dibang Valley",
        "Dibang Valley",
        "Anjaw",
        "Lohit",
        "Namsai",
        "Changlang",
        "Tirap",
        "Longding"
    ],
    "Assam": [
        "Baksa",
        "Barpeta",
        "Biswanath",
        "Bongaigaon",
        "Cachar",
        "Charaideo",
        "Chirang",
        "Darrang",
        "Dhemaji",
        "Dhubri",
        "Dibrugarh",
        "Goalpara",
        "Golaghat",
        "Hailakandi",
        "Hojai",
        "Jorhat",
        "Kamrup Metropolitan",
        "Kamrup",
        "Karbi Anglong",
        "Karimganj",
        "Kokrajhar",
        "Lakhimpur",
        "Majuli",
        "Morigaon",
        "Nagaon",
        "Nalbari",
        "Dima Hasao",
        "Sivasagar",
        "Sonitpur",
        "South Salmara-Mankachar",
        "Tinsukia",
        "Udalguri",
        "West Karbi Anglong"
    ],
    "Bihar": [
        "Araria",
        "Arwal",
        "Aurangabad",
        "Banka",
        "Begusarai",
        "Bhagalpur",
        "Bhojpur",
        "Buxar",
        "Darbhanga",
        "East Champaran (Motihari)",
        "Gaya",
        "Gopalganj",
        "Jamui",
        "Jehanabad",
        "Kaimur (Bhabua)",
        "Katihar",
        "Khagaria",
        "Kishanganj",
        "Lakhisarai",
        "Madhepura",
        "Madhubani",
        "Munger (Monghyr)",
        "Muzaffarpur",
        "Nalanda",
        "Nawada",
        "Patna",
        "Purnia (Purnea)",
        "Rohtas",
        "Saharsa",
        "Samastipur",
        "Saran",
        "Sheikhpura",
        "Sheohar",
        "Sitamarhi",
        "Siwan",
        "Supaul",
        "Vaishali",
        "West Champaran"
    ],
    "Chandigarh": [
        "Chandigarh"
    ],
    "Chhattisgarh": [
        "Balod",
        "Baloda Bazar",
        "Balrampur",
        "Bastar",
        "Bemetara",
        "Bijapur",
        "Bilaspur",
        "Dantewada (South Bastar)",
        "Dhamtari",
        "Durg",
        "Gariyaband",
        "Janjgir-Champa",
        "Jashpur",
        "Kabirdham (Kawardha)",
        "Kanker (North Bastar)",
        "Kondagaon",
        "Korba",
        "Korea (Koriya)",
        "Mahasamund",
        "Mungeli",
        "Narayanpur",
        "Raigarh",
        "Raipur",
        "Rajnandgaon",
        "Sukma",
        "Surajpur  ",
        "Surguja"
    ],
    "Dadra & Nagar Haveli": [
        "Dadra & Nagar Haveli",
        "Daman",
        "Diu"
    ],
    "Delhi": [
        "Central Delhi",
        "East Delhi",
        "New Delhi",
        "North Delhi",
        "North East  Delhi",
        "North West  Delhi",
        "Shahdara",
        "South Delhi",
        "South East Delhi",
        "South West  Delhi",
        "West Delhi"
    ],
    "Goa": [
        "North Goa",
        "South Goa"
    ],
    "Gujarat": [
        "Ahmedabad",
        "Amreli",
        "Anand",
        "Aravalli",
        "Banaskantha (Palanpur)",
        "Bharuch",
        "Bhavnagar",
        "Botad",
        "Chhota Udepur",
        "Dahod",
        "Dangs (Ahwa)",
        "Devbhoomi Dwarka",
        "Gandhinagar",
        "Gir Somnath",
        "Jamnagar",
        "Junagadh",
        "Kachchh",
        "Kheda (Nadiad)",
        "Mahisagar",
        "Mehsana",
        "Morbi",
        "Narmada (Rajpipla)",
        "Navsari",
        "Panchmahal (Godhra)",
        "Patan",
        "Porbandar",
        "Rajkot",
        "Sabarkantha (Himmatnagar)",
        "Surat",
        "Surendranagar",
        "Tapi (Vyara)",
        "Vadodara",
        "Valsad"
    ],
    "Haryana": [
        "Ambala",
        "Bhiwani",
        "Charkhi Dadri",
        "Faridabad",
        "Fatehabad",
        "Gurgaon",
        "Hisar",
        "Jhajjar",
        "Jind",
        "Kaithal",
        "Karnal",
        "Kurukshetra",
        "Mahendragarh",
        "Mewat",
        "Palwal",
        "Panchkula",
        "Panipat",
        "Rewari",
        "Rohtak",
        "Sirsa",
        "Sonipat",
        "Yamunanagar"
    ],
    "Himachal Pradesh": [
        "Bilaspur",
        "Chamba",
        "Hamirpur",
        "Kangra",
        "Kinnaur",
        "Kullu",
        "Lahaul &amp; Spiti",
        "Mandi",
        "Shimla",
        "Sirmaur (Sirmour)",
        "Solan",
        "Una"
    ],
    "Jammu & Kashmir": [
        "Anantnag",
        "Bandipore",
        "Baramulla",
        "Budgam",
        "Doda",
        "Ganderbal",
        "Jammu",
        "Kargil",
        "Kathua",
        "Kishtwar",
        "Kulgam",
        "Kupwara",
        "Leh",
        "Poonch",
        "Pulwama",
        "Rajouri",
        "Ramban",
        "Reasi",
        "Samba",
        "Shopian",
        "Srinagar",
        "Udhampur"
    ],
    "Jharkhand": [
        "Bokaro",
        "Chatra",
        "Deoghar",
        "Dhanbad",
        "Dumka",
        "East Singhbhum",
        "Garhwa",
        "Giridih",
        "Godda",
        "Gumla",
        "Hazaribag",
        "Jamtara",
        "Khunti",
        "Koderma",
        "Latehar",
        "Lohardaga",
        "Pakur",
        "Palamu",
        "Ramgarh",
        "Ranchi",
        "Sahibganj",
        "Seraikela-Kharsawan",
        "Simdega",
        "West Singhbhum"
    ],
    "Karnataka": [
        "Bagalkot",
        "Ballari (Bellary)",
        "Belagavi (Belgaum)",
        "Bengaluru (Bangalore) Rural",
        "Bengaluru (Bangalore) Urban",
        "Bidar",
        "Chamarajanagar",
        "Chikballapur",
        "Chikkamagaluru (Chikmagalur)",
        "Chitradurga",
        "Dakshina Kannada",
        "Davangere",
        "Dharwad",
        "Gadag",
        "Hassan",
        "Haveri",
        "Kalaburagi (Gulbarga)",
        "Kodagu",
        "Kolar",
        "Koppal",
        "Mandya",
        "Mysuru (Mysore)",
        "Raichur",
        "Ramanagara",
        "Shivamogga (Shimoga)",
        "Tumakuru (Tumkur)",
        "Udupi",
        "Uttara Kannada (Karwar)",
        "Vijayapura (Bijapur)",
        "Yadgir"
    ],
    "Kerala": [
        "Alappuzha",
        "Ernakulam",
        "Idukki",
        "Kannur",
        "Kasaragod",
        "Kollam",
        "Kottayam",
        "Kozhikode",
        "Malappuram",
        "Palakkad",
        "Pathanamthitta",
        "Thiruvananthapuram",
        "Thrissur",
        "Wayanad"
    ],
    "Lakshadweep": [
        "Agatti",
        "Amini",
        "Androth",
        "Bithra",
        "Chethlath",
        "Kavaratti",
        "Kadmath",
        "Kalpeni",
        "Kilthan",
        "Minicoy"
    ],
    "Madhya Pradesh": [
        "Agar Malwa",
        "Alirajpur",
        "Anuppur",
        "Ashoknagar",
        "Balaghat",
        "Barwani",
        "Betul",
        "Bhind",
        "Bhopal",
        "Burhanpur",
        "Chhatarpur",
        "Chhindwara",
        "Damoh",
        "Datia",
        "Dewas",
        "Dhar",
        "Dindori",
        "Guna",
        "Gwalior",
        "Harda",
        "Hoshangabad",
        "Indore",
        "Jabalpur",
        "Jhabua",
        "Katni",
        "Khandwa",
        "Khargone",
        "Mandla",
        "Mandsaur",
        "Morena",
        "Narsinghpur",
        "Neemuch",
        "Panna",
        "Raisen",
        "Rajgarh",
        "Ratlam",
        "Rewa",
        "Sagar",
        "Satna",
        "Sehore",
        "Seoni",
        "Shahdol",
        "Shajapur",
        "Sheopur",
        "Shivpuri",
        "Sidhi",
        "Singrauli",
        "Tikamgarh",
        "Ujjain",
        "Umaria",
        "Vidisha"
    ],
    "Maharashtra": [
        "Ahmednagar",
        "Akola",
        "Amravati",
        "Aurangabad",
        "Beed",
        "Bhandara",
        "Buldhana",
        "Chandrapur",
        "Dhule",
        "Gadchiroli",
        "Gondia",
        "Hingoli",
        "Jalgaon",
        "Jalna",
        "Kolhapur",
        "Latur",
        "Mumbai City",
        "Mumbai Suburban",
        "Nagpur",
        "Nanded",
        "Nandurbar",
        "Nashik",
        "Osmanabad",
        "Palghar",
        "Parbhani",
        "Pune",
        "Raigad",
        "Ratnagiri",
        "Sangli",
        "Satara",
        "Sindhudurg",
        "Solapur",
        "Thane",
        "Wardha",
        "Washim",
        "Yavatmal"
    ],
    "Manipur": [
        "Bishnupur",
        "Chandel",
        "Churachandpur",
        "Imphal East",
        "Imphal West",
        "Jiribam",
        "Kakching",
        "Kamjong",
        "Kangpokpi",
        "Noney",
        "Pherzawl",
        "Senapati",
        "Tamenglong",
        "Tengnoupal",
        "Thoubal",
        "Ukhrul"
    ],
    "Meghalaya": [
        "East Garo Hills",
        "East Jaintia Hills",
        "East Khasi Hills",
        "North Garo Hills",
        "Ri Bhoi",
        "South Garo Hills",
        "South West Garo Hills ",
        "South West Khasi Hills",
        "West Garo Hills",
        "West Jaintia Hills",
        "West Khasi Hills"
    ],
    "Mizoram": [
        "Aizawl",
        "Champhai",
        "Kolasib",
        "Lawngtlai",
        "Lunglei",
        "Mamit",
        "Saiha",
        "Serchhip"
    ],
    "Nagaland": [
        "Dimapur",
        "Kiphire",
        "Kohima",
        "Longleng",
        "Mokokchung",
        "Mon",
        "Peren",
        "Phek",
        "Tuensang",
        "Wokha",
        "Zunheboto"
    ],
    "Odisha": [
        "Angul",
        "Balangir",
        "Balasore",
        "Bargarh",
        "Bhadrak",
        "Boudh",
        "Cuttack",
        "Deogarh",
        "Dhenkanal",
        "Gajapati",
        "Ganjam",
        "Jagatsinghapur",
        "Jajpur",
        "Jharsuguda",
        "Kalahandi",
        "Kandhamal",
        "Kendrapara",
        "Kendujhar (Keonjhar)",
        "Khordha",
        "Koraput",
        "Malkangiri",
        "Mayurbhanj",
        "Nabarangpur",
        "Nayagarh",
        "Nuapada",
        "Puri",
        "Rayagada",
        "Sambalpur",
        "Sonepur",
        "Sundargarh"
    ],
    "Puducherry": [
        "Karaikal",
        "Mahe",
        "Pondicherry",
        "Yanam"
    ],
    "Punjab": [
        "Amritsar",
        "Barnala",
        "Bathinda",
        "Faridkot",
        "Fatehgarh Sahib",
        "Fazilka",
        "Ferozepur",
        "Gurdaspur",
        "Hoshiarpur",
        "Jalandhar",
        "Kapurthala",
        "Ludhiana",
        "Mansa",
        "Moga",
        "Muktsar",
        "Nawanshahr (Shahid Bhagat Singh Nagar)",
        "Pathankot",
        "Patiala",
        "Rupnagar",
        "Sahibzada Ajit Singh Nagar (Mohali)",
        "Sangrur",
        "Tarn Taran"
    ],
    "Rajasthan": [
        "Ajmer",
        "Alwar",
        "Banswara",
        "Baran",
        "Barmer",
        "Bharatpur",
        "Bhilwara",
        "Bikaner",
        "Bundi",
        "Chittorgarh",
        "Churu",
        "Dausa",
        "Dholpur",
        "Dungarpur",
        "Hanumangarh",
        "Jaipur",
        "Jaisalmer",
        "Jalore",
        "Jhalawar",
        "Jhunjhunu",
        "Jodhpur",
        "Karauli",
        "Kota",
        "Nagaur",
        "Pali",
        "Pratapgarh",
        "Rajsamand",
        "Sawai Madhopur",
        "Sikar",
        "Sirohi",
        "Sri Ganganagar",
        "Tonk",
        "Udaipur"
    ],
    "Sikkim": [
        "East Sikkim",
        "North Sikkim",
        "South Sikkim",
        "West Sikkim"
    ],
    "Tamil Nadu": [
        "Ariyalur",
        "Chennai",
        "Coimbatore",
        "Cuddalore",
        "Dharmapuri",
        "Dindigul",
        "Erode",
        "Kanchipuram",
        "Kanyakumari",
        "Karur",
        "Krishnagiri",
        "Madurai",
        "Nagapattinam",
        "Namakkal",
        "Nilgiris",
        "Perambalur",
        "Pudukkottai",
        "Ramanathapuram",
        "Salem",
        "Sivaganga",
        "Thanjavur",
        "Theni",
        "Thoothukudi (Tuticorin)",
        "Tiruchirappalli",
        "Tirunelveli",
        "Tiruppur",
        "Tiruvallur",
        "Tiruvannamalai",
        "Tiruvarur",
        "Vellore",
        "Viluppuram",
        "Virudhunagar"
    ],
    "Telangana": [
        "Adilabad",
        "Bhadradri Kothagudem",
        "Hyderabad",
        "Jagtial",
        "Jangaon",
        "Jayashankar Bhoopalpally",
        "Jogulamba Gadwal",
        "Kamareddy",
        "Karimnagar",
        "Khammam",
        "Komaram Bheem Asifabad",
        "Mahabubabad",
        "Mahabubnagar",
        "Mancherial",
        "Medak",
        "Medchal",
        "Nagarkurnool",
        "Nalgonda",
        "Nirmal",
        "Nizamabad",
        "Peddapalli",
        "Rajanna Sircilla",
        "Rangareddy",
        "Sangareddy",
        "Siddipet",
        "Suryapet",
        "Vikarabad",
        "Wanaparthy",
        "Warangal (Rural)",
        "Warangal (Urban)",
        "Yadadri Bhuvanagiri"
    ],
    "Tripura": [
        "Dhalai",
        "Gomati",
        "Khowai",
        "North Tripura",
        "Sepahijala",
        "South Tripura",
        "Unakoti",
        "West Tripura"
    ],
    "Uttarakhand": [
        "Almora",
        "Bageshwar",
        "Chamoli",
        "Champawat",
        "Dehradun",
        "Haridwar",
        "Nainital",
        "Pauri Garhwal",
        "Pithoragarh",
        "Rudraprayag",
        "Tehri Garhwal",
        "Udham Singh Nagar",
        "Uttarkashi"
    ],
    "Uttar Pradesh": [
        "Agra",
        "Aligarh",
        "Allahabad",
        "Ambedkar Nagar",
        "Amethi (Chatrapati Sahuji Mahraj Nagar)",
        "Amroha (J.P. Nagar)",
        "Auraiya",
        "Azamgarh",
        "Baghpat",
        "Bahraich",
        "Ballia",
        "Balrampur",
        "Banda",
        "Barabanki",
        "Bareilly",
        "Basti",
        "Bhadohi",
        "Bijnor",
        "Budaun",
        "Bulandshahr",
        "Chandauli",
        "Chitrakoot",
        "Deoria",
        "Etah",
        "Etawah",
        "Faizabad",
        "Farrukhabad",
        "Fatehpur",
        "Firozabad",
        "Gautam Buddha Nagar",
        "Ghaziabad",
        "Ghazipur",
        "Gonda",
        "Gorakhpur",
        "Hamirpur",
        "Hapur (Panchsheel Nagar)",
        "Hardoi",
        "Hathras",
        "Jalaun",
        "Jaunpur",
        "Jhansi",
        "Kannauj",
        "Kanpur Dehat",
        "Kanpur Nagar",
        "Kanshiram Nagar (Kasganj)",
        "Kaushambi",
        "Kushinagar (Padrauna)",
        "Lakhimpur - Kheri",
        "Lalitpur",
        "Lucknow",
        "Maharajganj",
        "Mahoba",
        "Mainpuri",
        "Mathura",
        "Mau",
        "Meerut",
        "Mirzapur",
        "Moradabad",
        "Muzaffarnagar",
        "Pilibhit",
        "Pratapgarh",
        "RaeBareli",
        "Rampur",
        "Saharanpur",
        "Sambhal (Bhim Nagar)",
        "Sant Kabir Nagar",
        "Shahjahanpur",
        "Shamali (Prabuddh Nagar)",
        "Shravasti",
        "Siddharth Nagar",
        "Sitapur",
        "Sonbhadra",
        "Sultanpur",
        "Unnao",
        "Varanasi"
    ],
    "West Bengal": [
        "Alipurduar",
        "Bankura",
        "Birbhum",
        "Burdwan (Bardhaman)",
        "Cooch Behar",
        "Dakshin Dinajpur (South Dinajpur)",
        "Darjeeling",
        "Hooghly",
        "Howrah",
        "Jalpaiguri",
        "Kalimpong",
        "Kolkata",
        "Malda",
        "Murshidabad",
        "Nadia",
        "North 24 Parganas",
        "Paschim Medinipur (West Medinipur)",
        "Purba Medinipur (East Medinipur)",
        "Purulia",
        "South 24 Parganas",
        "Uttar Dinajpur (North Dinajpur)"
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
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            # Nested Loop: Districts -> Categories
            for district in districts_to_search:
                if len(leads_to_insert) >= target_count:
                    break
                    
                for category in categories_to_search:
                    if len(leads_to_insert) >= target_count:
                        break
                        
                    query = f"{category} in {district}, {state}"
                    print(f"[{job_id}] Searching Google Maps: {query}")
                    
                    search_url = f"https://www.google.com/maps/search/{urllib.parse.quote_plus(query)}"
                    page.goto(search_url, timeout=60000)
                    page.wait_for_timeout(3000) # Give maps a moment to decide to show consent or load
                    
                    # Bypass cookie consent if it appears
                    try:
                        consent_btn = page.query_selector('button[aria-label="Reject all"]') or page.query_selector('button[aria-label="Accept all"]')
                        if consent_btn:
                            consent_btn.click()
                            page.wait_for_timeout(2000)
                    except:
                        pass
                    
                    try:
                        page.wait_for_selector('a[href*="/maps/place/"]', timeout=20000)
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
