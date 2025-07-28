import swisseph as swe
import datetime, pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import numpy as np

birth_date = '1998-05-06'
birth_time = '09:20:00'
birth_lat  = 30.7167
birth_lon  = 76.8833
birth_tz   = 'Asia/Kolkata'

swe.set_sid_mode(swe.SIDM_LAHIRI)

y, m, d = map(int, birth_date.split('-'))
hour, minute, second = map(int, birth_time.split(':'))
tz = pytz.timezone(birth_tz)
dt_local = tz.localize(datetime.datetime(y, m, d, hour, minute, second))
dt_utc = dt_local.astimezone(pytz.utc)

jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)

planets = {
    'Su': swe.SUN, 'Mo': swe.MOON, 'Ma': swe.MARS,
    'Me': swe.MERCURY, 'Ju': swe.JUPITER, 'Ve': swe.VENUS,
    'Sa': swe.SATURN, 'Ra': swe.MEAN_NODE,
    'Ur': swe.URANUS, 'Ne': swe.NEPTUNE, 'Pl': swe.PLUTO
}

exaltation_debilitation = {
    'Su': [('Aries', 10), ('Libra', 10)],
    'Mo': [('Taurus', 3), ('Scorpio', 3)],
    'Ma': [('Capricorn', 28), ('Cancer', 28)],
    'Me': [('Virgo', 15), ('Pisces', 15)],
    'Ju': [('Cancer', 5), ('Capricorn', 5)],
    'Ve': [('Pisces', 27), ('Virgo', 27)],
    'Sa': [('Libra', 20), ('Aries', 20)],
}

sign_rulers = {
    'Aries': 'Ma', 'Taurus': 'Ve', 'Gemini': 'Me', 'Cancer': 'Mo',
    'Leo': 'Su', 'Virgo': 'Me', 'Libra': 'Ve', 'Scorpio': 'Ma',
    'Sagittarius': 'Ju', 'Capricorn': 'Sa', 'Aquarius': 'Sa', 'Pisces': 'Ju'
}

planet_friends = {
    'Su': {'friends': ['Mo', 'Ma', 'Ju'], 'enemies': ['Sa', 'Ve'], 'neutral': ['Me']},
    'Mo': {'friends': ['Su', 'Me'], 'enemies': ['Ra', 'Ke'], 'neutral': ['Ma', 'Ju', 'Ve', 'Sa']},
    'Ma': {'friends': ['Su', 'Mo', 'Ju'], 'enemies': ['Me'], 'neutral': ['Ve', 'Sa']},
    'Me': {'friends': ['Su', 'Ve'], 'enemies': ['Mo'], 'neutral': ['Ma', 'Ju', 'Sa']},
    'Ju': {'friends': ['Su', 'Mo', 'Ma'], 'enemies': ['Ve', 'Me'], 'neutral': ['Sa']},
    'Ve': {'friends': ['Me', 'Sa'], 'enemies': ['Su', 'Mo'], 'neutral': ['Ma', 'Ju']},
    'Sa': {'friends': ['Me', 'Ve'], 'enemies': ['Su', 'Mo'], 'neutral': ['Ma', 'Ju']},
    'Ra': {'friends': [], 'enemies': [], 'neutral': []},
    'Ke': {'friends': [], 'enemies': [], 'neutral': []},
}

positions = {}
ayanamsa = swe.get_ayanamsa(jd)

for name, pl in planets.items():
    lon, lat, dist, speed_long, speed_lat, speed_dist = swe.calc_ut(jd, pl)[0]
    lon = (lon - ayanamsa) % 360
    positions[name] = lon
positions['Ke'] = (positions['Ra'] + 180) % 360

cusps, ascmc = swe.houses(jd, birth_lat, birth_lon, b'P')
asc_tropical = ascmc[0]
asc_sidereal = (asc_tropical - ayanamsa) % 360

signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio',
         'Sagittarius','Capricorn','Aquarius','Pisces']

def zodiac_sign(deg): return signs[int(deg//30)]
asc_sign = zodiac_sign(asc_sidereal)
lagna_idx = signs.index(asc_sign)

house_signs = {}
for h in range(1, 13):
    house_signs[h] = signs[(lagna_idx + h - 1) % 12]

sign_planets = {sign: [] for sign in signs}

sun_deg = positions['Su']

for name, deg in positions.items():
    sign = zodiac_sign(deg)
    deg_in_sign = deg % 30

    # Retrograde check
    if name != 'Ke':
        speed = swe.calc_ut(jd, planets.get(name, swe.SUN))[0][3]
    else:
        speed = 0
    status = ''
    if speed < 0:
        status += ' Ret'

    # Exaltation / Debilitation check
    if name in exaltation_debilitation:
        exalt_sign, exalt_deg = exaltation_debilitation[name][0]
        debil_sign, debil_deg = exaltation_debilitation[name][1]
        if sign == exalt_sign:
            status = "Ex"
            if abs(deg_in_sign - exalt_deg) <= 5:
                status += "(Peak)"
        elif sign == debil_sign:
            status = "Deb"
            if abs(deg_in_sign - debil_deg) <= 5:
                status += "(Peak)"

    # Combustion check
    if name != 'Su':
        diff = abs((deg - sun_deg + 180) % 360 - 180)
        if diff < 8:
            status += ' Comb'

    # Dignity check
    if name in planet_friends:
        sign_lord = sign_rulers[sign]
        if sign_lord == name:
            dignity = "Own"
        elif sign_lord in planet_friends[name]['friends']:
            dignity = "Friend"
        elif sign_lord in planet_friends[name]['neutral']:
            dignity = "Neutral"
        elif sign_lord in planet_friends[name]['enemies']:
            dignity = "Enemy"
        else:
            dignity = "N/A"
    else:
        dignity = "N/A"

    display = f"{name} ({deg_in_sign:.1f}°{', ' + status.strip() if status else ''}{', ' + dignity})"
    sign_planets[sign].append(display)

# Plotting
fig = go.Figure()
diamond_x = [0, 10, 10, 0, 0]
diamond_y = [0, 0, 10, 10, 0]
fig.add_trace(go.Scatter(x=diamond_x, y=diamond_y, mode='lines', line=dict(color='white')))
fig.add_trace(go.Scatter(x=[5, 0, 5, 10, 5], y=[10, 5, 0, 5, 10], mode='lines', line=dict(color='white')))
fig.add_trace(go.Scatter(x=[0, 10], y=[0, 10], mode='lines', line=dict(color='white')))
fig.add_trace(go.Scatter(x=[0, 10], y=[10, 0], mode='lines', line=dict(color='white')))

coords = {1: (5, 9), 2: (2.5, 9.5), 3: (0.6, 8.3), 4: (2.5, 6.3), 5: (0.6, 3.3), 6: (2.5, 1.3),
          7: (5, 4), 8: (7.5, 1.3), 9: (9.3, 3.3), 10: (7.5, 6.3), 11: (9.3, 8.3), 12: (7.5, 9.5)}

house_descriptions = {1: "Lagna/Ascendant: Personality, appearance, self.", 2: "Finances, possessions, values, speech.",
                      3: "Communication, siblings, short trips.", 4: "Home, family, roots, emotions.",
                      5: "Creativity, romance, children, joy.", 6: "Health, work, routines, service.",
                      7: "Partnerships, marriage, relationships.", 8: "Transformation, shared resources, intimacy.",
                      9: "Higher learning, travel, philosophy.", 10: "Career, public image, reputation.",
                      11: "Friendships, networks, aspirations.", 12: "Spirituality, isolation, subconscious."}

zodiac_nature = {'Aries': 'Fiery, Cardinal, Positive', 'Taurus': 'Earthy, Fixed, Negative',
                 'Gemini': 'Airy, Mutable, Positive', 'Cancer': 'Watery, Cardinal, Negative',
                 'Leo': 'Fiery, Fixed, Positive', 'Virgo': 'Earthy, Mutable, Negative',
                 'Libra': 'Airy, Cardinal, Positive', 'Scorpio': 'Watery, Fixed, Negative',
                 'Sagittarius': 'Fiery, Mutable, Positive', 'Capricorn': 'Earthy, Cardinal, Negative',
                 'Aquarius': 'Airy, Fixed, Positive', 'Pisces': 'Watery, Mutable, Negative'}

opposite_signs = {'Aries': 'Libra', 'Taurus': 'Scorpio', 'Gemini': 'Sagittarius', 'Cancer': 'Capricorn',
                  'Leo': 'Aquarius', 'Virgo': 'Pisces', 'Libra': 'Aries', 'Scorpio': 'Taurus',
                  'Sagittarius': 'Gemini', 'Capricorn': 'Cancer', 'Aquarius': 'Leo', 'Pisces': 'Virgo'}

def get_aspected_houses(planet, house_num):
    aspects = []
    if planet in ['Su', 'Mo', 'Me', 'Ve']:
        aspects.append((house_num + 6 - 1) % 12 + 1)  # 7th house
    elif planet == 'Ma':
        aspects += [((house_num + 3 - 1) % 12) + 1,  # 4th
                    ((house_num + 6 - 1) % 12) + 1,  # 7th
                    ((house_num + 7 - 1) % 12) + 1]  # 8th
    elif planet == 'Ju':
        aspects += [((house_num + 4 - 1) % 12) + 1,  # 5th
                    ((house_num + 6 - 1) % 12) + 1,  # 7th
                    ((house_num + 8 - 1) % 12) + 1]  # 9th
    elif planet == 'Sa':
        aspects += [((house_num + 2 - 1) % 12) + 1,  # 3rd
                    ((house_num + 6 - 1) % 12) + 1,  # 7th
                    ((house_num + 9 - 1) % 12) + 1]  # 10th
    elif planet in ['Ra', 'Ke']:
        aspects += [((house_num + 4 - 1) % 12) + 1,  # 5th
                    ((house_num + 8 - 1) % 12) + 1]  # 9th
    return aspects

def get_aspect_type(planet, from_house, to_house):
    diff = (to_house - from_house) % 12
    if planet in ['Su', 'Mo', 'Me', 'Ve']:
        if diff == 6: return "7th"
    elif planet == 'Ma':
        if diff == 3: return "4th"
        if diff == 6: return "7th"
        if diff == 8: return "8th"
    elif planet == 'Ju':
        if diff == 4: return "5th"
        if diff == 6: return "7th"
        if diff == 8: return "9th"
    elif planet == 'Sa':
        if diff == 2: return "3rd"
        if diff == 6: return "7th"
        if diff == 9: return "10th"
    elif planet in ['Ra', 'Ke']:
        if diff == 4: return "5th"
        if diff == 8: return "9th"
    return ""

def offset_point(x0, y0, x1, y1, offset=0.3):
    # Move (x0, y0) towards (x1, y1) by 'offset' units, and (x1, y1) towards (x0, y0) by 'offset' units
    dx = x1 - x0
    dy = y1 - y0
    dist = math.hypot(dx, dy)
    if dist == 0:
        return x0, y0, x1, y1
    ox = dx / dist * offset
    oy = dy / dist * offset
    return x0 + ox, y0 + oy, x1 - ox, y1 - oy

def get_contrasting_color(color):
    # Returns a contrasting color for tooltip text
    if color in ['black', 'purple', 'brown', 'deepskyblue', 'blue', 'darkgreen']:
        return 'yellow'
    if color in ['white', 'gold', 'hotpink', 'orange', 'lightgreen', 'aqua', 'gray']:
        return 'black'
    return 'white'

# Map each planet to its house number
planet_house = {}
for name, deg in positions.items():
    # Find which house this degree falls into
    # Each house starts at house_signs[h], so find h where sign matches
    sign = zodiac_sign(deg)
    for h in range(1, 13):
        if house_signs[h] == sign:
            planet_house[name] = h
            break

# Define planet colors for labels and aspect lines
planet_colors = {
    'Su': 'gold',
    'Mo': 'white',
    'Ma': 'red',
    'Me': 'deepskyblue',
    'Ju': 'orange',
    'Ve': 'hotpink',
    'Sa': 'black',
    'Ra': 'purple',
    'Ke': 'gray',
    'Ur': 'lightgreen',
    'Ne': 'aqua',
    'Pl': 'brown'
}

# Define benefic/malefic nature for color coding (must be before aspect_rows)
planet_nature = {
    'Su': 'malefic',
    'Mo': 'benefic',  # You can make this dynamic for waxing/waning
    'Ma': 'malefic',
    'Me': 'benefic',  # Mercury is generally benefic unless with malefics
    'Ju': 'benefic',
    'Ve': 'benefic',
    'Sa': 'malefic',
    'Ra': 'malefic',
    'Ke': 'malefic'
}
aspect_colors = {
    'benefic': 'rgba(0,200,0,0.5)',   # Green
    'malefic': 'rgba(200,0,0,0.5)',   # Red
    'neutral': 'rgba(200,200,0,0.5)'  # Yellow (if you want to use)
}

# Build aspect_rows for the table (must be before combined_fig and aspect plotting)
aspect_rows = []
for planet, h in planet_house.items():
    aspected_houses = get_aspected_houses(planet, h)
    planet_label = {
        'Su': 'Sun', 'Mo': 'Moon', 'Ma': 'Mars', 'Me': 'Mercury', 'Ju': 'Jupiter',
        'Ve': 'Venus', 'Sa': 'Saturn', 'Ra': 'Rahu', 'Ke': 'Ketu'
    }.get(planet, planet)
    nature = planet_nature.get(planet, 'neutral')
    nature_label = 'Benefic' if nature == 'benefic' else ('Malefic' if nature == 'malefic' else 'Neutral')
    for ah in aspected_houses:
        aspect_type = get_aspect_type(planet, h, ah)
        aspect_rows.append([
            planet_label,
            f"{h} ({house_signs[h]})",
            f"{ah} ({house_signs[ah]})",
            aspect_type + " aspect",
            nature_label
        ])

# Create a single subplot for the kundli chart (no table)
combined_fig = make_subplots(
    rows=1, cols=1,
    specs=[[{"type": "xy"}]]
)

# Add kundli plot traces to row 1
for trace in fig.data:
    combined_fig.add_trace(trace, row=1, col=1)
for shape in getattr(fig.layout, "shapes", []):
    combined_fig.add_shape(shape, row=1, col=1)

# Add house and planet text labels to the kundli plot in combined_fig
for h in range(1, 13):
    sign = house_signs[h]
    x, y = coords[h]
    planets_in_sign = sign_planets[sign]
    # Color each planet label in its own color using HTML <span>
    display_planets = []
    for p in planets_in_sign:
        p_short = p.split()[0]
        color = planet_colors.get(p_short, 'white')
        display_planets.append(f'<span style="color:{color}">{p}</span>')
    display_text = f"{sign}<br>" + "<br>".join(display_planets) if display_planets else f"{sign}"
    nature = zodiac_nature[sign]
    natural_sign = signs[(h-1)%12]
    color = 'white'
    if sign == natural_sign:
        color = 'limegreen'
    elif sign == opposite_signs[natural_sign]:
        color = 'red'
    hovertext = f"<b>{h}th House</b><br>{house_descriptions[h]}<br><b>Sign:</b> {sign}<br><b>Nature:</b> {nature}<br><b>Planets:</b><br>{'<br>'.join(planets_in_sign) if planets_in_sign else 'None'}"
    combined_fig.add_trace(go.Scatter(
        x=[x], y=[y], mode='text', text=[display_text], textposition="middle center",
        hovertext=hovertext, hoverinfo="text",
        textfont=dict(color=color, size=12),
        texttemplate="%{text}",
        textfont_family="monospace"
    ), row=1, col=1)

# Calculate unique positions for each planet in each house
planet_positions = {}
offset_radius = 0.25  # how far from the house center to place the planet

for name, deg in positions.items():
    sign = zodiac_sign(deg)
    deg_in_sign = deg % 30
    for h in range(1, 13):
        if house_signs[h] == sign:
            angle = np.pi/2 - (deg_in_sign / 30) * 2 * np.pi  # 0° at top, clockwise
            cx, cy = coords[h]
            radius = 0.35  # slightly larger for visual separation
            px = cx + radius * np.cos(angle)
            py = cy + radius * np.sin(angle)
            planet_positions[(name, h)] = (px, py)
            break

# Draw aspect lines as Scatter traces with hover tooltips and planet color coding
for planet, h in planet_house.items():
    aspected_houses = get_aspected_houses(planet, h)
    planet_label = {
        'Su': 'Sun', 'Mo': 'Moon', 'Ma': 'Mars', 'Me': 'Mercury', 'Ju': 'Jupiter',
        'Ve': 'Venus', 'Sa': 'Saturn', 'Ra': 'Rahu', 'Ke': 'Ketu'
    }.get(planet, planet)
    color = planet_colors.get(planet, 'white')
    nature = planet_nature.get(planet, 'neutral')
    nature_label = 'Benefic' if nature == 'benefic' else ('Malefic' if nature == 'malefic' else 'Neutral')
    for ah in aspected_houses:
        aspect_type = get_aspect_type(planet, h, ah)
        # Use the planet's unique position as the start point
        x0, y0 = planet_positions.get((planet, h), coords[h])
        x1, y1 = coords[ah]
        # Offset the line endpoints to avoid overlap with house/planet tooltips
        x0o, y0o, x1m, y1m = offset_point(x0, y0, x1, y1, offset=0.45)  # marker further out
        tooltip_color = get_contrasting_color(color)
        aspect_text = (
            f"<b><span style='color:{tooltip_color}'>{planet_label}</span></b><br>"
            f"({h}th, {house_signs[h]})<br>"
            f"aspects <b>{ah}th</b> ({house_signs[ah]})<br>"
            f"<b>Aspect:</b> {aspect_type} <br>"
            f"<b>Nature:</b> {nature_label}"
        )
        combined_fig.add_trace(go.Scatter(
            x=[x0o, x1m], y=[y0o, y1m],
            mode="lines",
            line=dict(color=color, width=2, dash="dot"),
            hoverinfo="text",
            hovertext=aspect_text,
            showlegend=False,
            opacity=0.7
        ), row=1, col=1)
        combined_fig.add_trace(go.Scatter(
            x=[x1m], y=[y1m],
            mode="markers",
            marker=dict(symbol="triangle-up", color=color, size=10, opacity=0.8, line=dict(width=1, color='white')),
            hoverinfo="skip",
            showlegend=False
        ), row=1, col=1)

arc_radius = 0.35
arc_points = 60  # smoothness

for h in range(1, 13):
    cx, cy = coords[h]
    # Arc from 0° (top) to 360° (full circle)
    arc_angles = np.linspace(np.pi/2, np.pi/2 - 2*np.pi, arc_points)
    arc_x = cx + arc_radius * np.cos(arc_angles)
    arc_y = cy + arc_radius * np.sin(arc_angles)
    combined_fig.add_trace(go.Scatter(
        x=arc_x, y=arc_y,
        mode='lines',
        line=dict(color='white', width=1, dash='dot'),
        opacity=0.2,
        hoverinfo='skip',
        showlegend=False
    ), row=1, col=1)

combined_fig.update_layout(
    height=900,
    plot_bgcolor='#444', paper_bgcolor='#444', showlegend=False,
    xaxis=dict(visible=False, range=[-1, 11]), yaxis=dict(visible=False, range=[-1, 11]),
    title=f"Kundli (Asc: {asc_sign}), Date: {birth_date}, Time: {birth_time}",
    title_font_color='white', margin=dict(l=0, r=0, t=40, b=0)
)

combined_fig.show()
