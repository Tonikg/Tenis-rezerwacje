% rebase('base_layout.tpl', title=f"Zarządzanie kortami w {facility_name}")
<h2>Zarządzanie kortami w ośrodku: {{facility_name}}</h2>
<p><a href="/admin" class="button-secondary">« Powrót do panelu admina</a></p>

% if defined('error_msg') and error_msg: <!-- Zmieniona nazwa zmiennej dla czytelności -->
    <p class="error">{{error_msg}}</p>
% end
% if defined('success_msg') and success_msg: <!-- Zmieniona nazwa zmiennej -->
    <p class="success">{{success_msg}}</p>
% end

<h3>Dodaj nowy kort</h3>
<form method="POST" action="/admin/facility/{{facility_id}}/courts/add" class="filter-form">
    <label for="court_number">Numer kortu:</label>
    <input type="number" id="court_number" name="court_number" min="1" required>
    
    <label for="court_type">Typ kortu:</label>
    <select id="court_type" name="court_type" required>
        % for type_key in all_court_types:
            % type_display = {'ziemny': 'Ziemny', 'twardy_hala': 'Twardy (Hala)', 'trawa': 'Trawiasty'}.get(type_key, type_key.capitalize())
            <option value="{{type_key}}">{{type_display}}</option>
        % end
    </select>
    <input type="submit" value="Dodaj kort">
</form>

<h3>Istniejące korty</h3>
% if not courts:
    <p>Brak kortów w tym ośrodku.</p>
% else:
    <table>
        <thead>
            <tr>
                <th>Numer Kortu</th>
                <th>Typ Kortu</th>
                <th>Akcje</th>
            </tr>
        </thead>
        <tbody>
        % for court in courts:
            <tr>
                <td>{{court['number']}}</td>
                <td>{{court['type_display']}}</td>
                <td>
                    <form method="POST" action="/admin/courts/delete/{{court['id']}}" style="display:inline;" onsubmit="return confirm('Czy na pewno chcesz usunąć ten kort? To działanie może wpłynąć na istniejące rezerwacje.');">
                        <input type="hidden" name="facility_id_redirect" value="{{facility_id}}">
                        <input type="submit" value="Usuń kort" class="button-danger">
                    </form>
                </td>
            </tr>
        % end
        </tbody>
    </table>
% end