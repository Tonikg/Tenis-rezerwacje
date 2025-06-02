% rebase('base_layout.tpl', title='Rejestracja')
<h2>Załóż konto</h2>
% if error:
    <p class="error">{{error}}</p>
% end
<form method="POST" action="/register">
    <label for="username">Nazwa użytkownika:</label>
    <input type="text" id="username" name="username" required><br>
    <label for="password">Hasło:</label>
    <input type="password" id="password" name="password" required><br>
    <label for="password_confirm">Potwierdź hasło:</label>
    <input type="password" id="password_confirm" name="password_confirm" required><br>
    <input type="submit" value="Zarejestruj">
</form>
<p>Masz już konto? <a href="/login">Zaloguj się</a>.</p>