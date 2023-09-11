import telebot
import uuid

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('6157430580:AAHim0idBu1WX_ne9LEi3sYIcWF5-zY3OM0')

# Define the available items in the shop
items = [
    {'name': 'Toothpaste', 'brand_tag': 'Colgate', 'price': 89, 'weight': 0.2, 'quantity_available': 100},
    {'name': 'Soap', 'brand_tag': 'Dove', 'price': 57, 'weight': 0.3, 'quantity_available': 200},
    {'name': 'Shampoo', 'brand_tag': 'Pantene', 'price': 199, 'weight': 0.5, 'quantity_available': 150},
    {'name': 'Toilet Paper', 'brand_tag': 'Charmin', 'price': 60, 'weight': 1.0, 'quantity_available': 50},
    {'name': 'Laundry Detergent', 'brand_tag': 'Tide', 'price': 179, 'weight': 2.5, 'quantity_available': 80},
    {'name': 'Batteries', 'brand_tag': 'Duracell', 'price': 54, 'weight': 0.2, 'quantity_available': 120},
    {'name': 'Trash Bags', 'brand_tag': 'Glad', 'price': 30, 'weight': 0.8, 'quantity_available': 90},
    {'name': 'Cereal', 'brand_tag': 'Kellogg\'s', 'price': 199, 'weight': 0.6, 'quantity_available': 180},
    {'name': 'Peanut Butter', 'brand_tag': 'Skippy', 'price': 399, 'weight': 0.4, 'quantity_available': 100},
    {'name': 'Aluminum Foil', 'brand_tag': 'Reynolds', 'price': 200, 'weight': 0.3, 'quantity_available': 150}
]


# Store the user's cart
carts = {}

# Store the customer details
customers = {}


import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('customer_data.db')
cursor = conn.cursor()

# Create a table to store customer data
cursor.execute('''CREATE TABLE IF NOT EXISTS customers
                  (chat_id INTEGER PRIMARY KEY, unique_id TEXT)''')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    # Check if the customer is new or existing
    if chat_id in customers:
        bot.send_message(chat_id, 'Welcome back! Please enter your unique ID:')
        bot.register_next_step_handler(message, process_existing_customer)
    else:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        new_customer_button = telebot.types.KeyboardButton('New Customer')
        returning_customer_button = telebot.types.KeyboardButton('Returning Customer')
        markup.add(new_customer_button, returning_customer_button)
        bot.send_message(chat_id, 'Are you a new customer or a returning customer?', reply_markup=markup)
        bot.register_next_step_handler(message, process_new_customer)


def process_new_customer(message):
    chat_id = message.chat.id
    text = message.text.strip().lower()

    if text == 'new customer':
        # Generate a new unique ID
        unique_id = str(uuid.uuid4())
        customers[chat_id] = {'unique_id': unique_id}
        bot.send_message(chat_id, f'Welcome to our shop! Your unique ID is: {unique_id}. '
                                  'Enjoy your shopping experience.')
        for index, item in enumerate(items, start=1):
            item_info = f"{index}. {item['name']} - Brand: {item['brand_tag']} - Price: ₹{item['price']:.2f} - Weight: {item['weight']} kg - Quantity Available: {item['quantity_available']}"
            bot.send_message(chat_id, item_info)

    elif text == 'returning customer':
        bot.send_message(chat_id, 'Please enter your unique ID:')
        bot.register_next_step_handler(message, process_existing_customer)
    else:
        bot.send_message(chat_id, 'Invalid input. Please select either "New Customer" or "Returning Customer".')


def process_existing_customer(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id in customers and customers[chat_id]['unique_id'] == text:
        bot.send_message(chat_id, f'Welcome back! Enjoy your shopping now.')
        bot.send_message(chat_id, 'Here are the available items:')

        for index, item in enumerate(items, start=1):
            item_info = f"{index}. {item['name']} - Brand: {item['brand_tag']} - Price: ₹{item['price']:.2f} - Weight: {item['weight']} kg - Quantity Available: {item['quantity_available']}"
            bot.send_message(chat_id, item_info)
    else:
        # Generate a new unique ID
        unique_id = str(uuid.uuid4())
        customers[chat_id] = {'unique_id': unique_id}
        bot.send_message(chat_id, f'Your unique ID doesn\'t exist. '
                                  f'Your new unique ID is: {unique_id}. '
                                  'Welcome to our shop, enjoy your shopping experience.')
        bot.send_message(chat_id, 'Here are the available items:')
        for index, item in enumerate(items, start=1):
            item_info = f"{index}. {item['name']} - Brand: {item['brand_tag']} - Price: ₹{item['price']:.2f} - Weight: {item['weight']} kg - Quantity Available: {item['quantity_available']}"
            bot.send_message(chat_id, item_info)

    # Clear the cart when starting a new conversation
    if chat_id in carts:
        carts[chat_id] = {}


# Handle the '/items' command to display the available items
@bot.message_handler(commands=['items'])
def handle_items(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Here are the available items:')

    for index, item in enumerate(items, start=1):
            item_info = f"{index}. {item['name']} - Brand: {item['brand_tag']} - Price: ₹{item['price']:.2f} - Weight: {item['weight']} kg - Quantity Available: {item['quantity_available']}"
            bot.send_message(chat_id, item_info)


@bot.message_handler(commands=['add'])
def handle_add(message):
    chat_id = message.chat.id

    if chat_id in customers:
        customer = customers[chat_id].setdefault('cart', {})
        command_params = message.text.split()[1:]

        if len(command_params) != 2:
            bot.send_message(chat_id, 'Invalid command. Please use the format: /add item_number quantity')
            return

        item_number, quantity = command_params

        try:
            item_number = int(item_number)
            quantity = int(quantity)
            if item_number <= 0 or item_number > len(items) or quantity <= 0:
                raise ValueError
        except ValueError:
            bot.send_message(chat_id, 'Invalid input. Please enter a valid item number and quantity.')
            return

        item = items[item_number - 1]

        # Check if the requested quantity is available
        if quantity > item['quantity_available']:
            bot.send_message(chat_id, f"Sorry, only {item['quantity_available']} {item['name']}(s) available.")
            return

        total_price = item['price'] * quantity

        if item_number in customer:
            customer[item_number] += quantity
        else:
            customer[item_number] = quantity

        # Subtract the quantity from items array
        item['quantity_available'] -= quantity

        bot.send_message(chat_id, f'{quantity} {item["name"]}(s) added to your cart. Total price: ₹{total_price:.2f}')
    else:
        bot.send_message(chat_id, '/start')




@bot.message_handler(commands=['remove'])
def handle_remove(message):
    chat_id = message.chat.id

    if chat_id in customers:
        customer = customers[chat_id].get('cart')
        if not customer:
            bot.send_message(chat_id, 'Your cart is empty.')
            return

        command_params = message.text.split()[1:]

        if len(command_params) != 2:
            bot.send_message(chat_id, 'Invalid command. Please use the format: /remove item_number quantity')
            return

        item_number, quantity = command_params

        try:
            item_number = int(item_number)
            quantity = int(quantity)
            if item_number <= 0 or item_number > len(items) or quantity <= 0:
                raise ValueError
        except ValueError:
            bot.send_message(chat_id, 'Invalid input. Please enter a valid item number and quantity.')
            return

        if item_number not in customer:
            bot.send_message(chat_id, 'The specified item is not in your cart.')
            return

        current_quantity = customer[item_number]
        if quantity >= current_quantity:
            del customer[item_number]
            bot.send_message(chat_id, f'All {items[item_number - 1]["name"]}(s) have been removed from your cart.')
        else:
            customer[item_number] -= quantity
            bot.send_message(chat_id, f'{quantity} {items[item_number - 1]["name"]}(s) have been removed from your cart.')
    else:
        bot.send_message(chat_id, '/start')


    
# Handle the '/cancel' command to cancel the order and clear the cart
@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    chat_id = message.chat.id

    if chat_id in customers:
        customer = customers[chat_id]
        cart = customer['cart']
        if not cart:
            bot.send_message(chat_id, 'Your cart is already empty.')
        else:
            # Clear the user's cart
            customer['cart'] = {}
            bot.send_message(chat_id, 'Your order has been canceled. Your cart is now empty.')
    else:
        bot.send_message(chat_id, 'Please enter your unique ID first.')




# Handle the '/cart' command to display the user's cart
@bot.message_handler(commands=['cart'])
def handle_cart(message):
    chat_id = message.chat.id

    if chat_id in customers:
        customer = customers[chat_id]
        cart = customer['cart']
        if not cart:
            bot.send_message(chat_id, 'Your cart is empty.')
        else:
            bot.send_message(chat_id, 'Your cart:')

            total_price = 0
            for item_number, quantity in cart.items():
                item = items[item_number - 1]
                item_info = f"{item['name']} - Brand: {item['brand_tag']} - Quantity: {quantity}"
                bot.send_message(chat_id, item_info)
                total_price += item['price'] * quantity

            bot.send_message(chat_id, f'Total price: ₹{total_price:.2f}')
    else:
        bot.send_message(chat_id, 'Please enter your unique ID first.')


def handle_payment(message, order_details):
    chat_id = message.chat.id
    response = message.text.lower()

    if response == 'yes':
        # Process payment here
        # ...
        # Send payment confirmation
        bot.send_message(chat_id, 'Payment successful. Thank you for shopping with us!')
    elif response == 'no':
        # Continue with shopping
        bot.send_message(chat_id, 'You can continue with your shopping.')
    else:
        # Invalid response
        bot.send_message(chat_id, 'Invalid response. Please try again.')

    # Clear the cart after checkout
    customers[chat_id]['cart'] = {}


# Handle the checkout command
@bot.message_handler(commands=['checkout'])
def handle_checkout(message):
    chat_id = message.chat.id

    if chat_id not in customers or not customers[chat_id]['cart']:
        bot.send_message(chat_id, 'Your cart is empty.')
        return

    total_price = 0
    items_ordered = []
    for item_number, quantity in customers[chat_id]['cart'].items():
        item = items[item_number - 1]
        item_price = item['price'] * quantity
        total_price += item_price
        item_info = f"{item['name']} - Brand: {item['brand_tag']} - Quantity: {quantity} - Price: ₹{item_price:.2f}"
        items_ordered.append(item_info)

    order_details = "Order summary:\n" + "\n".join(items_ordered)
    order_details += f"\nTotal price: ₹{total_price:.2f}"
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    delivery_button = telebot.types.KeyboardButton('Delivery')
    pickup_button = telebot.types.KeyboardButton('Pickup')
    markup.add(delivery_button, pickup_button)
    bot.send_message(chat_id, 'Please select your preference:', reply_markup=markup)
    # Wait for the customer's preference response
    bot.register_next_step_handler(message, lambda m: handle_delivery_preference(m, order_details,total_price))

def loyalty_points(chat_id, total_price):
    if total_price > 1000:
        loyalty_points = total_price / 100
        if chat_id in customers:
            customers[chat_id].setdefault('loyalty_points', 0)
            customers[chat_id]['loyalty_points'] += loyalty_points
            current_points = customers[chat_id]['loyalty_points']
            bot.send_message(chat_id, f"Loyalty points added: {loyalty_points}")
            bot.send_message(chat_id, f"Total loyalty points: {current_points}")


# Handle the payment preference
def handle_payment_preference(message, order_details,total_price):
    chat_id = message.chat.id
    response = message.text.lower()

    if response == 'yes':
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        hard_copy_button = telebot.types.KeyboardButton('Hard Copy')
        soft_copy_button = telebot.types.KeyboardButton('Soft Copy')
        markup.add(hard_copy_button, soft_copy_button)
        bot.send_message(chat_id, 'Please select your billing preference:(soft copy is more environment friendly:) )', reply_markup=markup)

        # Wait for the customer's billing preference response
        bot.register_next_step_handler(message, lambda m: handle_billing_preference(m, order_details,total_price))
    elif response == 'no':
        # Continue with shopping
        bot.send_message(chat_id, 'You can continue with your shopping.')
    else:
        # Invalid response
        bot.send_message(chat_id, 'Invalid response. Please try again.')

# Handle the delivery preference
def handle_delivery_preference(message, order_details,total_price):
    chat_id = message.chat.id
    response = message.text.lower()

    if response == 'delivery':
        bot.send_message(chat_id, 'Please enter your delivery address:')
        bot.register_next_step_handler(message, lambda m: handle_delivery_address(m, order_details,total_price))
    elif response == 'pickup':
        # Proceed to payment for pickup option
        # Ask the customer if they want to proceed to payment
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        yes_button = telebot.types.KeyboardButton('Yes')
        no_button = telebot.types.KeyboardButton('No')
        markup.add(yes_button, no_button)
        bot.send_message(chat_id, 'Would you like to proceed to payment?', reply_markup=markup)

        # Wait for the customer's response
        bot.register_next_step_handler(message, lambda m: handle_payment_preference(m, order_details,total_price))
    else:
        bot.send_message(chat_id, 'Invalid response. Please try again.')


# Handle the delivery address
def handle_delivery_address(message, order_details,total_price):
    chat_id = message.chat.id
    address = message.text

    if len(address) <= 15:
        delivery_fee = 0
        bot.send_message(chat_id, 'Your address is within city limits. Delivery fee: ₹0')
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        yes_button = telebot.types.KeyboardButton('Yes')
        no_button = telebot.types.KeyboardButton('No')
        markup.add(yes_button, no_button)
        bot.send_message(chat_id, 'Would you like to proceed to payment?', reply_markup=markup)
        # Wait for the customer's response
        bot.register_next_step_handler(message, lambda m: handle_payment_preference(m, order_details,total_price))
    else:
        delivery_fee = (len(address) - 15) * 10
        bot.send_message(chat_id, f'Your address is outside city limits. Delivery fee: ₹{delivery_fee}')
        # Ask the customer if they want to proceed to payment
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        yes_button = telebot.types.KeyboardButton('Yes')
        no_button = telebot.types.KeyboardButton('No')
        markup.add(yes_button, no_button)
        bot.send_message(chat_id, 'Would you like to proceed to payment?', reply_markup=markup)

        # Wait for the customer's response
        bot.register_next_step_handler(message, lambda m: handle_payment_preference(m, order_details,total_price+delivery_fee))

       
# Handle the billing preference
def handle_billing_preference(message, order_details,total_price):
    chat_id = message.chat.id
    response = message.text.lower()

    if response == 'hard copy':
        generate_hard_copy_bill(chat_id)
    elif response == 'soft copy':
        generate_soft_copy_bill(chat_id)
    else:
        bot.send_message(chat_id, 'Invalid response. Please try again.')
    loyalty_points(chat_id,total_price)
    bot.send_message(chat_id, 'Thank you for shopping with us today')

    
    customers[chat_id]['cart'] = {}


def generate_hard_copy_bill(chat_id):
    # Logic to generate hard copy bill
    bot.send_message(chat_id, 'Hard copy bill will be kept along with the other items')


def generate_soft_copy_bill(chat_id):
    # Logic to generate soft copy bill
    bot.send_message(chat_id, 'Soft copy bill generated.')

@bot.message_handler(commands=['hot_deals'])
def handle_hot_deals(message):
    chat_id = message.chat.id

    sorted_items = sorted(items, key=lambda x: x['price'] / x['weight'])
    hot_deals = sorted_items[:3]

    for index, item in enumerate(hot_deals, start=1):
        item_info = f"{index}. {item['name']} - Brand: {item['brand_tag']} - Price: ${item['price']:.2f} - Weight: {item['weight']} kg"
        bot.send_message(chat_id, item_info)


@bot.message_handler(commands=['contact_shop'])
def contact_shop(message):
    chat_id = message.chat.id
    contact_message = "If you are facing any technical or non-technical difficulties, feel free to contact us at +91 9xxxx92729"
    bot.send_message(chat_id, contact_message)

# Command handler for /help
@bot.message_handler(commands=['help'])
def show_help(message):
    commands = [
        '/start - Start a new session',
        '/add item_number quantity - Add items to the cart',
        '/remove item_number quantity - Remove items from the cart',
        '/cart - View the items in your cart',
        '/checkout - Proceed to checkout',
        '/delivery - Select delivery preference',
        '/contact_shop - Contact the shop',
        '/cancel - To cancel the current order and remove everything from cart',
        '/hot_deals - To show the best deals of the day',
        '/help - Show available commands and loyalty points rules'
    ]
    loyalty_points_rules = "Loyalty Points Rules:\n"
    loyalty_points_rules += "If your total price exceeds ₹1000, you will earn loyalty points.\n"
    loyalty_points_rules += "The number of loyalty points earned is equal to the total price divided by 100.\n"
    loyalty_points_rules += "Loyalty points can be redeemed for discounts on future purchases.\n"

    bot.send_message(message.chat.id, "Available commands:\n" + "\n".join(commands))
    bot.send_message(message.chat.id, loyalty_points_rules)



# Handle unknown commands
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Invalid command. Please use /help for more info')

bot.delete_webhook()

# Start the bot
bot.polling()
