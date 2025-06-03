# tennis_booking.py

# --- IMPORTY ---
#  `TEMPLATE_PATH` aby dodać ścieżkę do szablonów
from bottle import Bottle, run, template, request, redirect, static_file, TEMPLATE_PATH
# sqlite3 do obsługi bazy danych SQLite.
import sqlite3
# datetime do pracy z datami i czasem.
import datetime
# os do operacji na systemie plików (np. sprawdzanie istnienia bazy danych).
import os
# hashlib do hashowania haseł.
import hashlib
# Beaker do obsługi sesji (pamiętania, kto jest zalogowany).
from beaker.middleware import SessionMiddleware

# --- KONFIGURACJA ŚCIEŻEK DO SZABLONÓW ---
# Dodajemy folder 'views' do ścieżek, w których Bottle będzie szukał szablonów.
# Domyślnie Bottle szuka w ./ i ./views/, ale jawne dodanie jest dobrą praktyką.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWS_PATH = os.path.join(BASE_DIR, 'views')
TEMPLATE_PATH.insert(0, VIEWS_PATH)


# --- KONFIGURACJA SESJI ---
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'session.data_dir': './session_data', 
    'session.auto': True
}

# --- KONFIGURACJA APLIKACJI BOTTLE ---
app = Bottle()

# --- NAZWA BAZY DANYCH ---
DB_NAME = 'tennis_courts.db'

# --- FUNKCJE DLA INICJALIZACJI BAZY DANYCH ---
def connect_db():
    """Nawiązuje połączenie z bazą danych SQLite."""
    return sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

def init_db():
    """Inicjalizuje bazę danych, tworząc tabele, jeśli nie istnieją."""
    db_exists = os.path.exists(DB_NAME)
    conn = connect_db()
    cursor = conn.cursor()
    if not db_exists:
        print("Tworzenie tabel w bazie danych...")
        # Tabela użytkowników
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        ''')
        # Tabela ośrodków
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                osm_embed_code TEXT,
		        slogan TEXT
            )
        ''')
        # tabela kortów
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                facility_id INTEGER NOT NULL,
                court_number INTEGER NOT NULL, --nr kortu w ośrodku
                court_type TEXT NOT NULL, -- 'ziemny', 'twardy_hala', 'trawa'
                FOREIGN KEY (facility_id) REFERENCES facilities(id)
            )
        ''')
        # tabela reguł cenowych
        #  # day_type: 'weekday', 'weekend'
        # start_hour_slot: godzina rozpoczęcia obowiązywania ceny (np. 7 dla 7:00)
        # end_hour_slot: godzina zakończenia obowiązywania ceny (np. 17 dla zakresu 7:00-16:59)
        # (czyli sloty od start_hour_slot do end_hour_slot-1) 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_rules(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                facility_id INTEGER NOT NULL,
                day_type TEXT NOT NULL,
                start_hour_slot INTEGER NOT NULL,
                end_hour_slot INTEGER NOT NULL,
                price_indoor REAL, -- cena dla kortów indoor (np. twardy_hala)
                price_outdoor REAL, -- cena dla kortów outdoor (ziemny, trawiasty)
                FOREIGN KEY (facility_id) REFERENCES facilities(id)
                )
        ''')

        # tabela rezerwacyj
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                court_id INTEGER NOT NULL,
                reservation_date DATE NOT NULL,
                start_hour INTEGER NOT NULL,
                price_paid REAL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (court_id) REFERENCES courts(id)
            )
        ''')

        # hasło admina
        admin_pass_hash = hash_password('admin123')
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           ('admin', admin_pass_hash, 'admin'))
            print("Dodano domyślnego admina: login 'admin', hasło 'admin123'")
        except sqlite3.IntegrityError:
            print("Admin już istnieje.")
            

# dodanie osrodkow
        facilities_data = [
            (1, "Park Skaryszewski", "Aleja Zieleniecka 2, Warszawa", 
             '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0487,52.2470,21.0527,52.2490&layer=mapnik&marker=52.2480,21.0507" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.2480&mlon=21.0507#map=17/52.2480/21.0507">Zobacz większą mapę</a></small>', 
             "Poczuj klasykę tenisa na naszych 6 kortach ziemnych w sercu zielonej Pragi!"),
            (2, "Korty Solec", "ul. Solec 25, Warszawa", 
             '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0370,52.2310,21.0410,52.2330&layer=mapnik&marker=52.2320,21.0390" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.2320&mlon=21.0390#map=17/52.2320/21.0390">Zobacz większą mapę</a></small>', 
             "Graj przez cały rok! Korty ziemne i twarde w hali czekają nad Wisłą."),
            (3, "Korty Paryska", "ul. Paryska 10, Warszawa", 
             '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0620,52.2410,21.0660,52.2430&layer=mapnik&marker=52.2420,21.0640" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.2420&mlon=21.0640#map=17/52.2420/21.0640">Zobacz większą mapę</a></small>', 
             "Doświadcz różnorodności! Korty ziemne i unikalny kort trawiasty na Saskiej Kępie."),
            # NOWE OŚRODKI z XLS
            (4, "Korty Praga", "ul. Kawęczyńska 4, 03-855 Warszawa", 
             '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0580%2C52.2570%2C21.0640%2C52.2600&layer=mapnik&marker=52.2585%2C21.0610" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.2585&mlon=21.0610#map=17/52.2585/21.0610">Zobacz większą mapę</a></small>', # ZASTĄP TO
             "Nowoczesne korty na Pradze - graj komfortowo i nowocześnie!"), 
            (5, "Centrum Warszawianka", "ul. Merliniego 2, 02-511 Warszawa", 
             '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0210%2C52.1930%2C21.0270%2C52.1960&layer=mapnik&marker=52.1945%2C21.0240" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.1945&mlon=21.0240#map=17/52.1945/21.0240">Zobacz większą mapę</a></small>',
             "Kompleks sportowy dla każdego - tenis na najwyższym poziomie!") 
        ]
        cursor.executemany("INSERT INTO facilities (id, name, address, osm_embed_code, slogan) VALUES (?, ?, ?, ?, ?)", facilities_data)

        
        # --- Dodanie danych kortów --- 
        courts_data = [
            (1, 1, 'ziemny'), (1, 2, 'ziemny'), (1, 3, 'ziemny'), (1, 4, 'ziemny'), (1, 5, 'ziemny'), (1, 6, 'ziemny'),
            (2, 1, 'ziemny'), (2, 2, 'ziemny'), (2, 3, 'ziemny'), (2, 4, 'ziemny'),
            (2, 5, 'twardy_hala'), (2, 6, 'twardy_hala'), (2, 7, 'twardy_hala'), (2, 8, 'twardy_hala'),
            (3, 1, 'ziemny'), (3, 2, 'ziemny'), (3, 3, 'ziemny'), (3, 4, 'trawa'),
            (4, 1, 'twardy_hala'), (4, 2, 'twardy_hala'), (4, 3, 'ziemny'), (4, 4, 'ziemny'),
            (5, 1, 'twardy_hala'), (5, 2, 'twardy_hala'), (5, 3, 'twardy_hala'), (5, 4, 'ziemny'), (5, 5, 'ziemny'), (5, 6, 'ziemny'),
        ]
        cursor.executemany("INSERT INTO courts (facility_id, court_number, court_type) VALUES (?, ?, ?)", courts_data)

# --- Dodanie reguł cenowych ---
        pricing_rules_data = [
            (4, 'weekday', 7, 17, 65.0, 55.0), (4, 'weekday', 17, 23, 95.0, 85.0), (4, 'weekend', 8, 22, 80.0, 70.0),
            (5, 'weekday', 7, 12, 80.0, 70.0), (5, 'weekday', 12, 15, 70.0, 60.0), (5, 'weekday', 15, 22, 100.0, 90.0),
            (5, 'weekday', 22, 24, 85.0, 75.0), (5, 'weekend', 7, 24, 90.0, 80.0),
            # Na przykład dla Parku Skaryszewskiego (id=1), zakładając stałą cenę (tylko outdoor):
            (1, 'weekday', 10, 22, None, 50.0), # Cena od 10:00 do 21:00 w tygodniu
            (1, 'weekend', 10, 22, None, 60.0), # Cena od 10:00 do 21:00 w weekendy
            # Podobnie dla Korty Solec (id=2) i Paryska (id=3)
            (2, 'weekday', 10, 22, 40.0, 50.0), # Cena od 10:00 do 21:00 w tygodniu
            (2, 'weekend', 10, 22, 50.0, 60.0), # Cena od 10:00 do 21:00 w weekendy
            (3, 'weekday', 10, 22, None, 50.0), # Cena od 10:00 do 21:00 w tygodniu
            (3, 'weekend', 10, 22, None, 60.0), # Cena od 10:00 do 21:00 w weekendy
        ]
        cursor.executemany("""
            INSERT INTO pricing_rules 
            (facility_id, day_type, start_hour_slot, end_hour_slot, price_indoor, price_outdoor) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, pricing_rules_data)

        conn.commit()
        print("Baza danych zainicjalizowana i wypełniona danymi.")
    else:
        print("Baza danych już istnieje.")
    conn.close()


# --- FUNKCJE POMOCNICZE DOTYCZĄCE UWIERZYTELNIANIA I SESJI ---
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha256(user_password.encode('utf-8')).hexdigest()

def get_current_user():
    session = request.environ.get('beaker.session')
    user_id = session.get('user_id')
    if not user_id:
        return None
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'id': user[0], 'username': user[1], 'role': user[2]}
    return None

def login_required(f):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/login')
        # Przekazujemy obiekt użytkownika do opakowanej funkcji, jeśli go potrzebuje
        # kwargs['user'] = user 
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/login')
        if user['role'] != 'admin':
            return template("<h3>Brak uprawnień. Ta sekcja jest tylko dla administratorów.</h3> <a href='/'>Powrót</a>")
        # kwargs['user'] = user
        return f(*args, **kwargs)
    return wrapper

# --- FUNKCJE POMOCNICZE DLA LOGIKI APLIKACJI ---
def get_facility_court_types_summary(facility_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT court_type, COUNT(*) as count
        FROM courts
        WHERE facility_id = ?
        GROUP BY court_type
    """, (facility_id,))
    types = cursor.fetchall()
    conn.close()
    if not types:
        return "Brak informacji o kortach"
    type_names_map = {
        'ziemny': 'korty ziemne',
        'twardy_hala': 'nawierzchnia twarda (hala)',
        'trawa': 'korty na trawie'
    }
    summary_parts = []
    for court_type, count in types:
        friendly_name = type_names_map.get(court_type, court_type)
        summary_parts.append(f"{count}x {friendly_name}")
    return ", ".join(summary_parts)


def is_weekend(date_obj):
    """Sprawdza, czy dana data to weekend (sobota lub niedziela)."""
    # weekday() zwraca 0 dla poniedziałku, 5 dla soboty, 6 dla niedzieli
    return date_obj.weekday() >= 5

def get_price_for_slot(db_cursor, court_id, reservation_date_obj, start_hour):
    """
    Pobiera cenę dla danego kortu, daty i godziny.
    Zwraca cenę (float) lub None, jeśli nie znaleziono reguły.
    """
    # Pobierz facility_id i court_type dla danego court_id
    db_cursor.execute("SELECT facility_id, court_type FROM courts WHERE id = ?", (court_id,))
    court_details = db_cursor.fetchone()
    if not court_details:
        return None
    facility_id, court_type = court_details

    day_type_str = 'weekend' if is_weekend(reservation_date_obj) else 'weekday'
    
    # Sprawdź, czy kort jest indoor czy outdoor
    is_court_indoor = (court_type == 'twardy_hala')

    # Znajdź pasującą regułę cenową
    db_cursor.execute("""
        SELECT price_indoor, price_outdoor 
        FROM pricing_rules
        WHERE facility_id = ? 
          AND day_type = ?
          AND start_hour_slot <= ? 
          AND end_hour_slot > ? 
    """, (facility_id, day_type_str, start_hour, start_hour)) # start_hour musi być w przedziale [start_slot, end_slot-1]
    
    price_rule = db_cursor.fetchone()
    
    if price_rule:
        price_indoor, price_outdoor = price_rule
        return price_indoor if is_court_indoor else price_outdoor
    
    return None # Brak pasującej reguły cenowej

# --- PLIKI STATYCZNE (CSS, JS, OBRAZKI) ---
@app.route('/static/<filename:path>')
def send_static(filename):
    # Definiujemy ścieżkę do folderu static względem bieżącego pliku
    static_root = os.path.join(BASE_DIR, 'static')
    return static_file(filename, root=static_root)


# --- GŁÓWNE TRASY APLIKACJI (WIDOKI) ---

# Strona główna
@app.route('/')
def index():
    user = get_current_user() # Potrzebne do base_layout.tpl poprzez template()
    stock_photo_url = "/static/img/moje_zdjecie.jpg" 
    
    # Zamiast definiowania szablonu, używamy nazwy pliku
    return template('index_template', user=user, stock_photo_url=stock_photo_url, message=None)

# Rejestracja
@app.route('/register', method=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        password_confirm = request.forms.get('password_confirm')

        if not username or not password or not password_confirm:
            return template('register_template', error="Wszystkie pola są wymagane.")
        if password != password_confirm:
            return template('register_template', error="Hasła nie są zgodne.")
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return template('register_template', error="Nazwa użytkownika jest już zajęta.")

        hashed_pass = hash_password(password)
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'user')",
                           (username, hashed_pass))
            conn.commit()
        except sqlite3.Error as e:
            conn.close()
            return template('register_template', error=f"Błąd bazy danych: {e}")
        
        # Automatyczne logowanie po rejestracji
        cursor.execute("SELECT id, role FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            session = request.environ.get('beaker.session')
            session['user_id'] = user_data[0]
            session['user_role'] = user_data[1] 
            session.save()
            return redirect('/')
        else: 
            return redirect('/login')
    return template('register_template', error=None)

# Logowanie
@app.route('/login', method=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash, role FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data and check_password(user_data[1], password):
            session = request.environ.get('beaker.session')
            session['user_id'] = user_data[0]
            session['user_role'] = user_data[2] 
            session.save() 
            if user_data[2] == 'admin':
                return redirect('/admin')
            return redirect('/')
        else:
            return template('login_template', error="Nieprawidłowa nazwa użytkownika lub hasło.")
    return template('login_template', error=None)

# Wylogowanie
@app.route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session.delete() # Prostszy sposób na usunięcie całej sesji
    # if 'user_id' in session:
    #     del session['user_id']
    # if 'user_role' in session:
    #     del session['user_role']
    # session.save() 
    return redirect('/')


# -- ZASADY REJESTROWANIA NA KORTY
@app.route('/booking-rules')
def booking_rules_page():
    user = get_current_user()
    return template(
	'booking_rules_template', user=user
    )

@app.route('/our-centers')
def our_centers_page():
    user = get_current_user()
    
    conn = None
    centers_data_for_template = []

    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, address, osm_embed_code, slogan FROM facilities ORDER BY name")
        facilities_from_db = cursor.fetchall()

        for facility_row in facilities_from_db:
            facility_id, name, address, osm_embed_code, slogan_from_db = facility_row
            
            court_summary = get_facility_court_types_summary(facility_id)
            
            photo_file_name = f'facility_{facility_id}.jpg'
            photo_url = f"/static/img/{photo_file_name}"
            
            # photo_path = os.path.join(BASE_DIR, 'static', 'img', photo_file_name)
            # if not os.path.exists(photo_path):
            #     photo_url = "/static/img/placeholder_facility.jpg"

            centers_data_for_template.append({
                'id': facility_id,
                'name': name,
                'address': address,
                'slogan': slogan_from_db if slogan_from_db else "Zapraszamy na nasze korty!",
                'court_summary': court_summary,
                'photo_url': photo_url,
                'details_url': f"/facility/{facility_id}"
            })
            
    except sqlite3.Error as e:
        print(f"Błąd bazy danych przy pobieraniu ośrodków dla karuzeli: {e}")
    finally:
        if conn:
            conn.close()
            
    return template('our_centers_template', user=user, centers=centers_data_for_template)



# --- TRASY DLA ZALOGOWANEGO UŻYTKOWNIKA ---

@app.route('/facilities')
@login_required
def list_facilities():
    user = get_current_user() 
    filter_court_type = request.query.get('court_type')
    conn = connect_db()
    cursor = conn.cursor()

    query = "SELECT id, name, address, osm_embed_code, slogan FROM facilities"
    params = []

    if filter_court_type:
        query = """
            SELECT DISTINCT f.id, f.name, f.address, f.osm_embed_code, f.slogan
            FROM facilities f
            JOIN courts c ON f.id = c.facility_id
            WHERE c.court_type = ?
        """
        params.append(filter_court_type)

    cursor.execute(query, params)
    facilities_raw = cursor.fetchall()
    conn.close()

    facilities = []
    for facility_raw in facilities_raw: 
        facility_id, name, address, osm_code, slogan_text = facility_raw
        court_types_summary = get_facility_court_types_summary(facility_id)
        facility_photo_url = f"/static/img/facility_{facility_id}.jpg" # Załóżmy, że masz zdjęcia facility_1.jpg, facility_2.jpg itd.
        # Jeśli zdjęcie nie istnieje, można użyć placeholdera
        # Sprawdź czy plik istnieje:
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # if not os.path.exists(os.path.join(current_dir, 'static', 'img', f'facility_{facility_id}.jpg')):
        #     facility_photo_url = f"https://via.placeholder.com/300x150.png?text=Zdjęcie+{name.replace(' ', '+')}"

        facilities.append({
            'id': facility_id,
            'name': name,
            'address': address,
            'court_types_summary': court_types_summary,
            'photo_url': facility_photo_url,
            'osm_embed_code': osm_code,
            'slogan': slogan_text
        })
    available_court_types = ['ziemny', 'twardy_hala', 'trawa']
    return template('facilities_list_template', user=user, facilities=facilities, 
                    available_court_types=available_court_types, selected_filter=filter_court_type)

@app.route('/facility/<facility_id:int>')
@login_required
def facility_courts(facility_id):
    user = get_current_user()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM facilities WHERE id = ?", (facility_id,))
    facility_data = cursor.fetchone()
    if not facility_data:
        conn.close() # Zamknij połączenie przed zwróceniem błędu
        return "Ośrodek nie znaleziony."
    facility_name = facility_data[0]
    cursor.execute("SELECT id, court_number, court_type FROM courts WHERE facility_id = ? ORDER BY court_number", (facility_id,))
    courts_raw = cursor.fetchall()
    conn.close()
    type_names_map = {
        'ziemny': 'Kort ziemny',
        'twardy_hala': 'Kort z nawierzchnią twardą (hala)',
        'trawa': 'Kort na trawie'
    }
    courts = []
    for court_id, court_num, court_type in courts_raw:
        courts.append({
            'id': court_id,
            'name': f"{type_names_map.get(court_type, court_type)} nr {court_num}",
            'court_type': court_type
        })
    return template('facility_courts_template', user=user, facility_id=facility_id, facility_name=facility_name, courts=courts)



# OBLICZANIE CENY
# tennis_booking.py
# ...

@app.route('/court/<court_id:int>/book', method=['GET', 'POST'])
@login_required
def book_court(court_id):
    user = get_current_user()
    conn = connect_db()
    cursor = conn.cursor()

    # ... (pobieranie court_info, selected_date_obj, available_hours, booked_hours, slot_prices - bez zmian) ...
    cursor.execute("""
        SELECT c.id, c.court_number, c.court_type, c.facility_id, f.name as facility_name
        FROM courts c JOIN facilities f ON c.facility_id = f.id WHERE c.id = ?
    """, (court_id,))
    court_data = cursor.fetchone()

    if not court_data:
        conn.close()
        return "Kort nie znaleziony."
    court_info = {
        'id': court_data[0], 'number': court_data[1], 'type': court_data[2], 
        'facility_id': court_data[3], 'facility_name': court_data[4]
    }
    type_names_map_single = {
        'ziemny': 'Kort ziemny', 'twardy_hala': 'Kort z nawierzchnią twardą (hala)', 'trawa': 'Kort na trawie'
    }
    court_info['full_name'] = f"{type_names_map_single.get(court_info['type'], court_info['type'])} nr {court_info['number']} w {court_info['facility_name']}"

    selected_date_str = request.query.get('date', datetime.date.today().isoformat())
    try:
        selected_date_obj = datetime.date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date_obj = datetime.date.today()

    available_hours_range = list(range(10, 21)) # Zmieniono nazwę dla jasności
    
    cursor.execute("SELECT start_hour FROM reservations WHERE court_id = ? AND reservation_date = ?", 
                   (court_id, selected_date_obj))
    booked_hours_tuples_on_this_court = cursor.fetchall()
    booked_hours_on_this_court = {bh[0] for bh in booked_hours_tuples_on_this_court}

    slot_prices = {}
    for hour in available_hours_range:
        if hour not in booked_hours_on_this_court:
            price = get_price_for_slot(cursor, court_id, selected_date_obj, hour)
            slot_prices[hour] = f"{price:.2f} zł" if price is not None else "N/A"
        else:
            slot_prices[hour] = "Zajęty"
    # Koniec pobierania danych dla GET, ale połączenie zostaje otwarte


    if request.method == 'POST':
        newly_selected_slots_str = request.forms.getall('time_slots') # Zmieniono nazwę
        
        error_page_data = { # Słownik danych do przekazania w razie błędu
            'user': user, 'court_info': court_info, 
            'available_hours': available_hours_range, 'booked_hours': booked_hours_on_this_court, 
            'slot_prices': slot_prices, 'selected_date': selected_date_obj.isoformat(), 'datetime': datetime
        }

        if not newly_selected_slots_str:
            conn.close()
            return template('book_court_template', **error_page_data, error="Musisz wybrać przynajmniej jedną godzinę.")

        newly_selected_slots = sorted([int(s) for s in newly_selected_slots_str])

        # --- NOWA, ULEPSZONA WALIDACJA ---
        # 1. Pobierz istniejące rezerwacje użytkownika dla tego ośrodka i dnia (na dowolnym korcie w tym ośrodku)
        cursor.execute("""
            SELECT r.start_hour 
            FROM reservations r
            JOIN courts c ON r.court_id = c.id
            WHERE r.user_id = ? AND c.facility_id = ? AND r.reservation_date = ?
        """, (user['id'], court_info['facility_id'], selected_date_obj))
        
        user_existing_slots_in_facility_today = {row[0] for row in cursor.fetchall()}

        # 2. Połącz istniejące sloty z nowo wybranymi (unikalne, posortowane)
        #    Uwaga: nowo wybrane sloty nie mogą być wśród user_existing_slots_in_facility_today,
        #    chyba że rezerwujemy ten sam kort, a inna rezerwacja tego użytkownika jest na innym korcie.
        #    Na razie uprościmy: wszystkie rezerwacje użytkownika w ośrodku tego dnia tworzą jeden blok.
        
        all_user_slots_for_day_in_facility = sorted(list(user_existing_slots_in_facility_today.union(set(newly_selected_slots))))
        
        # 3. Sprawdź, czy łączna liczba godzin nie przekracza 3
        if len(all_user_slots_for_day_in_facility) > 3:
            conn.close()
            # Komunikat o błędzie powinien być bardziej precyzyjny
            existing_count = len(user_existing_slots_in_facility_today)
            error_msg = (f"Możesz zarezerwować maksymalnie 3 godziny dziennie w tym ośrodku. "
                         f"Masz już zarezerwowane {existing_count}h. "
                         f"Próbujesz dodać {len(newly_selected_slots)}h, co przekroczy limit.")
            return template('book_court_template', **error_page_data, error=error_msg)

        # 4. Sprawdź, czy wszystkie sloty (stare + nowe) tworzą ciągły blok
        if all_user_slots_for_day_in_facility: # Tylko jeśli są jakiekolwiek sloty
            for i in range(len(all_user_slots_for_day_in_facility) - 1):
                if all_user_slots_for_day_in_facility[i+1] - all_user_slots_for_day_in_facility[i] != 1:
                    conn.close()
                    # Komunikat o błędzie musi być jasny
                    error_msg = ("Twoje rezerwacje (włącznie z nowo wybranymi) muszą tworzyć ciągły blok godzin. "
                                 "Np. jeśli masz 12:00, możesz dobrać 11:00 lub 13:00. "
                                 f"Twoje planowane godziny to: {', '.join(map(lambda x: f'{x}:00', all_user_slots_for_day_in_facility))}")
                    return template('book_court_template', **error_page_data, error=error_msg)
        
        # --- KONIEC NOWEJ WALIDACJI ---
        
        # Pozostała część walidacji i logiki (ceny, zajętość konkretnego kortu)
        total_price = 0
        reservation_details_for_db = []

        for slot_hour in newly_selected_slots: # Iterujemy tylko po NOWYCH slotach do zarezerwowania
            # Sprawdzenie, czy NOWY slot nie jest już zajęty NA TYM KONKRETNYM KORCIE przez KOGOKOLWIEK
            # (booked_hours_on_this_court zawiera już te informacje)
            if slot_hour in booked_hours_on_this_court: # Ta walidacja jest już częściowo pokryta przez UI (disabled checkbox)
                                                       # ale warto ją tu zostawić jako zabezpieczenie serwerowe
                conn.close()
                return template('book_court_template', **error_page_data, 
                                error=f"Godzina {slot_hour}:00 na tym korcie została właśnie zajęta przez innego użytkownika. Odśwież stronę.")

            price_for_this_slot = get_price_for_slot(cursor, court_id, selected_date_obj, slot_hour)
            if price_for_this_slot is None:
                conn.close()
                return template('book_court_template', **error_page_data, 
                                error=f"Brak ceny dla godziny {slot_hour}:00. Skontaktuj się z administratorem.")
            total_price += price_for_this_slot
            reservation_details_for_db.append((user['id'], court_id, selected_date_obj, slot_hour, price_for_this_slot))
        
        # Jeśli doszliśmy tutaj, wszystkie walidacje przeszły pomyślnie
        try:
            for detail in reservation_details_for_db:
                cursor.execute("""
                    INSERT INTO reservations (user_id, court_id, reservation_date, start_hour, price_paid)
                    VALUES (?, ?, ?, ?, ?)
                """, detail)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return template('book_court_template', **error_page_data, error=f"Błąd bazy danych podczas rezerwacji: {e}")
            
        conn.close()
        return redirect(f'/my_reservations?success=true&total_price={total_price:.2f}')

    # Widok GET
    conn.close() 
    return template('book_court_template', 
                    user=user, court_info=court_info, 
                    available_hours=available_hours_range, 
                    booked_hours=booked_hours_on_this_court, 
                    slot_prices=slot_prices,
                    selected_date=selected_date_obj.isoformat(), error=None,
                    datetime=datetime)


# WYŚWIETLANIE REZERWACJI KIENTA
# tennis_booking.py

@app.route('/my_reservations')
@login_required
def my_reservations():
    user = get_current_user()
    success_message_text = request.query.get('success')
    total_price_from_redirect = request.query.get('total_price') # Pobierz cenę z redirect po nowej rezerwacji

    filter_date_str = request.query.get('filter_date')
    filter_facility_id_str = request.query.get('filter_facility')

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM facilities ORDER BY name") # Dla filtrów
    available_facilities_raw = cursor.fetchall()
    available_facilities = [(f_id, f_name) for f_id, f_name in available_facilities_raw]

    # Zapytanie SQL pobiera r.price_paid
    sql_query = """
        SELECT r.id, r.reservation_date, r.start_hour, r.price_paid, -- << TUTAJ POBIERAMY CENĘ
               c.court_number, c.court_type, f.name as facility_name, f.id as facility_id
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        JOIN facilities f ON c.facility_id = f.id
        WHERE r.user_id = ?
    """
    params = [user['id']]

    if filter_date_str:
        try:
            filter_date = datetime.date.fromisoformat(filter_date_str)
            sql_query += " AND r.reservation_date = ?"
            params.append(filter_date)
        except ValueError:
            filter_date_str = None
    if filter_facility_id_str and filter_facility_id_str.isdigit():
        filter_facility_id = int(filter_facility_id_str)
        sql_query += " AND f.id = ?"
        params.append(filter_facility_id)
    else:
        filter_facility_id_str = None
    sql_query += " ORDER BY r.reservation_date DESC, r.start_hour DESC"


    cursor.execute(sql_query, params)
    reservations_raw = cursor.fetchall()
    conn.close() 

    type_names_map = {
        'ziemny': 'Kort ziemny', 'twardy_hala': 'Kort z naw. twardą (hala)', 'trawa': 'Kort na trawie'
    }
    today = datetime.date.today()
    reservations = []
    for res_id, res_date_obj, start_hour, price_paid_val, court_num, court_type, facility_name, _facility_id in reservations_raw:
        can_cancel = res_date_obj >= today
        reservations.append({
            'id': res_id,
            'date_str': res_date_obj.strftime('%Y-%m-%d'),
            'time_str': f"{start_hour:02d}:00 - {start_hour+1:02d}:00",
            'court_info': f"{type_names_map.get(court_type, court_type)} nr {court_num}",
            'facility_name': facility_name,
            'price_paid': price_paid_val,
            'can_cancel': can_cancel
        })
    
    message_display = "Rezerwacja zakończona pomyślnie!" if success_message_text else None
    total_price_msg_display = total_price_from_redirect # Komunikat o cenie ostatniej rezerwacji

    current_filters = {
        'date': filter_date_str,
        'facility': filter_facility_id_str 
    }

    return template('my_reservations_template', 
                    user=user, 
                    reservations=reservations, 
                    message=message_display,
                    total_price_msg=total_price_msg_display, # Przekazanie informacji o cenie z redirectu
                    available_facilities=available_facilities,
                    current_filters=current_filters)

# USUWANIE REZERWACYJ
@app.route('/reservations/cancel/<reservation_id:int>', method='POST')
@login_required
def cancel_reservation(reservation_id):
    user = get_current_user()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, reservation_date FROM reservations WHERE id = ?", (reservation_id,))
    reservation_data = cursor.fetchone()
    if not reservation_data:
        conn.close()
        return "Rezerwacja nie znaleziona."
    res_user_id, res_date_obj = reservation_data
    if res_user_id != user['id']:
        conn.close()
        return "Nie masz uprawnień do anulowania tej rezerwacji."
    today = datetime.date.today()
    if res_date_obj < today:
        conn.close()
        return "Nie można anulować przeszłych rezerwacji."
    try:
        cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Błąd przy anulowaniu rezerwacji {reservation_id}: {e}")
    finally:
        conn.close()
    return redirect('/my_reservations')


# --- ROUTES DLA ADMINISTRATORA ---
@app.route('/admin')
@admin_required
def admin_dashboard():
    user = get_current_user()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM facilities ORDER BY name")
    facilities = cursor.fetchall()
    conn.close()
    return template('admin_dashboard_template', user=user, facilities=facilities)

@app.route('/admin/facility/<facility_id:int>/reservations')
@admin_required
def admin_facility_reservations(facility_id):
    user = get_current_user()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM facilities WHERE id = ?", (facility_id,))
    facility_name_tuple = cursor.fetchone()
    if not facility_name_tuple:
        conn.close()
        return "Ośrodek nie znaleziony."
    facility_name = facility_name_tuple[0]
    filter_date_str = request.query.get('filter_date')
    filter_court_type = request.query.get('filter_court_type')
    sort_by = request.query.get('sort_by', 'reservation_date')
    sort_order = request.query.get('sort_order', 'ASC')
    allowed_sort_columns = ['reservation_date', 'start_hour', 'u.username', 'c.court_type', 'f.name'] # f.name tu nie ma sensu
    if sort_by not in allowed_sort_columns:
        sort_by = 'reservation_date'
    if sort_order.upper() not in ['ASC', 'DESC']:
        sort_order = 'ASC'
    sql_query = f"""
        SELECT r.id, r.reservation_date, r.start_hour,
               c.court_number, c.court_type, f.name as facility_name,
               u.username as user_username
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        JOIN facilities f ON c.facility_id = f.id
        JOIN users u ON r.user_id = u.id
        WHERE f.id = ?
    """
    params = [facility_id]
    if filter_date_str:
        try:
            filter_date = datetime.date.fromisoformat(filter_date_str)
            sql_query += " AND r.reservation_date = ?"
            params.append(filter_date)
        except ValueError:
            filter_date_str = None
    if filter_court_type:
        sql_query += " AND c.court_type = ?"
        params.append(filter_court_type)
    sql_query += f" ORDER BY {sort_by} {sort_order.upper()}"
    cursor.execute(sql_query, params)
    reservations_raw = cursor.fetchall()

    cursor.execute("SELECT DISTINCT court_type FROM courts WHERE facility_id = ?", (facility_id,))
    available_court_types_raw = cursor.fetchall()
    available_court_types = [row[0] for row in available_court_types_raw]
    conn.close()

    type_names_map_display = {
        'ziemny': 'Ziemny',
        'twardy_hala': 'Twardy (Hala)',
        'trawa': 'Trawiasty'
    }
    reservations = []
    for res_id, res_date, start_hour, c_num, c_type, fac_name, u_name in reservations_raw:
        reservations.append({
            'id': res_id,
            'date_str': res_date.strftime('%Y-%m-%d') if isinstance(res_date, datetime.date) else res_date,
            'time_str': f"{start_hour:02d}:00 - {start_hour+1:02d}:00",
            'court_info': f"{type_names_map_display.get(c_type, c_type)} nr {c_num}",
            'facility_name': fac_name,
            'username': u_name
        })
    return template('admin_facility_reservations_template', 
                    user=user, 
                    facility_id=facility_id,
                    facility_name=facility_name,
                    reservations=reservations,
                    available_court_types=available_court_types,
                    current_filters={'date': filter_date_str, 'court_type': filter_court_type},
                    current_sort={'by': sort_by, 'order': sort_order.lower()})

@app.route('/admin/reservations/delete/<reservation_id:int>', method='POST')
@admin_required
def admin_delete_reservation(reservation_id):
    facility_id_redirect = request.forms.get('facility_id_redirect')
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Błąd admina przy usuwaniu rezerwacji {reservation_id}: {e}")
    finally:
        conn.close()
    if facility_id_redirect:
        return redirect(f'/admin/facility/{facility_id_redirect}/reservations')
    return redirect('/admin')

@app.route('/admin/facility/<facility_id:int>/courts')
@admin_required
def admin_manage_courts(facility_id):
    user = get_current_user()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM facilities WHERE id = ?", (facility_id,))
    facility_name_tuple = cursor.fetchone()
    if not facility_name_tuple:
        conn.close()
        return "Ośrodek nie znaleziony."
    facility_name = facility_name_tuple[0]
    cursor.execute("SELECT id, court_number, court_type FROM courts WHERE facility_id = ? ORDER BY court_number", (facility_id,))
    courts_raw = cursor.fetchall()
    conn.close()
    type_names_map_display = {
        'ziemny': 'Ziemny',
        'twardy_hala': 'Twardy (Hala)',
        'trawa': 'Trawiasty'
    }
    courts = [{'id': c_id, 'number': c_num, 'type': c_type, 'type_display': type_names_map_display.get(c_type, c_type)} 
              for c_id, c_num, c_type in courts_raw]
    all_court_types = ['ziemny', 'twardy_hala', 'trawa']
    
    # Obsługa komunikatów o błędach/sukcesach z redirectów
    error_code = request.query.get('error')
    success_code = request.query.get('success')
    error_msg = None
    success_msg = None

    if error_code:
        error_map = {
            'MissingFields': "Wszystkie pola są wymagane do dodania kortu.",
            'InvalidCourtNumber': "Nieprawidłowy numer kortu.",
            'InvalidCourtType': "Nieprawidłowy typ kortu.",
            'CourtNumberExists': "Kort o podanym numerze już istnieje w tym ośrodku.",
            'CannotDeleteCourtWithFutureReservations': "Nie można usunąć kortu, który ma przyszłe rezerwacje. Anuluj najpierw rezerwacje."
        }
        error_msg = error_map.get(error_code, f"Nieznany błąd: {error_code}")
        if 'DbError' in error_code: error_msg = f"Błąd bazy danych: {error_code}"

    if success_code:
        success_map = {
            'CourtAdded': "Kort został pomyślnie dodany.",
            'CourtDeleted': "Kort został pomyślnie usunięty."
        }
        success_msg = success_map.get(success_code, f"Operacja zakończona: {success_code}")
        if 'DbError' in success_code: success_msg = f"Operacja zakończona, ale z błędem bazy: {success_code}"


    return template('admin_manage_courts_template', 
                    user=user, 
                    facility_id=facility_id,
                    facility_name=facility_name, 
                    courts=courts,
                    all_court_types=all_court_types,
                    error_msg=error_msg, 
                    success_msg=success_msg)


@app.route('/admin/facility/<facility_id:int>/courts/add', method='POST')
@admin_required
def admin_add_court(facility_id):
    court_number_str = request.forms.get('court_number')
    court_type = request.forms.get('court_type')
    redirect_url_base = f'/admin/facility/{facility_id}/courts'

    if not court_number_str or not court_type:
        return redirect(f'{redirect_url_base}?error=MissingFields')
    try:
        court_number = int(court_number_str)
        if court_number <= 0: raise ValueError
    except ValueError:
        return redirect(f'{redirect_url_base}?error=InvalidCourtNumber')
    all_court_types = ['ziemny', 'twardy_hala', 'trawa']
    if court_type not in all_court_types:
        return redirect(f'{redirect_url_base}?error=InvalidCourtType')

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM courts WHERE facility_id = ? AND court_number = ?", (facility_id, court_number))
        if cursor.fetchone():
            conn.close()
            return redirect(f'{redirect_url_base}?error=CourtNumberExists')
        cursor.execute("INSERT INTO courts (facility_id, court_number, court_type) VALUES (?, ?, ?)",
                       (facility_id, court_number, court_type))
        conn.commit()
        redirect_query = "?success=CourtAdded"
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Błąd admina przy dodawaniu kortu: {e}")
        redirect_query = f"?error=DbError_{e}"
    finally:
        conn.close()
    return redirect(f'{redirect_url_base}{redirect_query}')

@app.route('/admin/courts/delete/<court_id:int>', method='POST')
@admin_required
def admin_delete_court(court_id):
    facility_id_redirect = request.forms.get('facility_id_redirect')
    redirect_url_base = f'/admin/facility/{facility_id_redirect}/courts' if facility_id_redirect else '/admin'
    query_params = ""

    conn = connect_db()
    cursor = conn.cursor()
    try:
        today = datetime.date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM reservations WHERE court_id = ? AND reservation_date >= ?", (court_id, today))
        future_reservations_count = cursor.fetchone()[0]
        if future_reservations_count > 0:
            query_params = "?error=CannotDeleteCourtWithFutureReservations"
        else:
            cursor.execute("DELETE FROM courts WHERE id = ?", (court_id,))
            conn.commit()
            query_params = "?success=CourtDeleted"
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Błąd admina przy usuwaniu kortu {court_id}: {e}")
        query_params = f"?error=DbError_{e}"
    finally:
        conn.close()
    return redirect(f'{redirect_url_base}{query_params}')


# --- URUCHOMIENIE APLIKACJI ---
if __name__ == '__main__':
    init_db()
    if not os.path.exists('./session_data'):
        os.makedirs('./session_data')
    
    # Przekazanie funkcji i modułów do wszystkich szablonów
    from bottle import SimpleTemplate
    SimpleTemplate.defaults['get_current_user'] = get_current_user
    SimpleTemplate.defaults['datetime'] = datetime
        
    app_with_session = SessionMiddleware(app, session_opts)
    run(app_with_session, host='localhost', port=8080, debug=True, reloader=True)