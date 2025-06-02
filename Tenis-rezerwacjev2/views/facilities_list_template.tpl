% rebase('base_layout.tpl', title='Dostępne Ośrodki')
<h2>Wybierz ośrodek tenisowy</h2>

<form method="GET" action="/facilities" class="filter-form">
    <label for="court_type_filter">Filtruj wg rodzaju kortu:</label>
    <select name="court_type" id="court_type_filter" onchange="this.form.submit()">
        <option value="">Wszystkie typy</option>
        % for type_key in available_court_types:
            % type_display = {'ziemny': 'Ziemne', 'twardy_hala': 'Twarde (hala)', 'trawa': 'Na trawie'}.get(type_key, type_key.capitalize())
            <option value="{{type_key}}" {{'selected' if selected_filter == type_key else ''}}>
                {{type_display}}
            </option>
        % end
    </select>
    <noscript><input type="submit" value="Filtruj"></noscript>
</form>

% if not facilities:
    <p>Brak ośrodków spełniających kryteria lub brak ośrodków w systemie.</p>
% else:
    % for facility in facilities:
        <div class="facility-box">
            <h3>{{facility['name']}}</h3>
            <p><strong>Adres:</strong> {{facility['address']}}</p>
            <p><strong>Rodzaje kortów:</strong> {{facility['court_types_summary']}}</p>
            % if facility.get('photo_url'):
                <img src="{{facility['photo_url']}}" alt="Zdjęcie {{facility['name']}}" style="max-width: 200px; height: auto; margin-bottom: 10px;">
            % end
            <div>{{!facility['osm_embed_code']}}</div> <!-- Używamy {{! ... }} aby HTML nie był escapowany -->
            <a href="/facility/{{facility['id']}}" class="button">Zobacz korty i zarezerwuj</a>
        </div>
    % end
% end