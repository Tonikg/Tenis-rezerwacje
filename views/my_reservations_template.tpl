% rebase('base_layout.tpl', title='Moje Rezerwacje')
<h2>Moje Rezerwacje</h2>
% if defined('message') and message:
    <p class="success">{{message}}</p>
% end

% if not reservations:
    <p>Nie masz jeszcze żadnych rezerwacji.</p>
% else:
    <table>
        <thead>
            <tr>
                <th>Data</th>
                <th>Godziny</th>
                <th>Ośrodek</th>
                <th>Kort</th>
                <th>Cena</th>
                <th>Anuluj rezerwację</th>
            </tr>
        </thead>
        <tbody>
        % for res in reservations:
            <tr>
                <td>{{res['date_str']}}</td>
                <td>{{res['time_str']}}</td>
                <td>{{res['facility_name']}}</td>
                <td>{{res['court_info']}}</td>
                <td>
                    % if res.get('price_paid') is not None:
                        {{ "%.2f zł" % res['price_paid'] }}
                    % else:
                        N/A
                    % end
                </td>
                <td>
                    % if res['can_cancel']:
                        <form method="POST" action="/reservations/cancel/{{res['id']}}" style="display:inline;" onsubmit="return confirm('Czy na pewno chcesz anulować tę rezerwację?');">
                            <input type="submit" value="Anuluj" class="button-danger">
                        </form>
                    % else:
                        Nie możesz anulować.
                    % end
                </td>
            </tr>
        % end
        </tbody>
    </table>
% end