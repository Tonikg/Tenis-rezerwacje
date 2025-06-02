% rebase('base_layout.tpl', title='Panel Administratora')
<h2>Panel Administratora</h2>
<p>Witaj w panelu administracyjnym. Wybierz ośrodek, aby zarządzać jego rezerwacjami lub kortami.</p>
% if not facilities:
    <p>Brak ośrodków w systemie.</p>
% else:
    <h3>Zarządzaj Ośrodkami:</h3>
    <ul>
    % for facility_id, facility_name in facilities:
        <li>
            <strong>{{facility_name}}</strong>
            - <a href="/admin/facility/{{facility_id}}/reservations">Zarządzaj rezerwacjami</a>
            - <a href="/admin/facility/{{facility_id}}/courts">Zarządzaj kortami</a>
        </li>
    % end
    </ul>
% end