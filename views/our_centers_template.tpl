%rebase('base_layout.tpl', title='Nasze Ośrodki', user=user)

<style>
    .page-header {
        margin-bottom: 20px;
        padding-bottom: 9px;
        border-bottom: 1px solid #eee;
    }
    .carousel-container {
        display: flex;
        overflow-x: auto;
        padding-bottom: 20px;
        scroll-snap-type: x mandatory; 
        -webkit-overflow-scrolling: touch;
    }
    .carousel-slide {
        flex: 0 0 auto;
        width: 300px;
        margin-right: 20px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 15px;
        scroll-snap-align: start;
        text-align: center;
        min-height: 420px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .carousel-slide:last-child {
        margin-right: 0;
    }
    .carousel-slide img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .carousel-slide h3 {
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 1.4em;
        color: #333;
    }
    .carousel-slide h3 a {
        color: inherit;
        text-decoration: none;
    }
    .carousel-slide h3 a:hover {
        text-decoration: underline;
    }
    .carousel-slide .slogan {
        font-style: italic;
        color: #555;
        margin-bottom: 10px;
        flex-grow: 1;
    }
    .carousel-slide .court-info {
        font-size: 0.9em;
        color: #666;
        margin-bottom: 15px;
    }
    .scroll-hint {
        text-align: center;
        margin-top: 10px;
        font-style: italic;
        color: #777;
    }
</style>

<div class="page-header">
    <h1>Nasze Ośrodki Tenisowe</h1>
</div>

% if not centers:
    <p>Przepraszamy, obecnie nie możemy wyświetlić informacji o naszych ośrodkach. Spróbuj ponownie później.</p>
% else:
    <div class="carousel-container">
        % for center in centers:
            <div class="carousel-slide">
                <div>
                    <img src="{{center['photo_url']}}" alt="Zdjęcie ośrodka {{center['name']}}">
                    <h3><a href="{{center['details_url']}}">{{center['name']}}</a></h3>
                    % if center['slogan']:
                        <p class="slogan">"{{center['slogan']}}"</p>
                    % else:
                        <p class="slogan"> </p>
                    % end
                    <p class="court-info"><strong>Korty:</strong> {{center['court_summary']}}</p>
                </div>
                <a href="{{center['details_url']}}" class="button">Zobacz szczegóły i zarezerwuj</a>
            </div>
        % end
    </div>
    % if len(centers) > 2:
        <p class="scroll-hint">Przesuń w bok, aby zobaczyć więcej ośrodków.</p>
    % end
% end