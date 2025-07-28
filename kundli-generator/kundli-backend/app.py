from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
import datetime, pytz

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

@app.route('/api/kundli', methods=['POST'])
def kundli():
    data = request.json
    # Extract birth details
    birth_date = data['date']         # 'YYYY-MM-DD'
    birth_time = data['time']         # 'HH:MM'
    birth_lat  = float(data['lat'])
    birth_lon  = float(data['lon'])
    birth_tz   = float(data['tz'])    # e.g. 5.5

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

    # Calculate ascendant (Lagna) sign
    cusps, ascmc = swe.houses(jd, birth_lat, birth_lon, b'P')
    asc_deg = (ascmc[0] - ayanamsa) % 360
    asc_sign = signs[int(asc_deg // 30)]

    # House descriptions
    house_descriptions = {
        1: "Self, body, appearance, personality",
        2: "Wealth, family, speech, possessions",
        3: "Siblings, courage, communication",
        4: "Mother, home, property, emotions",
        5: "Children, creativity, education",
        6: "Enemies, debts, health, service",
        7: "Marriage, spouse, partnerships",
        8: "Death, transformation, occult",
        9: "Luck, dharma, higher learning",
        10: "Career, status, public life",
        11: "Gains, friends, aspirations",
        12: "Losses, expenses, spirituality"
    }

    # Return as JSON
    return jsonify({
        'sign_planets': sign_planets,
        'positions': positions,
        'asc_sign': asc_sign,
        'house_descriptions': house_descriptions
    })

if __name__ == '__main__':
    app.run(debug=True)
