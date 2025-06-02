% rebase('base_layout.tpl', title=f'Korty w {facility_name}')
<h2>Dostępne korty w ośrodku: {{facility_name}}</h2>
<p><a href="/facilities" class="button-secondary">« Powrót do listy ośrodków</a></p>
% if not courts:
    <p>Brak dostępnych kortów w tym ośrodku.</p>
% else:
    % for court in courts:
        <div class="court-box">
            <h4>{{court['name']}}</h4>
            <a href="/court/{{court['id']}}/book" class="button">Rezerwuj ten kort</a>
        </div>
    % end
% end