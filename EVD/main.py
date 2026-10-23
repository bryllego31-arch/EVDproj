"""Kape Cebu - PyScript logic.
Event-driven concepts used: click, input, change, submit events,
event delegation, form validation, and dynamic DOM updates."""
from pyscript import document, when

MENU = [
    {"id": 1, "name": "Cebu Barako Espresso", "cat": "Coffee", "price": 90, "emoji": "☕", "desc": "Bold local barako, double shot."},
    {"id": 2, "name": "Cafe Latte", "cat": "Coffee", "price": 120, "emoji": "🥛", "desc": "Espresso with steamed milk."},
    {"id": 3, "name": "Spanish Latte", "cat": "Coffee", "price": 140, "emoji": "🍯", "desc": "Sweet condensed-milk latte."},
    {"id": 4, "name": "Iced Americano", "cat": "Cold", "price": 100, "emoji": "🧊", "desc": "Chilled and refreshing."},
    {"id": 5, "name": "Mango Cold Brew", "cat": "Cold", "price": 150, "emoji": "🥭", "desc": "Cold brew with Cebu mango."},
    {"id": 6, "name": "Ube Pandesal", "cat": "Pastry", "price": 60, "emoji": "🍞", "desc": "Warm, soft, ube-filled."},
    {"id": 7, "name": "Butter Croissant", "cat": "Pastry", "price": 85, "emoji": "🥐", "desc": "Flaky and freshly baked."},
    {"id": 8, "name": "Dried Mango Cookie", "cat": "Pastry", "price": 70, "emoji": "🍪", "desc": "Chewy with a tropical twist."},
]
PROMOS = {"BREW10": 0.10, "CEBU20": 0.20}

cart = {}  # item id -> quantity
state = {"cat": "All", "promo": 0.0}


def money(n):
    return f"₱{n:,.2f}"


def el(selector):
    return document.querySelector(selector)


def render_menu():
    text = el("#search").value.strip().lower()
    html = ""
    for m in MENU:
        if state["cat"] != "All" and m["cat"] != state["cat"]:
            continue
        if text and text not in m["name"].lower():
            continue
        html += (
            f'<article class="card"><div class="emoji">{m["emoji"]}</div>'
            f'<h3>{m["name"]}</h3><p class="muted">{m["desc"]}</p>'
            f'<div class="row"><strong>{money(m["price"])}</strong>'
            f'<button data-action="add" data-id="{m["id"]}">Add</button></div></article>'
        )
    el("#menu-grid").innerHTML = html or "<p>No items match your search.</p>"


def render_cart():
    box = el("#cart-items")
    if not cart:
        box.innerHTML = '<p class="muted">Your cart is empty.</p>'
    else:
        html = ""
        for m in MENU:
            q = cart.get(m["id"])
            if q:
                html += (
                    f'<div class="cart-row"><span>{m["name"]} × {q}</span><span>'
                    f'<button data-action="minus" data-id="{m["id"]}">−</button>'
                    f'<button data-action="plus" data-id="{m["id"]}">+</button>'
                    f'<strong> {money(m["price"] * q)}</strong></span></div>'
                )
        box.innerHTML = html
    subtotal = sum(m["price"] * cart.get(m["id"], 0) for m in MENU)
    discount = subtotal * state["promo"]
    fee = float(el("#delivery").value) if cart else 0.0
    el("#subtotal").innerText = money(subtotal)
    el("#discount").innerText = "-" + money(discount)
    el("#fee").innerText = money(fee)
    el("#total").innerText = money(subtotal - discount + fee)


# ---- Events ----
@when("input", "#search")
def on_search(event):
    render_menu()


@when("click", "#categories")
def on_category(event):
    btn = event.target.closest("button")
    if not btn:
        return
    state["cat"] = btn.getAttribute("data-cat")
    for chip in document.querySelectorAll(".chip"):
        chip.classList.toggle("active", chip == btn)
    render_menu()


@when("click", "#menu-grid")
def on_add(event):
    btn = event.target.closest("button")
    if btn:
        i = int(btn.getAttribute("data-id"))
        cart[i] = cart.get(i, 0) + 1
        render_cart()


@when("click", "#cart-items")
def on_cart_change(event):
    btn = event.target.closest("button")
    if not btn:
        return
    i = int(btn.getAttribute("data-id"))
    cart[i] = cart.get(i, 0) + (1 if btn.getAttribute("data-action") == "plus" else -1)
    if cart[i] <= 0:
        del cart[i]
    render_cart()


@when("click", "#apply-promo")
def on_promo(event):
    code = el("#promo").value.strip().upper()
    msg = el("#promo-msg")
    if code in PROMOS:
        state["promo"] = PROMOS[code]
        msg.innerText = f"Code {code} applied: {int(PROMOS[code] * 100)}% off."
        msg.className = "ok"
    else:
        state["promo"] = 0.0
        msg.innerText = "Invalid promo code."
        msg.className = "err"
    render_cart()


@when("change", "#delivery")
def on_delivery(event):
    render_cart()


@when("submit", "#order-form")
def on_order(event):
    event.preventDefault()
    name = el("#name").value.strip()
    phone = el("#phone").value.strip()
    msg = el("#form-msg")
    if not cart:
        msg.innerText, msg.className = "Add at least one item to your cart.", "err"
    elif len(name) < 2:
        msg.innerText, msg.className = "Please enter your name.", "err"
    elif not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
        msg.innerText, msg.className = "Enter a valid 11-digit mobile number (09XXXXXXXXX).", "err"
    else:
        total = el("#total").innerText
        msg.innerText = f"Thank you, {name}! Order placed. Total: {total}."
        msg.className = "ok"
        cart.clear()
        state["promo"] = 0.0
        el("#promo").value = ""
        el("#promo-msg").innerText = ""
        el("#order-form").reset()
        render_cart()


@when("input", "#comment")
def on_comment_typing(event):
    el("#count").innerText = str(len(el("#comment").value))


@when("click", "#send-feedback")
def on_feedback(event):
    box = el("#comment")
    msg = el("#feedback-msg")
    if box.value.strip():
        msg.innerText, msg.className = "Salamat! Your feedback was sent.", "ok"
        box.value = ""
        el("#count").innerText = "0"
    else:
        msg.innerText, msg.className = "Please write something first.", "err"


render_menu()
render_cart()
