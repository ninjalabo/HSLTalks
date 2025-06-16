from fasthtml.common import *

# Chat message bubble component
# is_user=True for user (right), False for assistant (left)
def ChatMessage(*content, is_user: bool):
    """
    Render one or more content elements inside a chat bubble.
    """
    bubble_cls = "chat-bubble-primary" #if is_user else "chat-bubble-secondary"
    alignment = "chat-end" if is_user else "chat-start"
    # Wrap provided content inside the styled bubble
    children = []
    for c in content:
        if isinstance(c, str):
            children.append(Div(c, cls=f"chat-bubble {bubble_cls}"))
        else:
            children.append(c)
    return Div(cls=f"chat {alignment} p-2")(*children)


# Initialize FastHTML app with Tailwind & DaisyUI
hdrs = (
    picolink,
    Script(src="https://cdn.tailwindcss.com"),
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
)
app, rt = fast_app(hdrs=hdrs, live=True)

# Main route: left-half iframe, right-half chat
@rt("/")
def index():
    # Left panel: iframe fills its container
    left_panel = Div(
        Iframe(
            src="https://omatnaytot.hsl.fi/static?url=ace225d4-84a0-5829-bad1-aab0f9e051cb",
            cls="absolute inset-0 w-full h-full border-none"
        ),
        style="position:relative; width:50vw; height:100vh; overflow:hidden;"
    )

    # Right panel: chat UI
    # QR code bubble at the top
    qr_msg = ChatMessage(
        Iframe(
            src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://omatnaytot.hsl.fi",
            cls="w-48 h-48 border-none"
        ),
        "Scan me to talk",
        is_user=False
    )
    
    # Message history (scrollable, below QR)
    history = Div(
        qr_msg,
        id="chatlist",
        cls="overflow-auto p-4 space-y-2 flex-1"
    )

    # Input form at bottom
    form = Form(
        hx_post="/handle",
        hx_target="#chatlist",
        hx_swap="beforeend",
        cls="p-4 flex gap-2 border-t bg-base-100 dark:bg-base-800"
    )(
        Input(name="msg", id="msg-input", placeholder="Type a message...", cls="flex-1 input input-bordered"),
        Button("Send", cls="btn btn-primary")
    )

    # Auto-scroll script
    script = Script("""
    const chatList = document.getElementById('chatlist');
    document.body.addEventListener('htmx:afterSwap', event => {
        if (event.detail.target.id === 'chatlist') {
            chatList.scrollTop = chatList.scrollHeight;
        }
    });
    """)

    right_panel = Div(
        history,
        form,
        script,
        style="position:relative; width:50vw; height:100vh; display:flex; flex-direction:column;"
    )

    # Combine panels
    return Div(
        left_panel,
        right_panel,
        style="display:grid; grid-template-columns:50% 50%; width:100vw; height:100vh; margin:0; padding:0; gap:0;"
    )

def ImgMsg(img_path:str, msg:str):
    return ChatMessage(Img(src="/static/images/" + img_path, cls="w-48 h-48"), msg, is_user=False)

how_to_go = ChatMessage(
    Div(
        Label(Input(type='checkbox', checked=''), '🚌 Bus'),Br(),
        Label(Input(type='checkbox', checked=''), '🚊 Tram'),Br(),
        Label(Input(type='checkbox', checked=''), '🚆 Train'),Br(),
        Label(Input(type='checkbox', checked=''),'🚇 Metro'),Br(),
        Label(Input(type='checkbox', checked=''),'⛴ Ferry'),Br(),
        Label(Input(type='checkbox', checked=''),'🚲 Helsinki and Espoo'),Br()
    ), "How do you want to go?", is_user=False,
)

ranking = ChatMessage(
    Div(
        Table(
            Thead(
                Tr(
                    Th('Rank'),
                    Th('Nickname'),
                    Th('Location'),
                    Th('Monthly Saved CO₂ (g)'),
                    Th('Annual Saved CO₂ (g)'),
                    Th('2025 Saved CO₂ (g)'),
                    Th('2024 rank')
                )
            ),
            Tbody(
                Tr(
                    Td('1'),
                    Td('RenewableRanger'),
                    Td('Tampere'),
                    Td('1222'),
                    Td('14664'),
                    Td(),
                    Td(53)
                ),
                Tr(
                    Td('2'),
                    Td('PlanetSaver'),
                    Td('Turku'),
                    Td('1047'),
                    Td('12564'),
                    Td(),
                    Td(12982)
                ),
                Tr(
                    Td('3'),
                    Td(
                        Strong('Hiroshi')
                    ),
                    Td('Vantaa'),
                    Td('986'),
                    Td('11832'),
                    Td('23221'),
                    Td(9),
                    style='background-color: #fffae6;'
                ),
                Tr(
                    Td('4'),
                    Td('EcoWarrior'),
                    Td('Helsinki'),
                    Td('748'),
                    Td('8976'),
                    Td(),
                    Td(1)
                ),
                Tr(
                    Td('5'),
                    Td('GreenRider'),
                    Td('Espoo'),
                    Td('422'),
                    Td('5064'),
                    Td(),
                    Td(987678)
                )
            ),
            border='1',
            cellpadding='6',
            cellspacing='0'
        )        
    ), "", is_user=False,
)

slider_msg = ChatMessage(
    "Do you want to use more bike🚴‍♂️ mileage on this trip?🤔",   
    Input(
        type="range",
        min="0",
        max="100",
        value="50",
        oninput="document.getElementById('val').textContent=this.value+'%';"
    ),
    Span("5%", id="val"),
    is_user=False
)

Reply = [

        ImgMsg("present_location.png", "Where do you want to go?"),
        how_to_go,
        ChatMessage("Use Bike! It's Sunny☀️!", is_user=False),
        ImgMsg("route.png", "Here you are!"),
        ChatMessage("You've saved 5g CO2🌳", is_user=False),
        ImgMsg("plot.png", "Total 172g saved this month🌳"),
        ranking,
        ChatMessage("Keep it up😍 to get free HSL tickets!", is_user=False),
        slider_msg,        
        ChatMessage("kiltti poika🥷", is_user=False),
]

# Handle incoming messages: user and OK
@rt("/handle")
def handle(msg: str):
    return (
        ChatMessage(msg, is_user=True),
        Reply.pop(0)
    )

if __name__ == "__main__":
    serve()
