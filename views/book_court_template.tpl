% rebase('base_layout.tpl', title=f"Rezerwacja: {court_info['full_name']}")
% import datetime 

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
        % price_display = slot_prices.get(hour, 'N/A')
        <div style="margin: 5px; padding: 10px; border: 1px solid {{'red' if is_booked else 'green'}}; background-color: {{'#ffdddd' if is_booked else '#ddffdd'}};">
            <input type="checkbox" name="time_slots" value="{{hour}}" id="slot_{{hour}}" {{'disabled' if is_booked else ''}} 
                   onchange="updateTotalPrice()"> <!-- Dodajemy event do przeliczania ceny -->
            <label for="slot_{{hour}}" style="font-weight: normal; {{'text-decoration: line-through;' if is_booked else ''}}">
                {{hour_str}} 
                % if is_booked:
                    (Zajęty)
                % else:
                    ({{price_display}}) <!-- Wyświetl cenę dla slotu -->
                % end
            </label>
            <!-- Ukryte pole z ceną dla JavaScript -->
            <input type="hidden" id="price_{{hour}}" value="{{slot_prices.get(hour, '0').replace(' zł', '').replace('N/A', '0') if not is_booked else '0'}}">
        </div>
    % end
    </div>
    <br>
    <div id="total-price-container" style="margin-top:10px; font-weight:bold;">
        Całkowita cena: <span id="total-price-value">0.00 zł</span>
    </div>
    <br>
    <input type="submit" value="Zarezerwuj wybrane godziny">
</form>

<script>
function updateTotalPrice() {
    let total = 0;
    const checkboxes = document.querySelectorAll('input[name="time_slots"]:checked');
    checkboxes.forEach(function(checkbox) {
        const hour = checkbox.value;
        const priceInput = document.getElementById('price_' + hour);
        if (priceInput) {
            const price = parseFloat(priceInput.value);
            if (!isNaN(price)) {
                total += price;
            }
        }
    });
    document.getElementById('total-price-value').textContent = total.toFixed(2) + ' zł';
}
// Wywołaj raz przy ładowaniu, jeśli są jakieś pre-selekcjonowane checkboxy (choć tutaj nie powinno być)
// updateTotalPrice();
</script>