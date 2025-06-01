% rebase('base_layout.tpl', title='Logowanie')
<h2>Zaloguj się</h2>
% if error:
    <p class="error">{{error}}</p>
% end
<form method="POST" action="/login">
    <label for="username">Nazwa użytkownika:</label>
    <input type="text" id="username" name="username" required><br>
    <label for="password">Hasło:</label>
    <input type="password" id="password" name="password" required><br>
    <input type="submit" value="Zaloguj">
</form>
<p>Nie masz konta? <a href="/register">Zarejestruj się</a>.</p>