% rebase('base_layout.tpl', title='Strona Główna')
<h2>Witaj w systemie rezerwacji kortów tenisowych!</h2>
% if defined('message') and message:
    <p class="success">{{message}}</p>
% end
<p>Znajdź i zarezerwuj kort w jednym z naszych ośrodków.</p>
<img src="/static/moje_zdjecie.jpg" alt="Mój piękny kort" style="max-width:100%; height:auto; margin-top:20px;">