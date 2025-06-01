<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title if defined('title') else 'System Rezerwacji Kortów'}}</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        header { background-color: #333; color: white; padding: 10px 20px; margin-bottom: 20px; }
        header h1 { margin: 0; display: inline-block; }
        nav { float: right; }
        nav ul { list-style-type: none; margin: 0; padding: 0; }
        nav ul li { display: inline; margin-left: 15px; }
        nav ul li a { color: white; text-decoration: none; }
        nav ul li a:hover { text-decoration: underline; }
        .container { background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .facility-box { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 4px; background-color: #fff; }
        .facility-box h3 { margin-top: 0; }
        .court-box { border: 1px solid #eee; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .button, input[type=submit] { background-color: #5cb85c; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .button:hover, input[type=submit]:hover { background-color: #4cae4c; }
        .button-danger { background-color: #d9534f; }
        .button-danger:hover { background-color: #c9302c; }
        .button-secondary { background-color: #6c757d; }
        .button-secondary:hover { background-color: #5a6268; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type=text], input[type=password], input[type=date], select, input[type=number] { width: calc(100% - 22px); padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .error { color: red; margin-bottom: 10px; }
        .success { color: green; margin-bottom: 10px; }
        .reservation-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .reservation-item:last-child { border-bottom: none; }
        .filter-form { margin-bottom: 20px; padding: 10px; background-color: #f9f9f9; border: 1px solid #eee; border-radius: 4px; }
        .filter-form label, .filter-form select, .filter-form input[type=date], .filter-form input[type=submit], .filter-form .button-secondary { margin-right: 10px; display: inline-block; vertical-align: middle; margin-bottom: 5px;}
        .filter-form input[type=text], .filter-form input[type=number], .filter-form select { width: auto; min-width: 150px;}
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <header>
        <h1><a href="/" style="color: white; text-decoration: none;">System Rezerwacji Kortów</a></h1>
        <nav>
            <ul>
                % user_info = get_current_user() # Musimy mieć dostęp do tej funkcji w szablonie bazowym
                % if user_info:
                    % if user_info['role'] == 'admin':
                        <li><a href="/admin">Panel Admina</a></li>
                    % end
                    <li><a href="/facilities">Zarezerwuj Kort</a></li>
                    <li><a href="/my_reservations">Historia Rezerwacji</a></li>
                    <li>Witaj, {{user_info['username']}} (<a href="/logout">Wyloguj</a>)</li>
                % else:
                    <li><a href="/register">Załóż konto</a></li>
                    <li><a href="/login">Zaloguj</a></li>
                % end
            </ul>
        </nav>
        <div style="clear:both;"></div>
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