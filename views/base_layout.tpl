<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title if defined('title') else 'System Rezerwacji Kortów Tennis Reservoire'}}</title>
    <link rel="stylesheet" type="text/css" href="/static/css/style.css">
</head>
<body style="background-color:rgb(255, 255, 255);">
    <header>
        <h1><a href="/" style="color: white; text-decoration: none;">System Rezerwacji Kortów</a></h1>
            <nav>
                <ul>
                    % user_info = get_current_user()
                    % if user_info:
                        % if user_info['role'] == 'admin':
                            <li><a href="/admin">Panel Admina</a></li>
                        % end
                        <li><a href="/facilities">Zarezerwuj Kort</a></li>
                        <li><a href="/my_reservations">Historia Rezerwacji</a></li>
                        <li><a href="/booking-rules">Zasady Rezerwacji</a></li>
                        <li class="user-info-logout">Witaj, {{user_info['username']}} (<a href="/logout">Wyloguj</a>)</li>
                    % else: # Niezalogowany użytkownik
			<li><a href="/our-centers">Nasze Ośrodki</a></li> 
                        <li><a href="/register">Załóż konto</a></li>
                        <li><a href="/booking-rules">Zasady Rezerwacji</a></li>
                        <li><a href="/login">Zaloguj</a></li>
                    % end
                </ul>
            </nav>
    </header>
    <div class="container">
        {{!base}} <!-- Tutaj zostanie wstawiona treść konkretnej strony -->
    </div>
    <footer>
        % import datetime # Import datetime, aby użyć go tutaj
        <p style="text-align: center; margin-top: 20px; color: #777;">© {{datetime.date.today().year}} Tennis Reservoir</p>
    </footer>
</body>
</html>