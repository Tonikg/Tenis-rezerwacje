% rebase('base_layout.tpl', title=f"Rezerwacja: {court_info['full_name']}")
% import datetime # Potrzebne dla min="{{datetime.date.today().isoformat()}}"

<h2>Rezerwacja: {{court_info['full_name']}}</h2>
<p><a href="/facility/{{court_info['facility_id']}}" class="button-secondary">« Powrót do listy kortów w ośrodku</a></p>

% if error:
    <p class="error">{{error}}</p>
% end

<form method="GET" action="/court/{{court_info['id']}}/book" style="margin-bottom: 20px;">
    <label for="date">Wybierz datę:</label>
    <input type="date" id="date" name="date" value="{{selected_date}}" min="{{datetime.date.today().isoformat()}}" onchange="this.form.submit()">
    <noscript><input type="submit" value="Pokaż dostępne godziny"></noscript>
</form>

<form method="POST" action="/court/{{court_info['id']}}/book?date={{selected_date}}">
    <h4>Dostępne godziny na {{selected_date}}:</h4>
    <p>Możesz zarezerwować maksymalnie 3 kolejne godziny. Godziny rezerwacji: 10:00 - 21:00.</p>
    <div style="display: flex; flex-wrap: wrap;">
    % for hour in available_hours:
        % hour_str = f"{hour:02d}:00 - {hour+1:02d}:00"
        % is_booked = hour in booked_hours
        <div style="margin: 5px; padding: 10px; border: 1px solid {{'red' if is_booked else 'green'}}; background-color: {{'#ffdddd' if is_booked else '#ddffdd'}};">
            <input type="checkbox" name="time_slots" value="{{hour}}" id="slot_{{hour}}" {{'disabled' if is_booked else ''}}>
            <label for="slot_{{hour}}" style="font-weight: normal; {{'text-decoration: line-through;' if is_booked else ''}}">
                {{hour_str}} {{'(Zajęty)' if is_booked else ''}}
            </label>
        </div>
    % end
    </div>
    <br>
    <input type="submit" value="Zarezerwuj wybrane godziny">
</form>