from app.schemas import MenuItem, Restaurant

RESTAURANTS: dict[str, Restaurant] = {
    "rest-1": Restaurant(
        id="rest-1",
        name="Dhaka Spice House",
        cuisine="Bengali",
        menu=[
            MenuItem(id="item-101", name="Kacchi Biryani", price=12.50),
            MenuItem(id="item-102", name="Beef Tehari", price=9.00),
            MenuItem(id="item-103", name="Borhani", price=2.50),
        ],
    ),
    "rest-2": Restaurant(
        id="rest-2",
        name="Napoli Woodfire",
        cuisine="Italian",
        menu=[
            MenuItem(id="item-201", name="Margherita Pizza", price=14.00),
            MenuItem(id="item-202", name="Truffle Pasta", price=16.50),
        ],
    ),
    "rest-3": Restaurant(
        id="rest-3",
        name="Tokyo Ramen Bar",
        cuisine="Japanese",
        menu=[
            MenuItem(id="item-301", name="Tonkotsu Ramen", price=13.75),
            MenuItem(id="item-302", name="Chicken Gyoza", price=6.50),
        ],
    ),
}