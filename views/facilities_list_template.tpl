% rebase('base_layout.tpl', title='Dostępne Ośrodki')
<h2>Wybierz ośrodek tenisowy</h2>

<!-- ... (formularz filtrów bez zmian) ... -->
<form method="GET" action="/facilities" class="filter-form">
    <label for="court_type_filter">Filtruj wg typu kortu:</label>
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
        <div class="facility-box-row"> <!-- Zmieniona główna klasa na .facility-box-row -->
            
            <!-- Kolumna 1: Informacje tekstowe -->
            <div class="facility-column facility-info">
                <p><strong>Adres:</strong> {{facility['address']}}</p>
                <p><strong>Rodzaje kortów:</strong> {{facility['court_types_summary']}}</p>
                <a href="/facility/{{facility['id']}}" class="button">Zobacz korty i zarezerwuj</a>
            </div>

            <!-- Kolumna 2: Zdjęcie -->
            <div class="facility-column facility-photo">
                % if facility.get('photo_url'):
                    <img src="{{facility['photo_url']}}" alt="Zdjęcie {{facility['name']}}" style="max-width: 100%; height: auto; border-radius: 4px;">
                % else:
                    <div style="width:200px; height:150px; background-color:#eee; display:flex; align-items:center; justify-content:center; text-align:center; color:#888; border-radius:4px;">Brak zdjęcia</div>
                % end
            </div>

            <!-- Kolumna 3: Mapa OSM -->
            <div class="facility-column facility-map">
                % if facility.get('osm_embed_code') and "OSM_CODE_" not in facility['osm_embed_code'] and "TUTAJ_WKLEJ_KOD_OSM" not in facility['osm_embed_code']:
                    <div>{{!facility['osm_embed_code']}}</div> 
                % else:
                    <p style="text-align:center; color:#888; margin-top:20px;">(Mapa OSM wkrótce)</p>
                % end
            </div>

        </div> <!-- Koniec .facility-box-row -->
    % end
% end