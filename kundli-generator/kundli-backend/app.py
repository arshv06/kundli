from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
import datetime, pytz
import requests
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import time

# Load environment variables from possible env files in priority order
base_dir = os.path.dirname(__file__)
for fname in ('yay.env', '.env', 'env.example'):
    load_dotenv(dotenv_path=os.path.join(base_dir, fname), override=False)

# Simple in-memory cooldown to avoid hitting free-tier rate limits
AI_COOLDOWN_SECONDS = int(os.getenv('AI_COOLDOWN_SECONDS', '30'))  # default 20s
_last_ai_call_ts = 0.0

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

def calculate_navamsa(positions: dict) -> dict:
    """Calculate D9 (Navamsa) chart from D1 positions"""
    navamsa_positions = {}
    
    for planet, degree in positions.items():
        if planet in ['Ra', 'Ke']:  # Rahu/Ketu don't have navamsa
            navamsa_positions[planet] = degree
            continue
            
        # Navamsa calculation: divide each sign into 9 parts
        sign_num = int(degree // 30)
        degree_in_sign = degree % 30
        
        # Each navamsa is 3°20' (3.333... degrees)
        navamsa_num = int(degree_in_sign // 3.333333)
        
        # Calculate new position in navamsa
        # Each sign is divided into 9 parts, each part corresponds to a sign
        navamsa_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Fire signs: Aries, Leo, Sagittarius (0, 4, 8)
        # Earth signs: Taurus, Virgo, Capricorn (1, 5, 9)
        # Air signs: Gemini, Libra, Aquarius (2, 6, 10)
        # Water signs: Cancer, Scorpio, Pisces (3, 7, 11)
        
        element_start = (sign_num % 4) * 3  # 0, 3, 6, 9
        navamsa_sign_index = element_start + navamsa_num
        navamsa_sign_index = navamsa_sign_index % 12
        
        # Calculate degree within the navamsa sign
        navamsa_degree = (degree_in_sign % 3.333333) * 9  # Convert to degree in new sign
        
        # Convert to absolute degree
        navamsa_positions[planet] = navamsa_sign_index * 30 + navamsa_degree
    
    return navamsa_positions

@app.route('/api/kundli', methods=['POST'])
def kundli():
    data = request.json
    # Extract birth details
    birth_date = data['date']         # 'YYYY-MM-DD'
    birth_time = data['time']         # 'HH:MM'
    birth_lat  = float(data['lat'])
    birth_lon  = float(data['lon'])
    birth_tz   = float(data['tz'])    # e.g. 5.5
    chart_type = data.get('chart_type', 'regular')  # 'regular' or 'd9'
    
    # Load dataset
    import json
    import os
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'dataset.json')
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        dataset = {}

    # Convert to UTC
    y, m, d = map(int, birth_date.split('-'))
    hour, minute = map(int, birth_time.split(':'))
    dt = datetime.datetime(y, m, d, hour, minute)
    dt_utc = dt - datetime.timedelta(hours=birth_tz)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)

    # Calculate planets (now including Uranus, Neptune, Pluto)
    planets = {
        'Su': swe.SUN, 'Mo': swe.MOON, 'Ma': swe.MARS,
        'Me': swe.MERCURY, 'Ju': swe.JUPITER, 'Ve': swe.VENUS,
        'Sa': swe.SATURN, 'Ra': swe.MEAN_NODE,
        'Ur': swe.URANUS, 'Ne': swe.NEPTUNE, 'Pl': swe.PLUTO
    }
    ayanamsa = swe.get_ayanamsa(jd)
    positions = {}
    speeds = {}
    for name, pl in planets.items():
        lon, lat, dist, speed_long, speed_lat, speed_dist = swe.calc_ut(jd, pl)[0]
        lon = (lon - ayanamsa) % 360
        positions[name] = lon
        speeds[name] = speed_long
    positions['Ke'] = (positions['Ra'] + 180) % 360
    speeds['Ke'] = 0

    # If D9 chart requested, calculate navamsa positions
    if chart_type == 'd9':
        positions = calculate_navamsa(positions)

    # Calculate ascendant
    if chart_type == 'regular':
        # For D1, calculate actual ascendant
        cusps, ascmc = swe.houses(jd, birth_lat, birth_lon, b'P')
        asc_lon = (ascmc[0] - ayanamsa) % 360
    else:
        # For D9, calculate navamsa ascendant from D1 ascendant
        cusps, ascmc = swe.houses(jd, birth_lat, birth_lon, b'P')
        d1_asc = (ascmc[0] - ayanamsa) % 360
        # Convert D1 ascendant to D9
        asc_sign_num = int(d1_asc // 30)
        asc_deg_in_sign = d1_asc % 30
        asc_navamsa_num = int(asc_deg_in_sign // 3.333333)
        
        # Calculate D9 ascendant sign
        element_start = (asc_sign_num % 4) * 3  # 0, 3, 6, 9
        d9_asc_sign_index = element_start + asc_navamsa_num
        d9_asc_sign_index = d9_asc_sign_index % 12
        
        # Calculate degree within the D9 ascendant sign
        d9_asc_degree = (asc_deg_in_sign % 3.333333) * 9
        
        # Convert to absolute degree
        asc_lon = d9_asc_sign_index * 30 + d9_asc_degree

    # Sign info
    signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio',
             'Sagittarius','Capricorn','Aquarius','Pisces']
    def zodiac_sign(deg): return signs[int(deg//30)]

    # Exaltation/Debility info
    exaltation_debilitation = {
        'Su': [('Aries', 10), ('Libra', 10)],
        'Mo': [('Taurus', 3), ('Scorpio', 3)],
        'Ma': [('Capricorn', 28), ('Cancer', 28)],
        'Me': [('Virgo', 15), ('Pisces', 15)],
        'Ju': [('Cancer', 5), ('Capricorn', 5)],
        'Ve': [('Pisces', 27), ('Virgo', 27)],
        'Sa': [('Libra', 20), ('Aries', 20)],
    }

    # Combustion orbits (approximate, in degrees)
    combust_orbits = {
        'Mo': 12, 'Ma': 17, 'Me': 14, 'Ju': 11, 'Ve': 10, 'Sa': 15
    }

    # Sun degree for combustion
    sun_deg = positions['Su']

    # Build sign_planets with details
    sign_planets = {sign: [] for sign in signs}
    for name, deg in positions.items():
        sign = zodiac_sign(deg)
        deg_in_sign = deg % 30
        status = []
        # Exaltation/Debility
        if name in exaltation_debilitation:
            exalt_sign, exalt_deg = exaltation_debilitation[name][0]
            debil_sign, debil_deg = exaltation_debilitation[name][1]
            if sign == exalt_sign:
                status.append("exalted")
                if abs(deg_in_sign - exalt_deg) <= 5:
                    status.append("peak")
            elif sign == debil_sign:
                status.append("debilitated")
                if abs(deg_in_sign - debil_deg) <= 5:
                    status.append("peak")
        # Combustion
        if name != 'Su' and name in combust_orbits:
            diff = abs((deg - sun_deg + 180) % 360 - 180)
            if diff < combust_orbits[name]:
                status.append("combust")
        # Retrograde
        if speeds.get(name, 0) < 0:
            status.append("retrograde")
        sign_planets[sign].append({
            'name': name,
            'deg': round(deg_in_sign, 1),
            'sign': sign,
            'status': status
        })

    # House descriptions
    house_descriptions = {
        1: "Self, personality, appearance, health, vitality",
        2: "Wealth, family, speech, face, right eye, food habits",
        3: "Siblings, courage, short journeys, communication, hands",
        4: "Mother, home, property, vehicles, comfort, happiness",
        5: "Children, intelligence, creativity, romance, speculation",
        6: "Enemies, diseases, debts, obstacles, service, pets",
        7: "Spouse, marriage, partnerships, business, foreign travel",
        8: "Longevity, death, transformation, occult, inheritance",
        9: "Father, guru, religion, higher education, fortune",
        10: "Career, profession, authority, government, reputation",
        11: "Income, gains, elder siblings, friends, social circle",
        12: "Expenses, losses, foreign lands, spirituality, sleep"
    }

    # Calculate house strengths and colors
    house_strengths = {}
    
    # Calculate aspects for strength analysis
    def get_aspects_to_house(target_house):
        aspects_to_house = []
        for sign, plist in sign_planets.items():
            house_num = ((signs.index(sign) - signs.index(zodiac_sign(asc_lon))) % 12) + 1
            for p in plist:
                planet = p['name']
                # Get aspects for this planet
                if planet in ['Su', 'Mo', 'Ma', 'Me', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke']:
                    aspect_rules = {
                        'Su': [6], 'Mo': [6], 'Ma': [3, 6, 7], 'Me': [6], 'Ju': [4, 6, 8], 'Ve': [6],
                        'Sa': [2, 6, 9], 'Ra': [4, 6, 8], 'Ke': [4, 6, 8]
                    }
                    
                    for offset in aspect_rules.get(planet, []):
                        target_house_num = ((house_num + offset - 1) % 12) + 1
                        if target_house_num == target_house:
                            # Determine aspect nature
                            if planet in ['Ju', 'Ve', 'Mo']:
                                aspect_nature = 'benefic'
                            elif planet in ['Ma', 'Sa', 'Ra', 'Ke']:
                                aspect_nature = 'malefic'
                            else:
                                aspect_nature = 'neutral'
                            aspects_to_house.append({'planet': planet, 'nature': aspect_nature})
        return aspects_to_house
    
    for house_num in range(1, 13):
        house_sign = signs[(house_num - 1) % 12]
        house_planets = sign_planets.get(house_sign, [])
        aspects_to_house = get_aspects_to_house(house_num)
        
        # Calculate strength based on planets and aspects
        strength = 0
        total_influence = 0
        
        # Analyze planets in the house
        for planet in house_planets:
            planet_name = planet['name']
            is_exalted = 'exalted' in planet.get('status', [])
            is_debilitated = 'debilitated' in planet.get('status', [])
            is_combust = 'combust' in planet.get('status', [])
            is_retrograde = 'retrograde' in planet.get('status', [])
            
            # Base strength based on planet nature
            if planet_name in ['Ju', 'Ve', 'Mo']:  # Benefics
                planet_strength = 1.5 if is_exalted else -0.5 if is_debilitated else 0.8
            elif planet_name in ['Ma', 'Sa', 'Ra', 'Ke']:  # Malefics
                planet_strength = 0.5 if is_exalted else -1.5 if is_debilitated else -0.8
            else:  # Neutral (Sun, Mercury)
                planet_strength = 1.0 if is_exalted else -1.0 if is_debilitated else 0.2
            
            # Adjust for combustion and retrograde
            if is_combust:
                planet_strength *= 0.5
            if is_retrograde:
                planet_strength *= 0.8
            
            strength += planet_strength
            total_influence += 1
        
        # Analyze aspects to the house
        for aspect in aspects_to_house:
            aspect_strength = 0.3 if aspect['nature'] == 'benefic' else -0.3 if aspect['nature'] == 'malefic' else 0
            strength += aspect_strength
            total_influence += 1
        
        # Normalize strength
        avg_strength = strength / total_influence if total_influence > 0 else 0
        
        # Debug: Print strength values
        print(f"House {house_num} ({house_sign}): strength={strength}, total_influence={total_influence}, avg_strength={avg_strength:.3f}")
        
        # Adjust thresholds to be more realistic
        if avg_strength >= 0.2:  # Lowered from 0.5
            house_strengths[house_num] = {'strength': 'strong', 'color': '#90EE90'}
        elif avg_strength <= -0.2:  # Lowered from -0.5
            house_strengths[house_num] = {'strength': 'weak', 'color': '#FFB6C1'}
        else:
            house_strengths[house_num] = {'strength': 'neutral', 'color': '#FFD700'}

    # Return as JSON
    return jsonify({
        'sign_planets': sign_planets,
        'positions': positions,
        'asc_sign': zodiac_sign(asc_lon),
        'house_descriptions': house_descriptions,
        'house_strengths': house_strengths,
        'dataset': dataset
    })

@app.route('/api/ai-analysis', methods=['POST'])
def ai_analysis():
    global _last_ai_call_ts
    # Simple cooldown check
    now_ts = time.time()
    if now_ts - _last_ai_call_ts < AI_COOLDOWN_SECONDS:
        wait_sec = int(AI_COOLDOWN_SECONDS - (now_ts - _last_ai_call_ts))
        return jsonify({'response': f'Please wait {wait_sec}s before asking another question.', 'cooldown': wait_sec})
    _last_ai_call_ts = now_ts

    data = request.json
    question = data.get('question', '')
    kundli_data = data.get('kundli_data', {})
    
    # Hugging Face AI API call
    def call_ai_api():
        """Call the Hugging Face text-generation inference API"""
        try:
            hf_token = os.getenv('HUGGING_FACE_TOKEN')
            model_name = os.getenv('HF_MODEL', 'tiiuae/falcon-rw-1b')

            if not hf_token:
                print("Hugging Face token not found. Set HUGGING_FACE_TOKEN in .env")
                return None

            client = InferenceClient(model_name, token=hf_token)

            user_name = data.get('user_name', 'friend')

            # Build readable planet placements with houses
            signs_list = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
            sign_to_idx = {s: i for i, s in enumerate(signs_list)}
            asc_idx = sign_to_idx.get(kundli_data.get('asc_sign', 'Aries'), 0)
            placement_lines = []
            for sign, plist in kundli_data.get('sign_planets', {}).items():
                house_num = ((sign_to_idx.get(sign, 0) - asc_idx) % 12) + 1
                for p in plist:
                    status = ', '.join(p.get('status', [])) or 'normal'
                    # Fix Venus in Pisces - it's always exalted
                    if p['name'] == 'Ve' and sign == 'Pisces':
                        status = 'exalted'
                    placement_lines.append(f"{p['name']} – {sign} sign, house {house_num}, {p['deg']}°, status: {status}")
            placements_text = "\n".join(placement_lines)

            # Build aspects data
            aspects_data = []
            for sign, plist in kundli_data.get('sign_planets', {}).items():
                house_num = ((sign_to_idx.get(sign, 0) - asc_idx) % 12) + 1
                for p in plist:
                    planet = p['name']
                    # Get aspects for this planet
                    if planet in ['Su', 'Mo', 'Ma', 'Me', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'Ur', 'Ne', 'Pl']:
                        aspect_rules = {
                            'Su': [6], 'Mo': [6], 'Ma': [3, 6, 7], 'Me': [6], 'Ju': [4, 6, 8], 'Ve': [6],
                            'Sa': [2, 6, 9], 'Ra': [4, 6, 8], 'Ke': [4, 6, 8], 'Ur': [6], 'Ne': [6], 'Pl': [6]
                        }
                        aspect_labels = {2: '3rd', 3: '4th', 4: '5th', 6: '7th', 7: '8th', 8: '9th', 9: '10th'}
                        
                        for offset in aspect_rules.get(planet, []):
                            target_house = ((house_num + offset - 1) % 12) + 1
                            aspect_type = aspect_labels.get(offset, f'{offset}th')
                            aspects_data.append(f"{planet} {aspect_type} aspect to House {target_house}")

            aspects_text = "\n".join(aspects_data) if aspects_data else "None"

            prompt = f""" 
You are Chat-Jyotish — a sharp, compassionate Vedic astrologer.

Your role is to guide {user_name} using their birth chart with warmth, clarity, and spiritual insight. Speak directly to them using “you” and “your.” Avoid technical jargon unless it's meaningful. Never refer to yourself or the user in the third person.

Your answer must:
• Stay focused on the chart and the user’s question.
• Use the provided planetary placements and aspects meaningfully.
• Highlight the most important 2–3 insights.
• Be emotionally attuned but concise — no fluff or vague lines.
• Limit your answer to 180 words (about 3–5 short, clear paragraphs).
• Do **not** repeat the question or suggest follow-ups.

KUNDLI SNAPSHOT
---------------
Ascendant (Lagna): {kundli_data.get('asc_sign')}
Chart Type        : {kundli_data.get('chart_type')}

Planet Placements:
{placements_text}

Planetary Aspects:
{aspects_text}

QUESTION
--------
{question}

Give an insightful, direct Vedic astrology interpretation that speaks to {user_name}'s inner life and outer path.
"""

            try:
                response_text = client.text_generation(
                    prompt=prompt,
                    max_new_tokens=150,
                    temperature=0.3,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            except Exception as gen_err:
                # Fallback for models that use the conversational/chat task
                print(f"text_generation failed: {gen_err}. Trying chat_completion...")
                print(f"Model: {model_name}")
                print(f"Error details: {str(gen_err)}")
                try:
                    chat_resp = client.chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=330,
                        temperature=0.2,
                        top_p=0.85
                    )
                    # chat_completion returns an object with .choices[0].message.content
                    response_text = getattr(chat_resp.choices[0].message, 'content', str(chat_resp))
                except Exception as chat_err:
                    print(f"chat_completion also failed: {chat_err}")
                    print(f"Chat error details: {str(chat_err)}")
                    return None
            # Clean up the response to remove unwanted content
            if response_text:
                # Remove any conversation tags or follow-up content
                lines = response_text.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith('[/') and not line.startswith('USER') and not line.startswith('ASS'):
                        cleaned_lines.append(line)
                    if line.startswith('[/') or line.startswith('[USER') or line.startswith('[ASS'):
                        break
                
                response_text = '\n'.join(cleaned_lines)
                
               
            return response_text
        except Exception as e:
            print(f"AI API exception: {e}")
            return None

  
    # Call AI API
    ai_response = call_ai_api()
    if ai_response:
        return jsonify({'response': ai_response})
    else:
        return jsonify({'response': 'AI service is currently unavailable. Please check your API key and internet connection.'})

if __name__ == '__main__':
    app.run(debug=True)
