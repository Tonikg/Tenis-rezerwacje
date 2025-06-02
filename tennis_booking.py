# tennis_booking.py

# --- IMPORTY ---
# Bottle to lekki framework webowy WSGI dla Pythona.
# Teraz importujemy `TEMPLATE_PATH` aby dodać ścieżkę do naszych szablonów
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

# --- FUNKCJE POMOCNICZE DLA BAZY DANYCH ---
# (bez zmian - skopiuj z oryginalnego kodu)
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                osm_embed_code TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                facility_id INTEGER NOT NULL,
                court_number INTEGER NOT NULL,
                court_type TEXT NOT NULL,
                FOREIGN KEY (facility_id) REFERENCES facilities(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                court_id INTEGER NOT NULL,
                reservation_date DATE NOT NULL,
                start_hour INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (court_id) REFERENCES courts(id)
            )
        ''')
        admin_pass_hash = hash_password('admin123')
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           ('admin', admin_pass_hash, 'admin'))
            print("Dodano domyślnego admina: login 'admin', hasło 'admin123'")
        except sqlite3.IntegrityError:
            print("Admin już istnieje.")
        facilities_data = [
            (1, "Park Skaryszewski", "Aleja Zieleniecka 2, Warszawa", '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0487,52.2470,21.0527,52.2490&layer=mapnik&marker=52.2480,21.0507" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.2480&mlon=21.0507#map=17/52.2480/21.0507">Zobacz większą mapę</a></small>'),
            (2, "Korty Solec", "ul. Solec 25, Warszawa", '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0370,52.2310,21.0410,52.2330&layer=mapnik&marker=52.2320,21.0390" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.2320&mlon=21.0390#map=17/52.2320/21.0390">Zobacz większą mapę</a></small>'),
            (3, "Korty Paryska", "ul. Paryska 10, Warszawa", '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=21.0620,52.2410,21.0660,52.2430&layer=mapnik&marker=52.2420,21.0640" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=52.2420&mlon=21.0640#map=17/52.2420/21.0640">Zobacz większą mapę</a></small>')
        ]
        cursor.executemany("INSERT INTO facilities (id, name, address, osm_embed_code) VALUES (?, ?, ?, ?)", facilities_data)
        courts_data = [
            (1, 1, 'ziemny'), (1, 2, 'ziemny'), (1, 3, 'ziemny'), (1, 4, 'ziemny'), (1, 5, 'ziemny'), (1, 6, 'ziemny'),
            (2, 1, 'ziemny'), (2, 2, 'ziemny'), (2, 3, 'ziemny'), (2, 4, 'ziemny'),
            (2, 5, 'twardy_hala'), (2, 6, 'twardy_hala'), (2, 7, 'twardy_hala'), (2, 8, 'twardy_hala'),
            (3, 1, 'ziemny'), (3, 2, 'ziemny'), (3, 3, 'ziemny'), (3, 4, 'trawa')
        ]
        for facility_id, court_num, court_type in courts_data:
            cursor.execute("INSERT INTO courts (facility_id, court_number, court_type) VALUES (?, ?, ?)",
                           (facility_id, court_num, court_type))
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
# (bez zmian - skopiuj z oryginalnego kodu)
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
    stock_photo_url = "/static/img/court_placeholder.jpg" # Przykład, jeśli masz obrazek
    # stock_photo_url = "https://via.placeholder.com/800x300.png?text=Zdjęcie+Kortu+Tenisowego+(Wstaw+Własne)" 
    
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

# --- TRASY DLA ZALOGOWANEGO UŻYTKOWNIKA ---

@app.route('/facilities')
@login_required
def list_facilities():
    user = get_current_user() 
    filter_court_type = request.query.get('court_type')
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT id, name, address, osm_embed_code FROM facilities"
    params = []
    if filter_court_type:
        query = """
            SELECT DISTINCT f.id, f.name, f.address, f.osm_embed_code
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
        facility_id, name, address, osm_code = facility_raw
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
            'osm_embed_code': osm_code
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


@app.route('/court/<court_id:int>/book', method=['GET', 'POST'])
@login_required
def book_court(court_id):
    user = get_current_user()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.court_number, c.court_type, c.facility_id, f.name as facility_name
        FROM courts c
        JOIN facilities f ON c.facility_id = f.id
        WHERE c.id = ?
    """, (court_id,))
    court_data = cursor.fetchone() # Nie zamykaj połączenia tutaj, jeśli będziesz go jeszcze używać

    if not court_data:
        conn.close()
        return "Kort nie znaleziony."

    court_info = {
        'id': court_data[0], 
        'number': court_data[1], 
        'type': court_data[2], 
        'facility_id': court_data[3],
        'facility_name': court_data[4]
    }
    type_names_map_single = {
        'ziemny': 'Kort ziemny',
        'twardy_hala': 'Kort z nawierzchnią twardą (hala)',
        'trawa': 'Kort na trawie'
    }
    court_info['full_name'] = f"{type_names_map_single.get(court_info['type'], court_info['type'])} nr {court_info['number']} w {court_info['facility_name']}"
    
    selected_date_str = request.query.get('date', datetime.date.today().isoformat())
    try:
        selected_date = datetime.date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = datetime.date.today()

    available_hours = list(range(10, 21))
    
    # Pobranie istniejących rezerwacji dla tego kortu i daty - użyj już otwartego połączenia
    cursor.execute("""
        SELECT start_hour FROM reservations
        WHERE court_id = ? AND reservation_date = ?
    """, (court_id, selected_date))
    booked_hours_tuples = cursor.fetchall()
    # conn.close() # Zamknij dopiero po wszystkich operacjach odczytu dla GET
    booked_hours = {bh[0] for bh in booked_hours_tuples}

    if request.method == 'POST':
        # Ponowne otwarcie połączenia, jeśli było zamknięte, lub użycie istniejącego kursora
        # Dla POST lepiej zarządzać połączeniem wewnątrz bloku POST
        # conn_post = connect_db() # lub użyj conn, jeśli nie zostało zamknięte
        # cursor_post = conn_post.cursor()
        cursor_post = cursor # Użyjemy tego samego kursora, jeśli połączenie jest nadal otwarte

        selected_slots_str = request.forms.getall('time_slots')
        
        if not selected_slots_str:
            conn.close() # Zamknij połączenie otwarte na początku funkcji
            return template('book_court_template', user=user, court_info=court_info, 
                            available_hours=available_hours, booked_hours=booked_hours,
                            selected_date=selected_date.isoformat(), error="Musisz wybrać przynajmniej jedną godzinę.",
                            datetime=datetime) # Przekaż datetime

        selected_slots = sorted([int(s) for s in selected_slots_str])

        if len(selected_slots) > 3:
            conn.close()
            return template('book_court_template', user=user, court_info=court_info, 
                            available_hours=available_hours, booked_hours=booked_hours,
                            selected_date=selected_date.isoformat(), error="Możesz zarezerwować maksymalnie 3 godziny na raz.",
                            datetime=datetime)

        for i in range(len(selected_slots) - 1):
            if selected_slots[i+1] - selected_slots[i] != 1:
                conn.close()
                return template('book_court_template', user=user, court_info=court_info, 
                                available_hours=available_hours, booked_hours=booked_hours,
                                selected_date=selected_date.isoformat(), error="Godziny muszą być po kolei (np. 13:00, 14:00, 15:00).",
                                datetime=datetime)
        
        for slot_hour in selected_slots:
            cursor_post.execute("""
                SELECT id FROM reservations
                WHERE court_id = ? AND reservation_date = ? AND start_hour = ?
            """, (court_id, selected_date, slot_hour))
            if cursor_post.fetchone():
                cursor_post.execute("SELECT start_hour FROM reservations WHERE court_id = ? AND reservation_date = ?", (court_id, selected_date))
                newly_booked_hours = {bh[0] for bh in cursor_post.fetchall()}
                conn.close() # Zamknij połączenie
                return template('book_court_template', user=user, court_info=court_info, 
                                available_hours=available_hours, booked_hours=newly_booked_hours,
                                selected_date=selected_date.isoformat(), error=f"Godzina {slot_hour}:00 została właśnie zarezerwowana. Wybierz inne.",
                                datetime=datetime)
        
        cursor_post.execute("""
            SELECT COUNT(*) FROM reservations r
            JOIN courts c ON r.court_id = c.id
            WHERE r.user_id = ? AND c.facility_id = ? AND r.reservation_date = ?
        """, (user['id'], court_info['facility_id'], selected_date))
        hours_already_booked_by_user_in_facility = cursor_post.fetchone()[0]

        if hours_already_booked_by_user_in_facility + len(selected_slots) > 3:
            conn.close() # Zamknij połączenie
            return template('book_court_template', user=user, court_info=court_info, 
                            available_hours=available_hours, booked_hours=booked_hours,
                            selected_date=selected_date.isoformat(), error=f"Przekraczasz dzienny limit 3 godzin rezerwacji w tym ośrodku (masz już zarezerwowane {hours_already_booked_by_user_in_facility}h).",
                            datetime=datetime)

        try:
            for slot_hour in selected_slots:
                cursor_post.execute("""
                    INSERT INTO reservations (user_id, court_id, reservation_date, start_hour)
                    VALUES (?, ?, ?, ?)
                """, (user['id'], court_id, selected_date, slot_hour))
            conn.commit() # Użyj oryginalnego obiektu połączenia 'conn'
        except sqlite3.Error as e:
            conn.rollback()
            conn.close() # Zamknij połączenie
            return template('book_court_template', user=user, court_info=court_info, 
                            available_hours=available_hours, booked_hours=booked_hours,
                            selected_date=selected_date.isoformat(), error=f"Błąd bazy danych podczas rezerwacji: {e}",
                            datetime=datetime)
        # finally: # Usunięcie finally, bo conn jest zamykane w różnych miejscach
            # conn.close() # Zamknij połączenie
            
        conn.close() # Zamknij połączenie po udanej operacji POST
        return redirect('/my_reservations?success=true')

    conn.close() # Zamknij połączenie otwarte na początku funkcji (dla GET)
    return template('book_court_template', user=user, court_info=court_info, 
                    available_hours=available_hours, booked_hours=booked_hours,
                    selected_date=selected_date.isoformat(), error=None,
                    datetime=datetime) # Przekaż datetime dla min daty


@app.route('/my_reservations')
@login_required
def my_reservations():
    user = get_current_user()
    success_message = request.query.get('success')
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.reservation_date, r.start_hour,
               c.court_number, c.court_type, f.name as facility_name
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        JOIN facilities f ON c.facility_id = f.id
        WHERE r.user_id = ?
        ORDER BY r.reservation_date DESC, r.start_hour DESC
    """, (user['id'],))
    reservations_raw = cursor.fetchall()
    conn.close()
    type_names_map = {
        'ziemny': 'Kort ziemny',
        'twardy_hala': 'Kort z naw. twardą (hala)',
        'trawa': 'Kort na trawie'
    }
    today = datetime.date.today()
    reservations = []
    for res_id, res_date_obj, start_hour, court_num, court_type, facility_name in reservations_raw:
        can_cancel = res_date_obj >= today
        reservations.append({
            'id': res_id,
            'date_str': res_date_obj.strftime('%Y-%m-%d'),
            'time_str': f"{start_hour:02d}:00 - {start_hour+1:02d}:00",
            'court_info': f"{type_names_map.get(court_type, court_type)} nr {court_num}",
            'facility_name': facility_name,
            'can_cancel': can_cancel
        })
    message = "Rezerwacja zakończona pomyślnie!" if success_message else None
    return template('my_reservations_template', user=user, reservations=reservations, message=message)

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

# --- TRASY DLA ADMINISTRATORA ---

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
    # conn.close() # Zamknij po wszystkich operacjach odczytu

    # Dostępne typy kortów do filtrowania (z tego ośrodka)
    # conn_types = connect_db() # niepotrzebne nowe połączenie
    # cursor_types = conn_types.cursor()
    cursor.execute("SELECT DISTINCT court_type FROM courts WHERE facility_id = ?", (facility_id,))
    available_court_types_raw = cursor.fetchall()
    available_court_types = [row[0] for row in available_court_types_raw]
    conn.close() # Teraz zamknij połączenie

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
                    error_msg=error_msg, # Przekazujemy przetworzoną wiadomość
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
            # Można rozważyć usunięcie WSZYSTKICH rezerwacji (także historycznych) dla tego kortu
            # cursor.execute("DELETE FROM reservations WHERE court_id = ?", (court_id,))
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


# --- DEFINICJE SZABLONÓW (HTML) ---
# JUŻ NIEPOTRZEBNE, bo szablony są w plikach .tpl
# SimpleTemplate.defaults["user"] = None # To też nie jest już najlepsze miejsce
# SimpleTemplate.defaults["base_layout"] = """...""" # Usunięte


# --- URUCHOMIENIE APLIKACJI ---
if __name__ == '__main__':
    init_db()
    if not os.path.exists('./session_data'):
        os.makedirs('./session_data')
    
    # Przekazanie funkcji i modułów do wszystkich szablonów
    # tak, aby były dostępne np. w base_layout.tpl
    # oraz datetime w book_court.tpl
    from bottle import SimpleTemplate
    SimpleTemplate.defaults['get_current_user'] = get_current_user
    SimpleTemplate.defaults['datetime'] = datetime # udostępnia cały moduł datetime
        
    app_with_session = SessionMiddleware(app, session_opts)
    run(app_with_session, host='localhost', port=8080, debug=True, reloader=True)