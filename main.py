from shiny import App, ui, reactive
from tango import TangoBoard 
import random, json

# Game instance ----------------------------------------------------------------

BOARD_SIZE = 6 # Default value
_game = TangoBoard(n=BOARD_SIZE)

# UI helpers

def render_board():
    rows = []
    for r in range(BOARD_SIZE):
        tds = [ui.html("td", {
                    "id": f"cell-{r}-{c}",
                    "class": "cell",
                    "style": "width:45px;height:45px;border:1px solid #555;text-align:center;cursor:pointer;"
                }, ui.HTML(_game.cell_symbol(r, c))) for c in range(BOARD_SIZE)]
        rows.append(ui.html("tr", tds))
    return ui.html("table", {"style": "border-collapse:collapse;margin:auto;"}, rows)

# -----------------------------------------------------------------------------
# Layout -----------------------------------------------------------------------
# -----------------------------------------------------------------------------

app_ui = ui.page_fluid(
    # Header div
    ui.div({"style": "text-align:center;margin-top:10px;"}, ui.h2("LinkedIn Tango (Shiny)")),

    # Game & controls div
    ui.div({"style": "text-align:center;margin-top:20px;"},
        render_board(),
        ui.br(),
        ui.input_action_button("new", "New Board", class_="btn btn-primary me-2"),
        ui.input_action_button("random", "Toggle Random", class_="btn btn-secondary me-2"),
        ui.input_download_button("save", "Save JSON", class_="btn btn-outline-success"),
    ),

    # Instructions div
    ui.div({"style": "max-width:700px;margin:30px auto;font-size:0.9rem;"},
        ui.h4("Instructions"),
        ui.p("Click a blank cell to cycle M → S → blank. Satisfy adjacency/row/column rules and respect '=' or '×' links."),
    ),

    # Disclaimer div
    ui.div({"style": "text-align:center;font-size:0.8rem;color:#666;margin:40px 0;"},
        "Unofficial fan adaptation; all LinkedIn Tango trademarks belong to their respective owners."),
)

# Server logic -----------------------------------------------------------------

def server(input, output, session):

    # ---------- create a fresh board ----------------------------------------
    @reactive.Effect
    @reactive.event(input.new)
    def _():
        global _game
        _game = TangoBoard(n=BOARD_SIZE)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                session.send_custom_message("update-cell", {
                    "id": f"cell-{r}-{c}",
                    "html": _game.cell_symbol(r, c)
                })

    # ---------- toggle a random editable cell -------------------------------
    @reactive.Effect
    @reactive.event(input.random)
    def _():
        editable = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                     if (r, c, 0) not in _game.known_cells and (r, c, 1) not in _game.known_cells]
        if editable:
            r, c = random.choice(editable)
            _game.toggle_cell(r, c)
            session.send_custom_message("update-cell", {
                "id": f"cell-{r}-{c}",
                "html": _game.cell_symbol(r, c)
            })

    # ---------- download -----------------------------------------------------
    @session.download(filename=lambda: "tango_board.json")
    def save():
        yield _game.to_json()
      
# Front‑end helper js 

custom_js = ui.tags.script("""
Shiny.addCustomMessageHandler('update-cell', function(msg){
  const el = document.getElementById(msg.id);
  if(el){ el.innerHTML = msg.html; }
});
""")

app = App(app_ui + [custom_js], server)
