% rebase('base_layout.tpl', title=f"Rezerwacje w {facility_name}")
<h2>Rezerwacje w ośrodku: {{facility_name}}</h2>
<p><a href="/admin" class="button-secondary">« Powrót do panelu admina</a></p>

<form method="GET" action="/admin/facility/{{facility_id}}/reservations" class="filter-form">
    <input type="hidden" name="sort_by" value="{{current_sort.get('by', 'reservation_date')}}"> <!-- Dodane .get dla bezpieczeństwa -->
    <input type="hidden" name="sort_order" value="{{current_sort.get('order', 'asc')}}">
    
    <label for="filter_date">Data:</label>
    <input type="date" id="filter_date" name="filter_date" value="{{current_filters.get('date', '')}}">
    
    <label for="filter_court_type">Typ kortu:</label>
    <select name="filter_court_type" id="filter_court_type">
        <option value="">Wszystkie typy</option>
        % for type_key in available_court_types:
            % type_display = {'ziemny': 'Ziemne', 'twardy_hala': 'Twarde (hala)', 'trawa': 'Na trawie'}.get(type_key, type_key.capitalize())
            <option value="{{type_key}}" {{'selected' if current_filters.get('court_type') == type_key else ''}}>
                {{type_display}}
            </option>
        % end
    </select>
    <input type="submit" value="Filtruj">
    <a href="/admin/facility/{{facility_id}}/reservations" class="button-secondary" style="margin-left:10px;">Resetuj filtry</a>
</form>

% if not reservations:
    <p>Brak rezerwacji spełniających kryteria.</p>
% else:
    <table>
        <thead>
            <tr>
                % current_filter_date = current_filters.get('date', '')
                % current_filter_court_type = current_filters.get('court_type', '')
                % current_sort_by = current_sort.get('by', 'reservation_date')
                % current_sort_order = current_sort.get('order', 'asc')
                % sort_link = lambda col_name, display_name: f"<a href='?filter_date={current_filter_date}&filter_court_type={current_filter_court_type}&sort_by={col_name}&sort_order={'desc' if current_sort_by == col_name and current_sort_order == 'asc' else 'asc'}'>{display_name} {'↑' if current_sort_by == col_name and current_sort_order == 'asc' else '↓' if current_sort_by == col_name and current_sort_order == 'desc' else ''}</a>"
                <th>{{!sort_link('reservation_date', 'Data')}}</th>
                <th>{{!sort_link('start_hour', 'Godziny')}}</th>
                <th>Ośrodek</th>
                <th>{{!sort_link('c.court_type', 'Kort')}}</th>
                <th>{{!sort_link('u.username', 'Użytkownik')}}</th>
                <th>Akcja</th>
            </tr>
        </thead>
        <tbody>
        % for res in reservations:
            <tr>
                <td>{{res['date_str']}}</td>
                <td>{{res['time_str']}}</td>
                <td>{{res['facility_name']}}</td>
                <td>{{res['court_info']}}</td>
                <td>{{res['username']}}</td>
                <td>
                    <form method="POST" action="/admin/reservations/delete/{{res['id']}}" style="display:inline;" onsubmit="return confirm('Czy na pewno chcesz usunąć tę rezerwację?');">
                        <input type="hidden" name="facility_id_redirect" value="{{facility_id}}">
                        <input type="submit" value="Usuń" class="button-danger">
                    </form>
                </td>
            </tr>
        % end
        </tbody>
    </table>
% end