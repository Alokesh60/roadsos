"""
response_templates.py
---------------------
Offline scripted responses for every intent.
Used when there is no network and the LLM cannot be reached.
These are stored in chatbot_intents.json AND in this file as a Python
fallback so the server never returns an empty reply.

Each template contains:
  - reply        : the text shown in the chat bubble
  - reply_hi     : Hindi translation (optional, falls back to reply)
  - reply_as     : Assamese translation (optional, falls back to reply)
  - action_label : label for the primary quick-action button
  - action_number: phone number for that button
  - extra_actions: optional additional buttons

FIX LOG (issues_alokesh_pdf.pdf):
  - Added missing intents: theft, robbery, assault, suspicious_activity,
    flood, landslide, earthquake
  - Added reply_hi / reply_as to every template (was English-only)
  - Improved "other" template — now guides user with explicit keywords
    instead of asking them to 'describe clearly' (panic UX fix)
"""

from typing import TypedDict


class ActionButton(TypedDict):
    label: str
    number: str


class Template(TypedDict):
    reply: str
    reply_hi: str
    reply_as: str
    action_label: str
    action_number: str
    extra_actions: list[ActionButton]


TEMPLATES: dict[str, Template] = {

    "accident": {
        "reply": (
            "There has been an accident. Stay calm.\n\n"
            "1. Call 108 for an ambulance immediately.\n"
            "2. Call 100 to report to police.\n"
            "3. Turn on your hazard lights.\n"
            "4. Do NOT move any injured person unless there is immediate danger "
            "of fire or water.\n"
            "5. If safe, place a warning triangle 50 metres behind the vehicle.\n\n"
            "Help is on the way. Stay on the line with the operator."
        ),
        "reply_hi": (
            "Durghatna ho gayi hai. Shant rahein.\n\n"
            "1. Turant 108 pe ambulance ke liye call karein.\n"
            "2. Police ke liye 100 pe call karein.\n"
            "3. Apni hazard lights chalu karein.\n"
            "4. Jab tak aag ya paani ka khatra na ho, kisi ghayaal vyakti ko mat hilaayein.\n"
            "5. Agar safe ho, gaadi ke 50 metre peechhe warning triangle lagaayein.\n\n"
            "Madad aa rahi hai. Operator se line pe bane rahein."
        ),
        "reply_as": (
            "Durghotona hoiche. Shant thakk.\n\n"
            "1. Turant 108 t ambulance-or karane korok.\n"
            "2. Police-or karane 100 t korok.\n"
            "3. Hazard light jalaao.\n"
            "4. Agun ba pani-or bhoyo naholey, ahatgrastha manuhok nushuwaba.\n"
            "5. Suraksit hole, gari-r 50 mitr pishot warning triangle rakhk.\n\n"
            "Sahajyo ashise. Operator-or loge line-t thakk."
        ),
        "action_label": "Call Ambulance — 108",
        "action_number": "108",
        "extra_actions": [
            {"label": "Call Police — 100", "number": "100"},
            {"label": "Highway Helpline — 1033", "number": "1033"},
        ],
    },

    "tyre_burst": {
        "reply": (
            "Tyre burst — follow these steps immediately:\n\n"
            "1. Grip the steering wheel FIRMLY with both hands.\n"
            "2. Do NOT brake suddenly — it will cause a skid.\n"
            "3. Ease off the accelerator slowly.\n"
            "4. Steer straight and let the vehicle slow down on its own.\n"
            "5. Gradually steer to the LEFT shoulder and stop.\n"
            "6. Turn on hazard lights and stay inside until it is safe.\n\n"
            "Call 1033 (NHAI) for roadside assistance on national highways."
        ),
        "reply_hi": (
            "Tyre burst — in steps ko turant follow karein:\n\n"
            "1. Steering wheel ko DONO haathon se mazbooti se pakdein.\n"
            "2. Achanak brakes mat lagaayein — gaadi fissal sakti hai.\n"
            "3. Dheere dheere accelerator chhodein.\n"
            "4. Seedha chalein aur gaadi khud slow hone dein.\n"
            "5. Dheere dheere LEFT shoulder par aa jaayein.\n"
            "6. Hazard lights chalu karein aur tab tak andar rahein jab tak safe na ho.\n\n"
            "Raaste ki sahayata ke liye 1033 (NHAI) pe call karein."
        ),
        "reply_as": (
            "Tyre burst — ei kadam turant lobok:\n\n"
            "1. Steering wheel DUYOKHAT dhori rakhk.\n"
            "2. Ekelge brake diba nuba — gari fisli jab.\n"
            "3. Dheere dheere accelerator-r pressure kom korok.\n"
            "4. Seedha yao aru gari nijei slow hobole diya.\n"
            "5. Ahiste LEFT shoulder-t gari thuwao.\n"
            "6. Hazard light jalaao aru suraksit nohowaloika andar thakk.\n\n"
            "National highway-t rastar sahajyo-or karane 1033 (NHAI) t call korok."
        ),
        "action_label": "NHAI Roadside Help — 1033",
        "action_number": "1033",
        "extra_actions": [
            {"label": "Call Police — 100", "number": "100"},
        ],
    },

    "breakdown": {
        "reply": (
            "Vehicle breakdown — here is what to do:\n\n"
            "1. Steer to the LEFT shoulder immediately.\n"
            "2. Turn on your hazard lights.\n"
            "3. Place a warning triangle behind the vehicle if you have one.\n"
            "4. Do not stand behind or in front of the vehicle on the road.\n"
            "5. Call 1033 (NHAI helpline) for highway assistance.\n"
            "6. Contact a local garage or towing service.\n\n"
            "Stay inside the vehicle with doors locked if traffic is fast."
        ),
        "reply_hi": (
            "Gaadi kharab ho gayi — yeh karein:\n\n"
            "1. Turant LEFT shoulder par aa jaayein.\n"
            "2. Hazard lights chalu karein.\n"
            "3. Agar warning triangle ho toh gaadi ke peechhe lagaayein.\n"
            "4. Sadak par gaadi ke aage ya peechhe mat khaDe ho.\n"
            "5. Highway sahayata ke liye 1033 (NHAI) pe call karein.\n"
            "6. Local garage ya towing service se contact karein.\n\n"
            "Agar traffic fast hai toh gaadi ke andar darwaza lock karke rahein."
        ),
        "reply_as": (
            "Gari kharab hoiche — ei koribo:\n\n"
            "1. Turant LEFT shoulder-t yao.\n"
            "2. Hazard light jalaao.\n"
            "3. Warning triangle thakile gari-r pitot rakhk.\n"
            "4. Sarak-t gari-r aagor ba pitot nithio.\n"
            "5. Highway sahajyo-or karane 1033 (NHAI) t call korok.\n"
            "6. Local garage ba towing service-k khabor diya.\n\n"
            "Traffic beshi hoile gari-r bhitort door lock kori thakk."
        ),
        "action_label": "NHAI Helpline — 1033",
        "action_number": "1033",
        "extra_actions": [
            {"label": "Call Police — 100", "number": "100"},
        ],
    },

    "medical": {
        "reply": (
            "Medical emergency — act immediately:\n\n"
            "1. Call 108 for an ambulance RIGHT NOW.\n"
            "2. Keep the person STILL, warm, and calm.\n"
            "3. Do NOT give water or food if they are unconscious.\n"
            "4. If they are not breathing and you are trained, begin CPR.\n"
            "5. If there is bleeding, apply firm pressure with a cloth.\n"
            "6. Stay on the line with the 108 operator — they will guide you.\n\n"
            "Do not leave the person alone."
        ),
        "reply_hi": (
            "Medical emergency — turant karein:\n\n"
            "1. ABHI ambulance ke liye 108 pe call karein.\n"
            "2. Vyakti ko STILL, garam aur shant rakhein.\n"
            "3. Behosh ho toh paani ya khaana mat dein.\n"
            "4. Saans nahi aa rahi aur training hai toh CPR shuru karein.\n"
            "5. Khoon aa raha ho toh kapde se mazboot dabaayen.\n"
            "6. 108 operator se line pe bane rahein — woh guide karenge.\n\n"
            "Vyakti ko akela mat chhodein."
        ),
        "reply_as": (
            "Medical emergency — turant korok:\n\n"
            "1. EKHONI ambulance-or karane 108 t call korok.\n"
            "2. Manuhjon-k STILL, garam aru shant rakhk.\n"
            "3. Unconscious hoile pani ba khabar nidiba.\n"
            "4. Nhashwas lorchhe aru training ase toh CPR aarambo korok.\n"
            "5. Rokto porile kapora-r e mukhliya dhori rakhk.\n"
            "6. 108 operator-or loge line-t thakk — tai guide korib.\n\n"
            "Manuhjon-k ekela neribi."
        ),
        "action_label": "Call Ambulance — 108",
        "action_number": "108",
        "extra_actions": [
            {"label": "Unified Emergency — 112", "number": "112"},
        ],
    },

    "fire": {
        "reply": (
            "Vehicle fire — get out immediately:\n\n"
            "1. STOP the vehicle and turn off the engine.\n"
            "2. GET EVERYONE OUT immediately — do not collect belongings.\n"
            "3. Move at least 100 metres away from the vehicle.\n"
            "4. Do NOT open the bonnet if smoke is coming from the engine.\n"
            "5. Call 101 (Fire) and 108 (Ambulance) immediately.\n\n"
            "WARNING: Fuel tanks can explode. Distance is your priority."
        ),
        "reply_hi": (
            "Gaadi mein aag — turant niklein:\n\n"
            "1. Gaadi ROKEIN aur engine band karein.\n"
            "2. SABHI KO TURANT nikalein — samaan mat uthaayen.\n"
            "3. Gaadi se kam se kam 100 metre door jaayein.\n"
            "4. Engine se dhuaan aa raha ho toh bonnet mat kholein.\n"
            "5. Turant 101 (Fire) aur 108 (Ambulance) pe call karein.\n\n"
            "CHETA DENA: Fuel tank blast ho sakta hai. Door rehna pehli zaroorat hai."
        ),
        "reply_as": (
            "Gari-t agun — turant beroi yao:\n\n"
            "1. Gari THAMAO aru engine band korok.\n"
            "2. SOKOLOK TURANT beroi diya — jinish-patra niba nuba.\n"
            "3. Gari-r poraa kam se kam 100 mitroot yao.\n"
            "4. Engine-r poraa dhuan asile bonnet nushuubo.\n"
            "5. Turant 101 (Fire) aru 108 (Ambulance) t call korok.\n\n"
            "SATORKOTA: Fuel tank blast hobo pare. Door thoka sab-r aagot."
        ),
        "action_label": "Call Fire — 101",
        "action_number": "101",
        "extra_actions": [
            {"label": "Call Ambulance — 108", "number": "108"},
            {"label": "Call Police — 100", "number": "100"},
        ],
    },

    "lost": {
        "reply": (
            "You appear to be lost or need directions.\n\n"
            "1. Pull over safely before checking your location.\n"
            "2. Your GPS coordinates are being recorded by this app.\n"
            "3. Call 1033 (NHAI helpline) if you are on a national highway — "
            "they can give you directions and milestone information.\n"
            "4. Call 100 (Police) if you feel unsafe.\n\n"
            "Stay on a lit, populated road if possible."
        ),
        "reply_hi": (
            "Aap raasta bhool gaye lagte hain.\n\n"
            "1. Location check karne se pehle safely rok lein.\n"
            "2. Yeh app aapke GPS coordinates record kar raha hai.\n"
            "3. National highway par ho toh 1033 (NHAI) pe call karein — "
            "woh directions aur milestone information de sakte hain.\n"
            "4. Surakshit na lage toh 100 (Police) pe call karein.\n\n"
            "Agar ho sake toh roshni wali aur bheed wali sadak par rahein."
        ),
        "reply_as": (
            "Apuni raasta pahi geche mone hoise.\n\n"
            "1. Location check korar aage suraksit thaimk.\n"
            "2. Ei app-e apunar GPS coordinates record koriche.\n"
            "3. National highway-t asile 1033 (NHAI) t call korok — "
            "tai directions aru milestone information dibo pare.\n"
            "4. Suraksit nolage toh 100 (Police) t call korok.\n\n"
            "Pare hole alokoito aru lokbalai sarak-t thakk."
        ),
        "action_label": "NHAI Helpline — 1033",
        "action_number": "1033",
        "extra_actions": [
            {"label": "Call Police — 100", "number": "100"},
        ],
    },

    # ── NEW INTENTS (added to match backend + fix issues_alokesh_pdf.pdf) ────

    "theft": {
        "reply": (
            "Vehicle theft or robbery reported.\n\n"
            "1. Do NOT chase the thief — your safety comes first.\n"
            "2. Move to a safe, well-lit area immediately.\n"
            "3. Call 100 (Police) and report: your location, vehicle description, "
            "registration number, and direction the thief went.\n"
            "4. Note the time and any identifying features of the person.\n"
            "5. Do not touch or move anything at the scene if possible.\n\n"
            "Stay calm and stay safe."
        ),
        "reply_hi": (
            "Gaadi chori ya loot ki report.\n\n"
            "1. Chor ka peecha mat karein — aapki safety pehle hai.\n"
            "2. Turant safe, roshni wali jagah jaayein.\n"
            "3. 100 (Police) pe call karein aur batayein: location, gaadi ki "
            "jaankari, registration number, chor kis direction mein gaya.\n"
            "4. Samay aur uss vyakti ki koi pehchan note karein.\n"
            "5. Ho sake toh scene par kuch mat chhuein ya hilaayein.\n\n"
            "Shant rahein aur surakshit rahein."
        ),
        "reply_as": (
            "Gari chor ba dakat-i-r khabar.\n\n"
            "1. Doror pishot nayabo — apunar suraksha pratham.\n"
            "2. Turant suraksit, alokoito thailot yao.\n"
            "3. 100 (Police) t call kori janaao: thaan, gari-r biboron, "
            "registration number, dor ki phale goise.\n"
            "4. Somoy aru sei manuh-r kono chinno note korok.\n"
            "5. Pare hole scene-t kichhu nohuwaba ba nashoriba.\n\n"
            "Shant thakk aru suraksit thakk."
        ),
        "action_label": "Call Police — 100",
        "action_number": "100",
        "extra_actions": [
            {"label": "Unified Emergency — 112", "number": "112"},
        ],
    },

    "robbery": {
        "reply": (
            "Robbery or assault in progress.\n\n"
            "1. Do NOT resist if you are threatened — give up valuables to "
            "protect your life.\n"
            "2. Once safe, move to a crowded place immediately.\n"
            "3. Call 100 (Police) or 112 (Emergency) RIGHT AWAY.\n"
            "4. Describe: location, number of attackers, physical description, "
            "direction they went.\n"
            "5. Call 108 if you or anyone is injured.\n\n"
            "Your life is more important than any possession."
        ),
        "reply_hi": (
            "Loot ya hamlaa ho raha hai.\n\n"
            "1. Dhamki milne par VIRODH MAT KAREIN — jaan bachane ke liye "
            "samaan de dein.\n"
            "2. Surakshit hone par turant bheed wali jagah jaayein.\n"
            "3. ABHI 100 (Police) ya 112 (Emergency) pe call karein.\n"
            "4. Batayein: location, hamlaawaron ki sankhya, pehchaan, "
            "kis direction mein gaye.\n"
            "5. Koi ghayaal ho toh 108 pe call karein.\n\n"
            "Kisi bhi cheez se zyada aapki jaan ki keemaat hai."
        ),
        "reply_as": (
            "Dakat ba aagroman hoise.\n\n"
            "1. Bhay dekhuale PORITISODH NIBAO — jeevan bachabo-r karane "
            "dhan-sampatti diya.\n"
            "2. Suraksit holei turant manuh bhaloi thaikia thailot yao.\n"
            "3. EKHONI 100 (Police) ba 112 (Emergency) t call korok.\n"
            "4. Janaao: thaan, aagromonkarir sankhya, chinno, ki phale goise.\n"
            "5. Koyoba aahot hoile 108 t call korok.\n\n"
            "Ekono jinistor sait apunar jeevan beshi daami."
        ),
        "action_label": "Call Police — 100",
        "action_number": "100",
        "extra_actions": [
            {"label": "Unified Emergency — 112", "number": "112"},
            {"label": "Call Ambulance — 108", "number": "108"},
        ],
    },

    "assault": {
        "reply": (
            "Physical assault reported.\n\n"
            "1. Get to a safe place immediately — a petrol station, shop, "
            "or any public place with people.\n"
            "2. Call 100 (Police) or 112 immediately.\n"
            "3. If you are injured, call 108 for an ambulance.\n"
            "4. Try to remember: attacker's description, time, location, "
            "and direction they went.\n"
            "5. Do not wash wounds before medical help arrives — this "
            "preserves evidence.\n\n"
            "You are not alone. Help is coming."
        ),
        "reply_hi": (
            "Shareerik hamlaa ki report.\n\n"
            "1. Turant safe jagah jaayein — petrol station, dukaan ya "
            "koi bhi bheed wali jagah.\n"
            "2. Turant 100 (Police) ya 112 pe call karein.\n"
            "3. Ghayaal ho toh ambulance ke liye 108 pe call karein.\n"
            "4. Yaad rakhein: hamlaawaar ki pehchaan, samay, jagah, "
            "aur woh kis taraf gaya.\n"
            "5. Medical help aane se pehle zakhm mat dhoyen — saboot "
            "surakshit rahenge.\n\n"
            "Aap akele nahi hain. Madad aa rahi hai."
        ),
        "reply_as": (
            "Shareerik aagromon-r khabar.\n\n"
            "1. Turant suraksit thailot yao — petrol station, dukan ba "
            "kono manuh bhaloi thaikia thaan.\n"
            "2. Turant 100 (Police) ba 112 t call korok.\n"
            "3. Aahot hoile ambulance-or karane 108 t call korok.\n"
            "4. Mone rakhk: aagromonkarir chinno, somoy, thaan, "
            "aru ki phale goise.\n"
            "5. Medical help nohowalo-ika ghao nidhuibo — saaksho surakshit thakib.\n\n"
            "Apuni ekela nohay. Sahajyo ashise."
        ),
        "action_label": "Call Police — 100",
        "action_number": "100",
        "extra_actions": [
            {"label": "Call Ambulance — 108", "number": "108"},
            {"label": "Unified Emergency — 112", "number": "112"},
        ],
    },

    "suspicious_activity": {
        "reply": (
            "Suspicious activity reported.\n\n"
            "1. Do not confront the person — keep your distance.\n"
            "2. Move to a safe location.\n"
            "3. Call 100 (Police) and describe:\n"
            "   — What you saw (people, vehicle, actions)\n"
            "   — Exact location and time\n"
            "   — Any registration numbers or descriptions\n"
            "4. Call 112 if you feel in immediate danger.\n\n"
            "Trust your instincts — reporting is always the right call."
        ),
        "reply_hi": (
            "Shak-shubha gatividdhi ki report.\n\n"
            "1. Us vyakti se PANGA MAT LEIN — door rahein.\n"
            "2. Safe jagah par jaayein.\n"
            "3. 100 (Police) pe call karein aur batayein:\n"
            "   — Kya dekha (log, gaadi, harkaat)\n"
            "   — Sahi location aur samay\n"
            "   — Koi registration number ya pehchaan\n"
            "4. Agar turant khatara ho toh 112 pe call karein.\n\n"
            "Apni zubaan pe bharosa karein — report karna hamesha sahi hai."
        ),
        "reply_as": (
            "Shankajanak gotibidhir khabar.\n\n"
            "1. Sei manuh-r sait JHOGRA NIBAO — door thakk.\n"
            "2. Suraksit thailot yao.\n"
            "3. 100 (Police) t call kori janaao:\n"
            "   — Ki dekhilu (manuh, gari, kaaj)\n"
            "   — Sathik thaan aru somoy\n"
            "   — Kono registration number ba chinno\n"
            "4. Turant bhoyo lagile 112 t call korok.\n\n"
            "Nija manor kathata biswaas koribo — report kora somiyo-r sathik kaaj."
        ),
        "action_label": "Call Police — 100",
        "action_number": "100",
        "extra_actions": [
            {"label": "Unified Emergency — 112", "number": "112"},
        ],
    },

    "flood": {
        "reply": (
            "Flood warning — take immediate action:\n\n"
            "1. Move to HIGHER GROUND immediately. Do not wait.\n"
            "2. Do NOT attempt to drive through flooded roads — "
            "even 15 cm of water can sweep a car.\n"
            "3. Call 108 (NDRF Disaster) or 112 for rescue.\n"
            "4. Turn off electricity at the mains if you can do so safely.\n"
            "5. Take essential documents, medicines, and charge your phone.\n"
            "6. Inform family and neighbours.\n\n"
            "Assam SDMA: 0361-2237219"
        ),
        "reply_hi": (
            "Baaadh ki chetaavni — turant kadam uthaayen:\n\n"
            "1. ABHI OONCHI JAGAH par jaayein. Intezaar mat karein.\n"
            "2. Baarish mein bhi saDki sadak par gaadi mat chalaayein — "
            "15 cm paani bhi gaadi baha sakta hai.\n"
            "3. Rescue ke liye 108 (NDRF) ya 112 pe call karein.\n"
            "4. Safely ho sake toh bijli ka main switch band karein.\n"
            "5. Zaroori documents, dawaaiyaan le lein aur phone charge karein.\n"
            "6. Parivar aur padosiyon ko bataayein.\n\n"
            "Assam SDMA: 0361-2237219"
        ),
        "reply_as": (
            "Boniya satorkota — turant kadam lo:\n\n"
            "1. EKHONI UCHHO THAILOT yao. Apeksha nibao.\n"
            "2. Boniyai sarak-t gari nuchalaabo — 15 cm pani-teo gari "
            "bhasi jab.\n"
            "3. Uddhaar-or karane 108 (NDRF) ba 112 t call korok.\n"
            "4. Suraksit hole bijolir main switch band korok.\n"
            "5. Dorkari kaagoj-patra, biyad lobok aru phone charge korok.\n"
            "6. Poriyal aru jilonaghori-k khabor diya.\n\n"
            "Assam SDMA: 0361-2237219"
        ),
        "action_label": "Disaster Helpline — 108",
        "action_number": "108",
        "extra_actions": [
            {"label": "Unified Emergency — 112", "number": "112"},
            {"label": "Assam SDMA — 0361-2237219", "number": "03612237219"},
        ],
    },

    "landslide": {
        "reply": (
            "Landslide reported — this is critical in Assam/NE India:\n\n"
            "1. MOVE AWAY from the slide path and slope immediately.\n"
            "2. If driving, DO NOT attempt to pass — turn back.\n"
            "3. Call 108 (NDRF) or 112 for rescue teams.\n"
            "4. Call 1033 (NHAI) to report the blocked highway.\n"
            "5. Warn other drivers by turning on hazard lights.\n"
            "6. Move to high, stable ground and await rescue.\n\n"
            "Do not re-enter the area until authorities declare it safe."
        ),
        "reply_hi": (
            "Bhookhislaav ki report — Assam/NE India mein yeh bahut zaroori hai:\n\n"
            "1. TURANT slide path aur dhaalon se door ho jaayein.\n"
            "2. Gaadi chlaa rahe ho toh AAGE MAT BADHO — vaapis lo.\n"
            "3. Rescue team ke liye 108 (NDRF) ya 112 pe call karein.\n"
            "4. Blocked highway report karne ke liye 1033 (NHAI) pe call karein.\n"
            "5. Hazard lights chalu karke doosre drivers ko saavadhaan karein.\n"
            "6. Oonche, stable zameen par jaayein aur rescue ka intezaar karein.\n\n"
            "Jab tak authorities safe nahi kehte, area mein wapis mat jaayein."
        ),
        "reply_as": (
            "Bhuhukhola-r khabar — Assam/NE India-t ei ati guruttopurno:\n\n"
            "1. TURANT slide path aru dhal-r poraa soriya yao.\n"
            "2. Gari chalailat asile AGOBO NIBAO — ghuri ao.\n"
            "3. Uddhaar dal-or karane 108 (NDRF) ba 112 t call korok.\n"
            "4. Bondh highway report korar karane 1033 (NHAI) t call korok.\n"
            "5. Hazard light jalaai anya driver-k satorkota diya.\n"
            "6. Uchhu, sthir maati-t yao aru uddhaar-or opeksha korok.\n\n"
            "Jotrikhon adhikorihoi-e suraksit nabhabe, sei thailot nayabo."
        ),
        "action_label": "Disaster Helpline — 108",
        "action_number": "108",
        "extra_actions": [
            {"label": "Highway Helpline — 1033", "number": "1033"},
            {"label": "Unified Emergency — 112", "number": "112"},
        ],
    },

    "earthquake": {
        "reply": (
            "Earthquake — drop, cover, and hold:\n\n"
            "1. If INSIDE: DROP to knees, take COVER under a table or "
            "against an interior wall, HOLD ON until shaking stops.\n"
            "2. If OUTSIDE: move away from buildings, trees, and power lines.\n"
            "3. If DRIVING: pull over away from bridges or overpasses. "
            "Stay in the vehicle.\n"
            "4. After shaking stops, check for injuries and hazards (gas leaks, fire).\n"
            "5. Call 108 for injuries, 112 for rescue.\n\n"
            "Expect aftershocks. Stay away from damaged structures."
        ),
        "reply_hi": (
            "Bhookamp — giro, chhipo, aur pakdo:\n\n"
            "1. ANDAR ho toh: Ghutno pe GIR JAAO, mez ke neechhe ya "
            "andar ki deewar ke paas CHHUPO, jhatkhe rukne tak PAKDE RAHO.\n"
            "2. BAAHAR ho toh: imaarat, ped aur bijli ke khambon se door ho jaao.\n"
            "3. GAADI CHLAA RAHE HO: pool ya overpass se door ruk jaao. "
            "Gaadi mein hi rahein.\n"
            "4. Jhatka rukne ke baad, chot aur khatare (gas leak, aag) check karein.\n"
            "5. Chot ke liye 108, rescue ke liye 112 pe call karein.\n\n"
            "Aftershock aa sakte hain. Nuksaan wali imaartton se door rahein."
        ),
        "reply_as": (
            "Bhumikomp — dharo, dhako, aru dhoro:\n\n"
            "1. BHITORT asile: ghunduli-t DHARO, table-r tale ba "
            "bhitorer bhitti-r kase DHAKO, joluni narutolaloika DHORI THAKK.\n"
            "2. BAAHIROT asile: ghor, gachh aru bijolir khambal-r poraa soro.\n"
            "3. GARI CHALAILAT asile: pool ba overpass-r poraa aahi thaimk. "
            "Gari-r bhitortei thakk.\n"
            "4. Joluni rutolai, ghaw aru bipod (gas leak, agun) check korok.\n"
            "5. Ghaw-or karane 108, uddhaar-or karane 112 t call korok.\n\n"
            "Aftershock aahibo pare. Khotikgrastha ghor-r poraa doribo."
        ),
        "action_label": "Call Ambulance — 108",
        "action_number": "108",
        "extra_actions": [
            {"label": "Unified Emergency — 112", "number": "112"},
        ],
    },

    # ── IMPROVED "other" template ─────────────────────────────────────────────
    # Old: "describe your emergency clearly" — weak UX in panic
    # New: give immediate numbers + guide with specific keywords
    "other": {
        "reply": (
            "I am here to help. If someone is injured or in danger:\n\n"
            "• Ambulance: 108\n"
            "• Police: 100\n"
            "• Fire: 101\n"
            "• Highway (NHAI): 1033\n"
            "• Unified Emergency: 112\n\n"
            "Reply with one of these words for faster help:\n"
            "accident · fire · breakdown · bleeding · theft ·\n"
            "unconscious · tyre burst · flood · landslide"
        ),
        "reply_hi": (
            "Main madad ke liye yahan hoon. Agar koi ghayaal hai ya khatara hai:\n\n"
            "• Ambulance: 108\n"
            "• Police: 100\n"
            "• Aag: 101\n"
            "• Highway (NHAI): 1033\n"
            "• Unified Emergency: 112\n\n"
            "Jaldi madad ke liye in mein se ek shabd type karein:\n"
            "durghatna · aag · gaadi kharab · khoon · chori ·\n"
            "behosh · tyre burst · baaad · bhookhislaav"
        ),
        "reply_as": (
            "Ami sahajyo korar karane iyat ase. Koyoba aahot hoile ba bhoyo lagile:\n\n"
            "• Ambulance: 108\n"
            "• Police: 100\n"
            "• Agun: 101\n"
            "• Highway (NHAI): 1033\n"
            "• Unified Emergency: 112\n\n"
            "Shighroi sahajyo-r karane ei shabd-r ekta type korok:\n"
            "durghotona · agun · gari kharab · rokto · chor ·\n"
            "unconscious · tyre burst · boniya · bhuhukhola"
        ),
        "action_label": "Unified Emergency — 112",
        "action_number": "112",
        "extra_actions": [
            {"label": "Call Ambulance — 108", "number": "108"},
            {"label": "Call Police — 100", "number": "100"},
        ],
    },
}


def get_template(intent: str, lang: str = "en") -> Template:
    """
    Return the offline template for a given intent. Defaults to 'other'.

    Args:
        intent: One of the intent strings defined in TEMPLATES.
        lang:   Language code — 'en' (default), 'hi' (Hindi), 'as' (Assamese).
                If a non-English reply is requested but not available,
                falls back to the English reply automatically.

    Returns:
        A Template dict. The 'reply' field is set to the language-specific
        response so callers don't need to know the field names.
    """
    template = TEMPLATES.get(intent, TEMPLATES["other"])

    if lang == "hi" and template.get("reply_hi"):
        # Return a copy with 'reply' set to Hindi text
        return {**template, "reply": template["reply_hi"]}
    if lang == "as" and template.get("reply_as"):
        return {**template, "reply": template["reply_as"]}

    return template