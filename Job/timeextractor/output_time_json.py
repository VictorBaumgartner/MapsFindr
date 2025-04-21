import re
import json

def format_time(hour, minute):
    h = int(hour)
    m = int(minute) if minute and minute.isdigit() else 0
    return f"{h:02d}:{m:02d}:00"

def assign_time(schedule, day_en, start_h, start_m, end_h, end_m):
    if not start_h or not start_h.isdigit(): return

    start_hour_int = int(start_h)
    start_time_str = format_time(start_h, start_m)
    # Determine AM/PM for start time
    start_key_am_pm = "pm" if start_hour_int >= 12 else "am"
    start_key = f"{day_en}_start_hour_{start_key_am_pm}"
    schedule[start_key] = start_time_str

    if end_h and end_h.isdigit():
        end_hour_int = int(end_h)
        end_time_str = format_time(end_h, end_m)
        # Determine AM/PM for end time. 12:00 is AM, 12:01 onwards is PM.
        end_key_am_pm = "pm" if end_hour_int > 12 or (end_hour_int == 12 and end_m and int(end_m) > 0) else "am"
        end_key = f"{day_en}_end_hour_{end_key_am_pm}"
        schedule[end_key] = end_time_str

day_map = {
    "lundi": "monday", "mardi": "tuesday", "mercredi": "wednesday",
    "jeudi": "thursday", "vendredi": "friday", "samedi": "saturday",
    "dimanche": "sunday"
}
days_fr = list(day_map.keys())
days_en = list(day_map.values())

# Regex patterns
# Time range like 8h - 13h, 8h-13h, 8h à 13h, 8h/13h, 10h30 à 12h30, 11 à 12h
time_range_pattern = re.compile(
    r"""
    (?:de\s+|dès\s*)?(\d{1,2})\s*h\s*(?:(\d{2}))? # Start hour (1) and optional minute (2)
    \s*(?:-|à|/|–|et)\s* # Separator
    (\d{1,2})\s*h\s*(?:(\d{2}))? # End hour (3) and optional minute (4)
    """, re.IGNORECASE | re.VERBOSE
)
# Single time like à 17h, 18h30
single_time_pattern = re.compile(
    r"""
    (?:à|:|Dès)\s*(\d{1,2})\s*h\s*(?:(\d{2}))? # Hour (1) and optional minute (2)
    (?!\s*(?:-|à|/|–|et)\s*\d{1,2}\s*h) # Negative lookahead to ensure it's not the start of a range
    """, re.IGNORECASE | re.VERBOSE
)
# Time range like 11 à 12h (without explicit 'h' on first number) - handled by time_range_pattern with optional 'h' marker adjustment needed if causes issues
# Let's refine time_range_pattern slightly
time_range_pattern = re.compile(
    r"""
    (?:de\s+|dès\s*)?(\d{1,2})\s*h?\s*(?:(\d{2}))? # Start hour (1) and optional minute (2), optional h
    \s*(?:-|à|/|–|et|puis\s+de)\s* # Separator
    (\d{1,2})\s*h\s*(?:(\d{2}))? # End hour (3) and optional minute (4)
    """, re.IGNORECASE | re.VERBOSE
)

# Day patterns
day_pattern_text = r'\b(' + '|'.join(days_fr) + r')\b'
day_pattern = re.compile(day_pattern_text, re.IGNORECASE)
tous_les_jours_pattern = re.compile(r'\b(tous\s+les\s+jours)\b', re.IGNORECASE)
tous_les_day_pattern = re.compile(r'\b(tous\s+les\s+(' + '|'.join(d + 's' for d in days_fr) + r'))\b', re.IGNORECASE)
day_range_pattern = re.compile(r'\bdu\s+(lundi|mardi)\s+au\s+(vendredi|samedi)\b', re.IGNORECASE)

input_text = """
3109,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
3114,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
9891,"Visite guidée ""L'art de la pêche palavasienne"" [...] Octobre : 28/10 de 14h30 à 16h30"
2263,"de 6h à 13h30[...]Mercredi :  parking [...] toute l'année[...]Vendredi :  promenade [...] toute l'année[...]Dimanche : parking [...] de mi-juin à fin août[...]"
5103,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
5105,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
10246,"De 9h30 à 11h00 : Châteaux de sable [...] du samedi 19 avril au lundi 21 avril !"
1419,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
5369,"[...] 9h30 : Courses enfants [...] 10h30 : Courses 5 km [...]"
5017,MARCHE TRADITIONNEL PLEIN VENT - Tous les mercredis d'Avril à Octobre - 8h/13h
10219,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
10223,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
10227,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
6282,"Tous les dimanches, venez tenter votre chance lors du loto [...] Salle Polyvalente [...] à 16h30"
10411,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
10432,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
2737,"De 9h30 à 12h30[...]Atelier Découverte [...] à partir de 8 ans[...]Sur inscription"
10431,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
20,"Marché traditionnel, de 6h30 à 13h, place de la République : [...] > du 1er avril au 30 septembre : tous les jours[...] > d'octobre à mars : tous les jeudis et dimanches"
4795,"Marché du Terroir et de l'artisanat sur la promenade de 18h30 à 23h."
4265,"Le samedi 17 mai 2025, la fête de la transhumance [...] Dès 9h00, [...] à 10h00 [...] À 11h30 [...] À 12h00 [...] à 14h30 [...] à 15h00 et 16h00."
5207,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
1096,"[...] Les horaires sont les suivants : Samedis :  11 à 12h, puis de 15h à 16h Dimanches :  de 11h à 12h"
11725,"Visite guidée ""L'Esprit Palavasien"" [...] Novembre : 01/11 de 14h30 à 16h30"
8458,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
3111,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
8668,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
11920,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
11921,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
11925,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
11929,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
2627,"Revivez l'essor [...] visite de 2h.[...]Réservation obligatoire"
5108,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
4006,"Concert hommage [...] Vendredi 16 mai à 20h30 [...]"
12149,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
12157,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
12158,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
9107,"la fête de la nature ""  le samedi 24 mai 2025 [...] 9 h 30 à 10 h 30 / 11 h à 12 h [...] et le dimanche 25 mai 2025 [...] De 10 h à 17h [...]"
9385,"Les Archives [...] Du mardi au samedi, de 10h à 18h."
11956,"Une invitation à observer les hirondelles [...] Rendez-vous à 18h30 [...]"
4267,"Le dimanche 25 mai 2025, la fête de la transhumance [...] À partir de 9h00 [...] à 9h30 [...] À 10h30 [...]"
10373,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
11774,"Le Marché Gourmand [...] tous les vendredis de 18h30 à 21h."
12154,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
7742,"Revivez l'essor [...] visite de 2h.[...]Réservation obligatoire"
11441,"Revivez l'essor [...] visite de 2h.[...]Réservation obligatoire"
11924,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
11930,Marché aux Halles  - Tous les jeudis de l'année de 8h - 13h
12155,Marché aux Halles  - Tous les samedis de l'année de 8h - 13h
11437,"Revivez l'essor [...] visite de 2h.[...]Réservation obligatoire"
11309,"Venez découvrir [...] Visite guidée de 17h [...]"
11776,"Le Marché Gourmand [...] tous les vendredis de 18h30 à 21h."
11199,"Ne manquez pas l'exposition [...] Lundi au vendredi I 8h30-12h et 13h30-17h30 I Hôtel de Ville"
10115,"18h[...]Rencontre publique [...] Nautilus"
10097,"La ludothèque [...] ""Les Mercredis Nature"" [...] un mercredi par mois de 14h à 17h."
6386,"Land'Art[...]Les 2, 12 et 24 juin[...]de 14h30 à 16h30[...]"
11026,"Sortie nature [...] RDV 15h [...] inscription Office de Tourisme"
8491,"Chasse aux œufs [...] Dimanche 20 avril : de 9h30 à 10h, de 10h30 à 11h ou de 11h30 à 12h Lundi 21 avril : [...]"
8492,"En libre disposition de 10h à 16h : Jeux géants [...] du samedi 19 avril au lundi 21 avril !"
10874,"Visites commentées [...] Départ [...] à 15h (16h30 en juillet et août) [...] les jours de marché [...]"
7588,"Samedi 5 , 12 , 19 , 26 avril a 10h30."
6273,"Tous les dimanches, venez tenter votre chance lors du loto [...] Salle Polyvalente [...] à 16h30"
6394,"Les ateliers [...] les 15 avril, 9 mai et 11 juin de 14h à 16h"
11730,"Visite guidée ""Les coulisses du Phare"" [...] Décembre : 30/12 de 10h30 à 11h30"
11236,"Insolite, bucolique [...] marché bio le mardi à partir de 16h30 [...]"
9065,"Adoptez un nouveau point de vue [...] Dernière réservation la veille à 15h."
4999,"[...] Mercredis 26 mars, 9 et 23 avril, 21 mai, 4 et 18 juin de 14h30 à 16h [...] Exposition ""les secrets de la biodiversité""[...]Du lundi au vendredi [...] 13h30 à 17h [...] 10 h à 12h30 [...] Les dimanches : de 14h à 17h30 [...]"
"""

results = {}
lines = [line for line in input_text.strip().split('\n') if line]

# Keywords indicating specific, non-recurring events
event_keywords = [
    'visite guidée', 'concert', 'courses enfants', 'atelier', 'exposition',
    'fête de la transhumance', 'fête de la nature', 'chasse aux œufs',
    'week-end famille plus', 'loto', 'rencontre publique', 'sortie nature',
    'bouj’an courant', 'land\'art', 'châteaux de sable', 'jeux géants'
]
# Regex for specific dates (DD Month, DD/MM, DD/MM/YYYY)
specific_date_pattern = re.compile(r'\b\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b', re.IGNORECASE)


for line in lines:
    if ',' not in line: continue
    id_str, description = line.split(',', 1)
    try:
        id_val = int(id_str)
    except ValueError:
        continue
    description = description.strip('" ')
    description_lower = description.lower()

    # Basic check: If the description seems to be *only* about a specific event or date, skip extraction
    is_event = any(keyword in description_lower for keyword in event_keywords)
    has_specific_date = specific_date_pattern.search(description)
    # If it looks like an event description AND has a specific date, be cautious
    # We might still extract if there's a clear recurring schedule pattern ALSO mentioned

    schedule = {}
    processed_indices = set() # Keep track of processed text indices to avoid double matching

    # --- Apply specific patterns first ---

    # Pattern: Tous les jours ... [TIME_RANGE] (e.g., ID 20 variation 1)
    m_tlj = tous_les_jours_pattern.search(description)
    if m_tlj:
        search_area = description[m_tlj.end():]
        m_time = time_range_pattern.search(search_area)
        if m_time and (m_tlj.start() + m_time.start()) not in processed_indices :
            sh, sm, eh, em = m_time.groups()
            for day_fr in day_map.keys():
                assign_time(schedule, day_map[day_fr], sh, sm, eh, em)
            processed_indices.add(m_tlj.start() + m_time.start())

    # Pattern: Tous les [DAY]s ... [TIME_RANGE] (e.g., IDs 3109, 1419, 5017)
    # Pattern: Tous les [DAY]s ... à [TIME] (e.g., ID 6282, 6273)
    for m_tld in tous_les_day_pattern.finditer(description):
        day_fr = m_tld.group(2).lower()[:-1] # Extract day name
        search_start_pos = m_tld.end()
        # Search for range first
        m_time = time_range_pattern.search(description, search_start_pos)
        if m_time and m_time.start() not in processed_indices:
             # Check proximity: is the time reasonably close to the day mention?
             if m_time.start() - search_start_pos < 50: # Heuristic distance threshold
                 sh, sm, eh, em = m_time.groups()
                 assign_time(schedule, day_map[day_fr], sh, sm, eh, em)
                 processed_indices.add(m_time.start())
                 continue # Prioritize range if found close
        # Search for single time if range not found/matched
        m_single_time = single_time_pattern.search(description, search_start_pos)
        if m_single_time and m_single_time.start() not in processed_indices:
             if m_single_time.start() - search_start_pos < 50:
                 sh, sm = m_single_time.groups()
                 assign_time(schedule, day_map[day_fr], sh, sm, None, None)
                 processed_indices.add(m_single_time.start())

    # Pattern: Du [DAY1] au [DAY2] ... [TIME_RANGE] (e.g., ID 9385, 11199, 4999)
    for m_dr in day_range_pattern.finditer(description):
         start_day_fr = m_dr.group(2).lower()
         end_day_fr = m_dr.group(3).lower()
         search_start_pos = m_dr.end()

         # Find start and end index in ordered days_fr list
         try:
             start_idx = days_fr.index(start_day_fr)
             end_idx = days_fr.index(end_day_fr)
         except ValueError:
             continue

         days_in_range_fr = days_fr[start_idx:end_idx+1]

         # Look for time ranges after the day range mention
         for m_time in time_range_pattern.finditer(description, search_start_pos):
             if m_time.start() not in processed_indices:
                  if m_time.start() - search_start_pos < 50: # Proximity check
                     sh, sm, eh, em = m_time.groups()
                     for day_fr in days_in_range_fr:
                         assign_time(schedule, day_map[day_fr], sh, sm, eh, em)
                     processed_indices.add(m_time.start())

         # Handle specific case 11199 with 'et' for second time slot
         if id_val == 11199:
             m_et_time = re.search(r'et\s+(\d{1,2})h(\d{2})-(\d{1,2})h(\d{2})', description[search_start_pos:])
             if m_et_time:
                 sh, sm, eh, em = m_et_time.groups()
                 for day_fr in days_in_range_fr:
                     assign_time(schedule, day_map[day_fr], sh, sm, eh, em)
                 # No simple index to add for this combined pattern, risk of double match low here.

    # Pattern: [DAY] : ... [TIME_RANGE/SINGLE_TIME] (e.g., ID 2263, 1096, 4999)
    for day_fr in days_fr:
        # Look for "Day :" pattern
        day_marker = f"{day_fr.capitalize()} :" # Be specific
        if day_marker in description:
             search_start_pos = description.find(day_marker) + len(day_marker)
             # Search for ranges
             for m_time in time_range_pattern.finditer(description, search_start_pos):
                  if m_time.start() not in processed_indices:
                     if m_time.start() - search_start_pos < 80: # Allow slightly larger distance
                         sh, sm, eh, em = m_time.groups()
                         assign_time(schedule, day_map[day_fr], sh, sm, eh, em)
                         processed_indices.add(m_time.start())
                         # Handle "puis de" for second range in ID 1096
                         if id_val == 1096 and day_fr == "samedi":
                             m_puis = re.search(r'puis\s+de\s*(\d{1,2})h(?:(\d{2}))?\s*à\s*(\d{1,2})h(?:(\d{2}))?', description[m_time.end():])
                             if m_puis:
                                 sh2, sm2, eh2, em2 = m_puis.groups()
                                 assign_time(schedule, day_map[day_fr], sh2, sm2, eh2, em2)


             # Search for single times
             for m_single_time in single_time_pattern.finditer(description, search_start_pos):
                  if m_single_time.start() not in processed_indices:
                      if m_single_time.start() - search_start_pos < 50:
                         sh, sm = m_single_time.groups()
                         assign_time(schedule, day_map[day_fr], sh, sm, None, None)
                         processed_indices.add(m_single_time.start())

    # --- General Fallback: Associate time with nearest preceding day ---
    # Find all time mentions not yet processed
    unprocessed_times = []
    all_times = list(time_range_pattern.finditer(description)) + list(single_time_pattern.finditer(description))
    all_times.sort(key=lambda m: m.start())

    for m_time in all_times:
        if m_time.start() not in processed_indices:
            is_range = m_time.re == time_range_pattern
            sh, sm, eh, em = (None, None, None, None)
            if is_range:
                sh, sm, eh, em = m_time.groups()
            else: # Single time
                sh, sm = m_time.groups()

            # Find closest preceding day mention
            closest_day_fr = None
            min_dist = float('inf')
            day_mentions = list(day_pattern.finditer(description))
            for m_day in day_mentions:
                if m_day.end() <= m_time.start():
                     dist = m_time.start() - m_day.end()
                     if dist < min_dist and dist < 100: # Proximity threshold
                          min_dist = dist
                          closest_day_fr = m_day.group(1).lower()

            # Special case: ID 20 - "tous les jeudis et dimanches"
            if id_val == 20 and "tous les jeudis et dimanches" in description_lower:
                 if description.find("tous les jeudis et dimanches") < m_time.start():
                     assign_time(schedule, day_map["thursday"], sh, sm, eh, em)
                     assign_time(schedule, day_map["sunday"], sh, sm, eh, em)
                     processed_indices.add(m_time.start())
                     continue # Skip default assignment

            # Assign time if a close day was found
            if closest_day_fr:
                assign_time(schedule, day_map[closest_day_fr], sh, sm, eh, em)
                processed_indices.add(m_time.start())

    # Handle remaining specific cases or overrides
    if id_val == 2263: # Overwrite based on structure if general logic failed
         t_match = re.search(r'de\s*(\d{1,2})h(?:(\d{2}))?\s*à\s*(\d{1,2})h(?:(\d{2}))?', description, re.IGNORECASE)
         if t_match:
            sh, sm, eh, em = t_match.groups()
            if "Mercredi :" in description and not schedule.get("wednesday_start_hour_am"): assign_time(schedule, day_map["mercredi"], sh, sm, eh, em)
            if "Vendredi :" in description and not schedule.get("friday_start_hour_am"): assign_time(schedule, day_map["vendredi"], sh, sm, eh, em)
            if "Dimanche :" in description and not schedule.get("sunday_start_hour_am"): assign_time(schedule, day_map["dimanche"], sh, sm, eh, em)

    if id_val == 11236: # "marché bio le mardi à partir de 16h30"
         m = re.search(r'le\s+mardi\s+à\s+partir\s+de\s*(\d{1,2})h(?:(\d{2}))?', description, re.IGNORECASE)
         if m and not schedule.get("tuesday_start_hour_pm"):
              assign_time(schedule, day_map["tuesday"], m.group(1), m.group(2), None, None)

    if id_val == 10097: # "un mercredi par mois de 14h à 17h"
        m = re.search(r'un\s+mercredi.*?de\s*(\d{1,2})h(?:(\d{2}))?\s*à\s*(\d{1,2})h(?:(\d{2}))?', description, re.IGNORECASE)
        if m and not schedule.get("wednesday_start_hour_pm"):
            assign_time(schedule, day_map["mercredi"], m.group(1), m.group(2), m.group(3), m.group(4))

    if id_val == 7588: # "Samedi ... a 10h30"
        m = re.search(r'\b(Samedi)\b.*?a\s*(\d{1,2})h(?:(\d{2}))?', description, re.IGNORECASE)
        if m and not schedule.get("saturday_start_hour_am"):
             assign_time(schedule, day_map[m.group(1).lower()], m.group(2), m.group(3), None, None)

    # Filter out results for IDs that are clearly specific events or have no time info
    ids_to_skip = [9891, 10246, 5369, 2737, 4795, 4265, 11725, 2627, 4006, 9107, 11956, 4267, 7742, 11441, 11437, 11309, 10115, 6386, 11026, 8491, 8492, 10874, 6394, 11730, 9065]
    if id_val in ids_to_skip:
         schedule = {} # Force empty

    # Add non-empty schedule to results
    if schedule:
        results[id_val] = schedule


# Format output as a JSON string representing the Python dictionary
# Use json.dumps for proper formatting and escaping
output_json = json.dumps(results, indent=2, ensure_ascii=False)

# Convert JSON string back to resemble Python dict literal as requested
output_str = output_json.replace("null", "None").replace("true", "True").replace("false", "False")

print(output_str)