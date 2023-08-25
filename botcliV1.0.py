import telebot
from telebot import types
import psycopg2
import os
import pyzbar.pyzbar as pyzbar
from PIL import Image
import io
import random
import requests
from telebot.apihelper import ApiException
import datetime
from telegram import ReplyKeyboardRemove
import threading
import time 
# Token d'API de ton bot
TOKEN = '6082635856:AAHSf33r9e9r3bZIEiiRCJ_ZseqTlfQjzMg'
VOTRE_CINETPAY_API_KEY = '63102016562bb6111a2b101.28388740'

# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    host="127.0.0.1",
    port="5432",
    database="best_seller",
    user="postgres",
    password="1234"
)

# Crée l'instance du bot
bot = telebot.TeleBot(TOKEN)

# Dictionnaire pour stocker le panier de chaque utilisateur
user_carts = {}


# Gère la commande /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Crée les boutons pour les fonctionnalités
    markup = types.ReplyKeyboardMarkup(row_width=2)
    
    btn_acheter = types.KeyboardButton("Acheter 🛍️")
    btn_scanner_qr = types.KeyboardButton("Scanner QR code 📷")
    btn_panier = types.KeyboardButton("🛒 Voir Panier")
    #btn_livraisons = types.KeyboardButton("Voir Livraisons 🚚")
    btn_contact = types.KeyboardButton("Contactez-nous ☎️")
    btn_quitter = types.KeyboardButton("Quitter ❌")
    btn_enregistrer = types.KeyboardButton("Enregistrer les informations 💾")
    
    markup.add(btn_acheter, btn_scanner_qr, btn_panier,  btn_contact, btn_quitter, btn_enregistrer)
    
    # Envoie le message de bienvenue avec les boutons
    bot.reply_to(message, "Bienvenue sur notre bot de commerce électronique ! Que voulez-vous faire aujourd'hui ?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.startswith("Quitter"))
def handle_quitter(message):
    user_id = message.from_user.id

    # Supprime le panier de l'utilisateur
    clear_cart(user_id)

    # Masque le menu des catégories
    markup = types.ReplyKeyboardRemove()

    # Affiche le message d'au revoir
    bot.reply_to(message, "Au revoir ! Pour commencer, appuyez sur /start.", reply_markup=markup)

# Gère l'action du bouton "/enregistrer_informations"

def handle_enregistrer_informations(message):
    client_id = message.chat.id  # ID du client (ID du chat)
    bot.reply_to(message, "Veuillez saisir votre nom :")
    bot.register_next_step_handler(message, process_name, client_id)


# Variables globales pour stocker les informations du client
temp_name = None
temp_prenom = None
temp_adresse = None
temp_client_id = None
temp_email = None

# Fonction de traitement du nom
def process_name(message, client_id):
    global temp_name
    temp_name = message.text
    bot.reply_to(message, "Veuillez saisir votre prénom :")
    bot.register_next_step_handler(message, process_prenom)


# Fonction de traitement du prénom
def process_prenom(message):
    global temp_prenom
    temp_prenom = message.text
    bot.reply_to(message, "Veuillez saisir votre adresse :")
    bot.register_next_step_handler(message, process_adresse)

# Fonction de traitement de l'adresse
def process_adresse(message):
    global temp_adresse
    temp_adresse = message.text
    bot.reply_to(message, "Veuillez saisir votre email :")
    bot.register_next_step_handler(message, process_email)

def process_email(message):
    global temp_email
    temp_email = message.text
    bot.reply_to(message, "Veuillez saisir votre téléphone :")
    bot.register_next_step_handler(message, process_telephone)

# Fonction de traitement du téléphone
def process_telephone(message):
    global temp_client_id
    telephone = message.text
    # Assurez-vous que client_id est un entier
    client_id = message.chat.id
    try:
        cursor = conn.cursor()

        # Vérifier si l'utilisateur existe déjà
        check_query = "SELECT * FROM clients WHERE client_id = %s"
        cursor.execute(check_query, (client_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Utiliser la requête UPDATE pour mettre à jour les informations
            update_query = "UPDATE clients SET nom = %s, prenom = %s, adresse = %s, telephone = %s, email = %s WHERE client_id = %s"
            update_values = (temp_name, temp_prenom, temp_adresse, telephone, temp_email, client_id)
            cursor.execute(update_query, update_values)
        else:
            # Utiliser la requête INSERT INTO pour insérer de nouvelles informations
            insert_query = "INSERT INTO clients (client_id, nom, prenom, adresse, telephone, email) VALUES (%s, %s, %s, %s, %s, %s)"
            insert_values = (client_id, temp_name, temp_prenom, temp_adresse, telephone, temp_email)
            cursor.execute(insert_query, insert_values)

        conn.commit()
        cursor.close()
        bot.reply_to(message, "Informations enregistrées avec succès !")
    except (Exception, psycopg2.Error) as error:
        bot.reply_to(message, "Une erreur s'est produite lors de l'enregistrement des informations.")



# Gère les messages textuels
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text.startswith('/add'):
        product_name = message
        user_id = message.from_user.id
        if product_name:
            add_product_to_cart(user_id, product_name)
            bot.reply_to(message, f"Produit {product_name} ajouté au panier avec succès.")
        else:
            bot.reply_to(message, "Veuillez spécifier le nom du produit à ajouter au panier.")
    elif message.text == "🛒 Voir Panier":
        handle_voir_panier(message)
    elif message.text.startswith("Acheter"):
        handle_acheter(message)
    elif message.text in get_categories():
        category = message.text
        # Récupère les produits de la catégorie sélectionnée depuis la base de données
        products = get_products_by_category(category)
        markup = None
        # Traite les données des produits comme tu le souhaites
        sent_products = []  # Liste pour stocker les produits déjà envoyés

        for product in products:
            product_name = product[0]
            response = f"Nom : {product_name}\nDescription : {product[1]}\nPrix : {product[2]} FCFA\n"
            images = get_product_images(product_name)

            if images:
                media_group = []
                for image_path in images:
                    with open(image_path, 'rb') as photo:
                        file_data = photo.read()
                        media = types.InputMediaPhoto(media=file_data)
                        media_group.append(media)

                # Envoyer le carrousel d'images
                bot.send_media_group(message.chat.id, media_group)

            # Envoyer le message du produit uniquement s'il n'a pas été déjà envoyé
            if product_name not in sent_products:
                if images:
                    # Ajouter le bouton "Ajouter au panier"
                    btn_add_to_cart = types.InlineKeyboardButton("Ajouter au panier", callback_data=f"add_to_cart {product_name}")
                    markup = types.InlineKeyboardMarkup().add(btn_add_to_cart)
                    bot.send_message(message.chat.id, text=response, reply_markup=markup)
                else:
                    # Envoyer le message sans les images mais avec le bouton "Ajouter au panier"
                    btn_add_to_cart = types.InlineKeyboardButton("Ajouter au panier", callback_data=f"add_to_cart {product_name}")
                    markup = types.InlineKeyboardMarkup().add(btn_add_to_cart)
                    bot.send_message(message.chat.id, text=response, reply_markup=markup)

            sent_products.append(product_name)  # Ajouter le produit à la liste des produits envoyés
    elif message.text.startswith("Scanner QR code"):
        handle_scanner_qrcode(message)
    elif message.text.startswith("Contactez-nous"):
        handle_contactez_nous(message)
    elif message.text.startswith("Enregistrer les informations"):
        handle_enregistrer_informations(message)
    else:
        # Répondre en cas de message non reconnu
        bot.reply_to(message, 'Je ne comprends pas votre demande.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart'))
def handle_add_to_cart(call):
    user_id = call.from_user.id
    callback_data = call.data.split()
    product_name = " ".join(callback_data[1:])
    add_product_to_cart(user_id, product_name)
    bot.answer_callback_query(call.id, f"Produit {product_name} ajouté au panier.")




@bot.callback_query_handler(func=lambda call: call.data == 'confirm_payment')
def handle_confirm_payment(call):
    # Message simplifié sur le processus de paiement sécurisé
    payment_message = (
        "Merci pour votre paiement! En cliquant sur le bouton ci-dessous, vous serez redirigé "
        "vers une page web sécurisée pour finaliser votre paiement en toute sécurité.\n\n"
        "Appuyez sur 'Confirmer le paiement' pour continuer."
    )

    # Création du bouton
    btn_mobile = types.InlineKeyboardButton("Confirmer le paiement", callback_data="payment_mobile")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(btn_mobile)

    # Envoie du message avec le bouton
    bot.send_message(call.from_user.id, payment_message, reply_markup=markup)






def calculate_total_amount(user_id):
    cart_content = get_cart_content(user_id)
    total_amount = 0

    for product_name, quantity in cart_content.items():
        price = get_product_price(product_name)
        if price is not None:
            total_amount += price * quantity

    return total_amount

def get_client_info(client_id):
    try:  
        cursor = conn.cursor()
        query = "SELECT nom, prenom, email FROM clients WHERE client_id = %s"
        cursor.execute(query, (client_id,))
        client_info = cursor.fetchone()
        
        if client_info:
            return {
                "nom": client_info[0],
                "prenom": client_info[1],
                "email": client_info[2]
            }
        else:
            return None
    except (psycopg2.Error, Exception) as error:
        print("Erreur lors de la récupération des informations du client :", error)
        return None
    finally:
        if conn:
            conn.close()


def generate_cinetpay_payment_link(montant_depot, transaction_id, client_id):
    # Récupère les informations du client depuis la base de données en utilisant le client_id
    client_info = get_client_info(client_id)  # À implémenter selon ta structure de base de données
    
    if client_info is None:
        print("Impossible de récupérer les informations du client depuis la base de données.")
        return None
    
    numero_destinataire = "656958696"  # Numéro de téléphone de destination
    api_url = "https://api-checkout.cinetpay.com/v2/payment"
    amount = int(montant_depot)
    
    # Utilise les informations du client pour remplir les paramètres de la requête
    query_params = {
        "amount": amount,
        "currency": "XAF",
        "description": "Paiement de facture",
        "customer_name": client_info["nom"],  # Remplace avec le nom du client depuis la base de données
        "customer_surname": client_info["prenom"],  # Remplace avec le prénom du client depuis la base de données
        "customer_phone_number": numero_destinataire,
        "customer_email": client_info["email"],  # Remplace avec l'adresse email du client depuis la base de données
        "return_url": "https://t.me/BEST_SELLER_UPbot",
        "notify_url": "https://t.me/BEST_SELLER_UPbot",
        "site_id": "607207",  # Remplace par l'identifiant de votre site CinetPay
        "transaction_id": transaction_id  # Remplace par un identifiant unique pour chaque transaction
    }
    
    # Ajoute la clé API aux paramètres de l'URL
    query_params["apikey"] = VOTRE_CINETPAY_API_KEY
    
    response = requests.post(api_url, params=query_params)
    
    if response.status_code == 200:  # Utilisez le code 201 pour indiquer "CREATED"
        data = response.json()
        if "data" in data and "payment_url" in data["data"]:
            return data["data"]["payment_url"]  # Retourne le lien de paiement
    else:
        print("Erreur lors de la génération du lien de paiement :", response.text, response.status_code)
        return None



def save_invoice(facture_id, client_id, date_facture, montant, lieu_livraison, livre):
    try:
        # Création d'un curseur pour exécuter les requêtes SQL
        cursor = conn.cursor()
        site_id = 607207
        # Vérifier l'état de la transaction avec CinetPay
        result = verify_cinetpay_transaction(facture_id, site_id, VOTRE_CINETPAY_API_KEY)

        if result is not None and result["status"] == "ACCEPTED":
            # La transaction est réussie, enregistrer la facture dans la base de données
            insert_query = """
                INSERT INTO factures (facture_id, client_id, date_facture, montant, lieu_livraison, livre)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            data = (facture_id, client_id, date_facture, montant, lieu_livraison, livre)

            cursor.execute(insert_query, data)
            conn.commit()
            print("La facture a été enregistrée avec succès dans la base de données.")
        else:
            # La transaction n'est pas réussie, demander à l'utilisateur de vérifier le paiement
            print("La transaction n'a pas été réussie. Veuillez vérifier votre paiement.")

    except (psycopg2.Error, Exception) as error:
        # Gérer les erreurs liées à la base de données
        print("Erreur lors de l'enregistrement de la facture :", error)

    finally:
        # Fermer le curseur et la connexion à la base de données, même en cas d'exception
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


# Dictionnaire pour stocker les informations de paiement en cours
payment_info = {}

# Dictionnaire pour stocker les comptes à rebours
countdown_timers = {}

def start_countdown(user_id):
    remaining_time = 120
    while remaining_time >= 0:
        if payment_info[user_id]["verified"]:
            return
        if remaining_time % 60 == 0:
            bot.send_message(user_id, f"Temps restant : {remaining_time // 60} minutes")
        time.sleep(1)
        remaining_time -= 1
    bot.send_message(user_id, "Transaction annulée : Veuillez vérifier votre paiement ou réessayer.")
    payment_info.pop(user_id, None)
    countdown_timers.pop(user_id, None)

def verify_payment_periodically(user_id):
    site_id = 607207
    time.sleep(60)  # Attendre 1 minute avant la première vérification
    while not payment_info[user_id]["verified"]:
        if verify_cinetpay_transaction(payment_info[user_id]["id_recu"], site_id, VOTRE_CINETPAY_API_KEY, payment_info[user_id]["amount"]):
            payment_info[user_id]["verified"] = True
            # Enregistrer la facture dans la base de données si la transaction est réussie
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
            delivery_address = get_user_address(user_id)
            bools = False
            save_invoice(payment_info[user_id]["id_recu"], user_id, current_datetime, payment_info[user_id]["amount"], delivery_address, bools)
            bot.send_message(user_id, "Transaction réussie : La facture a été enregistrée.")
        else:
            bot.send_message(user_id, "Veuillez vérifier votre paiement.")
            time.sleep(60)  # Attendre 1 minute avant la prochaine vérification


    
@bot.callback_query_handler(func=lambda call: call.data == 'start_countdown')
def start_countdown_callback(call):
    user_id = call.from_user.id
    
    if user_id not in countdown_timers and user_id in payment_info and not payment_info[user_id]["verified"]:
        # Démarrer le compte à rebours de 2 minutes et la vérification périodique dans des threads distincts
        countdown_thread = threading.Thread(target=start_countdown, args=(user_id,))
        countdown_thread.start()
        countdown_timers[user_id] = countdown_thread

        verification_thread = threading.Thread(target=verify_payment_periodically, args=(user_id,))
        verification_thread.start()
        
        # Créer un bouton annuler
        cancel_button = types.InlineKeyboardButton("Annuler", callback_data="cancel")
        cancel_keyboard = types.InlineKeyboardMarkup()
        cancel_keyboard.row(cancel_button)
        bot.send_message(user_id, "Le compte à rebours a commencé. Cliquez sur le bouton 'Annuler' pour arrêter la transaction.", reply_markup=cancel_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_transaction_callback(call):
    user_id = call.from_user.id
    if payment_info.get(user_id):
        payment_info.pop(user_id, None)
        if user_id in countdown_timers:
            countdown_timers[user_id].join()  # Attendre que le compte à rebours se termine
            countdown_timers.pop(user_id, None)
        bot.send_message(user_id, "Transaction annulée : Vous avez annulé la transaction en cours.")

def start_countdown(user_id):
    # Démarrez le compte à rebours de 2 minutes
    countdown_duration = 120  # 2 minutes en secondes
    end_time = time.time() + countdown_duration
    
    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        bot.send_message(user_id, f"Temps restant : {remaining_time} secondes")
        time.sleep(10)  # Attendez 10 secondes avant de mettre à jour le message

    bot.send_message(user_id, "Le compte à rebours est terminé.")


@bot.callback_query_handler(func=lambda call: call.data == 'payment_mobile')
def process_mobile_payment(call):
    user_id = call.from_user.id

    amount = calculate_total_amount(user_id)
    amount = amount + 1000
    id_recu = random.randint(100000, 999999)

    payment_info[user_id] = {
        "amount": amount,
        "id_recu": id_recu,
        "payment_url": generate_cinetpay_payment_link(amount, id_recu, user_id),
        "verified": False
    }

    bot.send_message(user_id, f"Vous allez payer {amount} pour le reçu {id_recu}.")

    payment_button = types.InlineKeyboardButton("Cliquez ici pour effectuer le paiement", url=payment_info[user_id]["payment_url"])
    payment_keyboard = types.InlineKeyboardMarkup()
    payment_keyboard.row(payment_button)

    message = bot.send_message(user_id, "Veuillez cliquer sur le lien suivant pour effectuer le paiement :", reply_markup=payment_keyboard)
    
    countdown_thread = threading.Thread(target=start_countdown, args=(user_id,))
    countdown_thread.start()
    countdown_timers[user_id] = countdown_thread
    
    # Store the transaction ID in the payment_info dictionary
    payment_info[user_id]["transaction_id"] = id_recu  # Replace this with your actual logic to get the transaction ID
    
    verification_thread = threading.Thread(target=verify_payment_periodically, args=(user_id,))
    verification_thread.start()
    
    # Send the payment link as a message
    bot.send_message(user_id, f"Voici le lien de paiement : {payment_info[user_id]['payment_url']}")

# ...


@bot.message_handler(func=lambda message: message.text == "Annuler")
def cancel_transaction(message):
    user_id = message.from_user.id
    if payment_info.get(user_id):
        payment_info.pop(user_id, None)
        if user_id in countdown_timers:
            countdown_timers[user_id].join()  # Attendre que le compte à rebours se termine
            countdown_timers.pop(user_id, None)
        bot.send_message(user_id, "Transaction annulée : Vous avez annulé la transaction en cours.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay'))
def handle_payment(call):
    # Récupère le mode de paiement sélectionné
    #payment_method = call.data.split('_')[1]

    # Affiche un message avec le mode de paiement sélectionné
    #bot.send_message(call.from_user.id, f"Vous avez sélectionné le mode de paiement : {payment_method}")

    # Crée les boutons pour les options de récupération
    btn_delivery = types.InlineKeyboardButton("Se faire livrer", callback_data="delivery")
    btn_pickup = types.InlineKeyboardButton("Récupérer", callback_data="pickup")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(btn_delivery, btn_pickup)

    # Envoie le message avec les options de récupération
    bot.send_message(call.from_user.id, "Comment souhaitez-vous récupérer votre produit :", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'delivery')
def handle_delivery(call):
    user_id = call.from_user.id
    address = get_user_address(user_id)

    if address:
        # Si le client a déjà une adresse enregistrée, demande de confirmation
        confirm_delivery_address(call.from_user.id, address)
    else:
        # Si le client n'a pas d'adresse enregistrée, demande d'entrer une adresse
        bot.send_message(call.from_user.id, "Veuillez entrer votre adresse de livraison :")
        bot.register_next_step_handler(call.message, process_delivery_address)

@bot.callback_query_handler(func=lambda call: call.data == 'pickup')
def handle_pickup(call):
    user_id = call.from_user.id
    pickup_address = get_user_address(user_id)

    if pickup_address:
        # Si l'adresse de récupération existe, demande de confirmation
        confirm_pickup_address(user_id, pickup_address)
    else:
        # Si l'adresse de récupération n'est pas disponible, envoie un message d'erreur
        bot.send_message(user_id, "L'adresse de récupération n'est pas disponible pour le moment.")
        bot.register_next_step_handler(call.message, process_delivery_address)
        # Vous pouvez également proposer d'autres options ou demander des informations supplémentaires

def get_user_address(user_id):
    try:
        cursor = conn.cursor()
        query = "SELECT adresse FROM clients WHERE client_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]  # Retourne l'adresse du client
        else:
            return None  # Aucune adresse trouvée pour ce client

    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la récupération de l'adresse du client :", error)
        return None


def confirm_pickup_address(user_id, address):
    # Crée les boutons de confirmation d'adresse
    btn_confirm = types.InlineKeyboardButton("Confirmer", callback_data="confirm_pickup")
    btn_change = types.InlineKeyboardButton("Changer", callback_data="change_address")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(btn_confirm, btn_change)

    # Envoie le message avec l'adresse et les boutons de confirmation
    bot.send_message(user_id, f"Votre adresse de retrait :\n\n{address}\n\nConfirmez-vous cette adresse ?", reply_markup=markup)

def confirm_delivery_address(user_id, address):
    # Crée les boutons de confirmation d'adresse
    btn_confirm = types.InlineKeyboardButton("Confirmer", callback_data="confirm_address")
    btn_change = types.InlineKeyboardButton("Changer", callback_data="change_address")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(btn_confirm, btn_change)

    # Envoie le message avec l'adresse et les boutons de confirmation
    bot.send_message(user_id, f"Votre adresse de livraison :\n\n{address}\n\nConfirmez-vous cette adresse ?", reply_markup=markup)

def process_delivery_address(message):
    user_id = message.from_user.id
    delivery_address = message.text

    # Vérifie si l'adresse de livraison est valide (vous pouvez ajouter vos critères de validation ici)
    if len(delivery_address) > 1:
        # L'adresse de livraison est valide, on peut l'utiliser
        update_user_address(user_id, delivery_address)
        bot.send_message(user_id, "Votre adresse de livraison a été enregistrée avec succès.")
    else:
        bot.send_message(user_id, "Adresse de livraison invalide. Veuillez entrer une adresse valide.")



def update_user_address(user_id, address):
    try:
        cursor = conn.cursor()
        query = "UPDATE clients SET adresse = %s WHERE client_id = %s"
        values = (address, user_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la mise à jour de l'adresse du client :", error)


@bot.callback_query_handler(func=lambda call: call.data == 'confirm_address')
def handle_confirm_address(call):
    user_id = call.from_user.id
    
    # Récupérer la date et l'heure actuelle
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Récupérer le montant total du panier
    total_amount = calculate_total_amount(user_id)
    
    # Récupérer l'adresse de livraison confirmée
    delivery_address = get_user_address(user_id)
    
    # Calculer le montant total du reçu
    receipt_amount = total_amount + 1000

    # Construire le message de réception
    receipt_message = f"Voici votre reçu :\n\n"
    receipt_message += f"Date et heure : {current_datetime}\n"
    receipt_message += f"Montant total du panier : {total_amount} FCFA\n"
    receipt_message += f"Adresse de livraison : {delivery_address}\n"
    receipt_message += f"Montant total du reçu : {receipt_amount} FCFA\n\n"
    
    # Créer le bouton de confirmation de paiement
    btn_confirm_payment = types.InlineKeyboardButton("Confirmer le paiement", callback_data="confirm_payment")
    markup = types.InlineKeyboardMarkup().add(btn_confirm_payment)
    
    # Envoyer le message de réception avec le bouton de confirmation de paiement
    bot.send_message(user_id, receipt_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_pickup')
def handle_confirm_pickup(call):
    user_id = call.from_user.id
    
    # Récupérer la date et l'heure actuelle
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Récupérer le montant total du panier
    total_amount = calculate_total_amount(user_id)
    
    # Récupérer l'adresse de livraison confirmée
    delivery_address = get_user_address(user_id)
    
    # Calculer le montant total du reçu
    receipt_amount = total_amount

    # Construire le message de réception
    receipt_message = f"Voici votre reçu :\n\n"
    receipt_message += f"Date et heure : {current_datetime}\n"
    receipt_message += f"Montant total du panier : {total_amount} FCFA\n"
    receipt_message += f"Adresse de livraison : {delivery_address}\n"
    receipt_message += f"Montant total du reçu : {receipt_amount} FCFA\n\n"
    
    # Créer le bouton de confirmation de paiement
    btn_confirm_payment = types.InlineKeyboardButton("Confirmer le paiement", callback_data="confirm_payment")
    markup = types.InlineKeyboardMarkup().add(btn_confirm_payment)
    
    # Envoyer le message de réception avec le bouton de confirmation de paiement
    bot.send_message(user_id, receipt_message, reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data == 'change_address')
def handle_change_address(call):
    # Demande au client d'entrer une nouvelle adresse
    bot.send_message(call.from_user.id, "Veuillez entrer votre nouvelle adresse de livraison :")
    bot.register_next_step_handler(call.message, process_delivery_address)



@bot.callback_query_handler(func=lambda call: call.data == 'delivery')
def handle_delivery(call):
    # Traite la récupération par livraison
    bot.send_message(call.from_user.id, "Vous avez choisi de vous faire livrer.")


@bot.callback_query_handler(func=lambda call: call.data == 'pickup')
def handle_pickup(call):
    # Traite la récupération en personne
    bot.send_message(call.from_user.id, "Vous avez choisi de récupérer en personne.")




@bot.callback_query_handler(func=lambda call: call.data == 'clear')
def handle_clear(call):
    user_id = call.from_user.id
    clear_cart(user_id)
    bot.answer_callback_query(call.id, "Le panier a été vidé.")


def clear_cart(user_id):
    if user_id in user_carts:
        user_carts[user_id] = {}


def get_categories():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categorie FROM produits")
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return categories


def calculate_total_amount(user_id):
    cart_content = get_cart_content(user_id)
    total_amount = 0

    for product_name, quantity in cart_content.items():
        price = get_product_price(product_name)
        if price is not None:
            total_amount += price * quantity

    return total_amount






def get_products_by_category(category):
    cursor = conn.cursor()
    query = "SELECT nom_produit, description_produit, prix_produit FROM produits WHERE categorie = %s"
    cursor.execute(query, (category,))
    products = cursor.fetchall()
    cursor.close()
    return products



def get_product_price(product_name):
    try:
        cursor = conn.cursor()
        query = "SELECT prix_produit FROM produits WHERE nom_produit = %s"
        cursor.execute(query, (product_name,))
        price = cursor.fetchone()
        if price is not None:
            return price[0]
        else:
            return None
    except (psycopg2.Error, Exception) as error:
        print("Erreur lors de la récupération du prix du produit:", error)
        return None
    finally:
        cursor.close()



def handle_contactez_nous(message):
    contacts = {
        "Email": "defspsp@gmail.com",
        "Numéro de téléphone": "+237656958696"
    }
    
    contact_message = "Pour nous contacter :\n"
    for title, value in contacts.items():
        contact_message += f"{title}: {value}\n"
    
    # Envoie les informations de contact sans désactiver le clavier
    bot.reply_to(message, contact_message)



def add_product_to_cart(user_id, product_name):
    if user_id in user_carts:
        cart = user_carts[user_id]
        if product_name in cart:
            cart[product_name] += 1
        else:
            cart[product_name] = 1
    else:
        user_carts[user_id] = {product_name: 1}


def get_cart_content(user_id):
    return user_carts.get(user_id, {})


@bot.message_handler(func=lambda message: message.text.startswith("Acheter"))
def handle_acheter(message):
    if message.text == "🛒 Voir Panier":
        handle_voir_panier(message)  # Appelle directement la fonction handle_voir_panier
        return 
    # Récupère les catégories de produits depuis la base de données
    categories = get_categories()

    # Crée les boutons de catégories
    markup = types.ReplyKeyboardMarkup(row_width=2)
    buttons = [types.KeyboardButton(category) for category in categories]

    # Ajoute le bouton "Quitter"
    buttons.append(types.KeyboardButton("Quitter"))
    buttons.append(types.KeyboardButton("🛒 Voir Panier"))
    markup.add(*buttons)

    # Envoie le message avec les boutons de catégories
    bot.reply_to(message, 'Veuillez sélectionner une catégorie :', reply_markup=markup)

    # Enregistre la prochaine étape pour traiter la catégorie sélectionnée
    bot.register_next_step_handler(message, process_selected_category)


def process_selected_category(message):
    category = message.text

    # Vérifie si la catégorie est valide en la comparant aux catégories disponibles
    categories = get_categories()
    if category in categories:
        # La catégorie est valide, on peut afficher les produits
        get_products_by_category(category)
    else:
        bot.send_message(message.chat.id, "Catégorie invalide. Veuillez sélectionner une catégorie valide.")


scanned_invoice_id = None

# Gère l'action du bouton "Scanner QR code"
@bot.message_handler(func=lambda message: message.text.startswith("Scanner QR code"))
def handle_scanner_qrcode(message):
    user_id = message.from_user.id
    
    invoices = get_invoices_by_user(user_id)
    invoices_in_progress = [invoice for invoice in invoices if invoice[3] == 'en_cours']  # Remplace ['etat'] par [4]
    if invoices_in_progress:
        response = "Voici vos livraisons en cours :\n\n"
        for invoice in invoices_in_progress:
            facture_id = invoice[0]
            client_id = invoice[1]
            lieu_livraison = invoice[2]
            etat = invoice[3]
            response += f"Facture ID : {facture_id}\nClient ID : {client_id}\nLieu de livraison : {lieu_livraison}\nÉtat : {etat}\n\n"
        bot.reply_to(message, response)
        # Créer les boutons "Envoyer le code" et "Prendre une photo"
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_send_code = types.InlineKeyboardButton("Envoyer le code", callback_data="send_code")
        btn_take_photo = types.InlineKeyboardButton("Prendre une photo", callback_data="take_photo")
        markup.row(btn_send_code, btn_take_photo)
        bot.reply_to(message, "Veuillez choisir une option :", reply_markup=markup)
    else:
        bot.reply_to(message, "Aucune livraison en cours.")


@bot.callback_query_handler(func=lambda call: call.data == "send_code")
def handle_send_code(call):
    message = call.message
    client_id = message.chat.id
    # Demander à l'utilisateur d'envoyer une photo
    bot.reply_to(message, "Veuillez envoyer une photo du code QR.")
    bot.register_next_step_handler(message, check_qr_code_photo)

    # Définir la fonction de vérification de la photo
def check_qr_code_photo(message):
    user_id = message.from_user.id
    invoice_id = get_invoice_id_from_qrcode(user_id)

    if invoice_id is None:
        bot.reply_to(message, "Aucune facture en cours.")
        return

    try:
        # Vérifie si le message a des données photo
        if message.photo:
            # Récupère les informations de la photo
            photo_info = message.photo[-1]
            photo_id = photo_info.file_id

            # Récupère la photo par son ID
            photo_file = bot.get_file(photo_id)
            photo_data = bot.download_file(photo_file.file_path)

            # Valider la photo du QR code
            if verify_qr_code_from_invoice(user_id, invoice_id, photo_data):
                set_delivery_state(invoice_id, "livree")
                bot.reply_to(message, "Le code QR correspond. La livraison a été marquée comme livrée.")
            else:
                bot.reply_to(message, "Le code QR ne correspond pas. Veuillez réessayer.")
        else:
            bot.reply_to(message, "Aucune photo n'a été envoyée. Veuillez envoyer une photo contenant le code QR.")

    except Exception as api_exception:
        bot.reply_to(message, "Une erreur s'est produite lors du traitement de la photo. Veuillez réessayer.")
        print("Error while processing photo:", api_exception)

@bot.message_handler(func=lambda message: message.text == "🛒 Voir Panier")
def handle_voir_panier(message):
    user_id = message.from_user.id
    cart_content = get_cart_content(user_id)
    response = "Contenu du panier :\n\n"
    if cart_content:
        total_price = 0
        for product_name, quantity in cart_content.items():
            price = get_product_price(product_name)
            if price is not None:
                item_price = price * quantity
                response += f"Produit : {product_name}\nQuantité : {quantity}\nPrix unitaire : {price} FCFA\nPrix total : {item_price} FCFA\n\n"
                total_price += item_price
            else:
                response += f"Produit : {product_name}\nQuantité : {quantity}\nPrix unitaire : Prix inconnu\n\n"
        response += f"Total : {total_price} FCFA"
        # Ajoute le bouton "Payer" en dessous du total
        btn_pay = types.InlineKeyboardButton("Payer", callback_data="pay")
        markup = types.InlineKeyboardMarkup().add(btn_pay)

        # Ajoute le bouton "Vider" à côté du bouton "Payer"
        btn_clear = types.InlineKeyboardButton("Vider", callback_data="clear")
        markup.row(btn_clear)

        bot.reply_to(message, response, reply_markup=markup)
    else:
        response = "Votre panier est vide."
        bot.reply_to(message, response)

def get_invoice_id_from_qrcode(client_id):
    try:
        cursor = conn.cursor()
        query = "SELECT facture_id FROM factures WHERE client_id = %s"
        cursor.execute(query, (client_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]  # Retourne l'ID de la facture
        else:
            return None  # Aucune facture trouvée pour ce client

    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la récupération de l'ID de la facture :", error)
        return None



@bot.callback_query_handler(func=lambda call: call.data == "take_photo")
def handle_take_photo_callback(call):
    message = call.message
    chat_id = message.chat.id

    # Ask the user to take a photo
    bot.send_message(chat_id, "Veuillez prendre une photo du QR code.")

    # Register the next step handler for processing the photo
    bot.register_next_step_handler(message, process_photo)



#def verify_cinetpay_transaction(transaction_id, site_id, apikey, expected_amount):
    #try:
       # url = "https://api-checkout.cinetpay.com/v2/payment/check"
        #headers = {'Content-Type': 'application/json'}
       # data = {
          #  "transaction_id": transaction_id,
         #   "site_id": site_id,
         #   "apikey": apikey
       # }

        #response = requests.post(url, json=data, headers=headers)
       # response_json = response.json()

        #if response_json.get("code") == "00" and response_json.get("data", {}).get("status") == "ACCEPTED":
            #actual_amount = response_json.get("data", {}).get("amount")
          #  #if actual_amount == expected_amount:
           #     return True
          #  else:
         #       print("Montant de la transaction ne correspond pas.")
        #        return False
       # else:
      #      print("Erreur lors de la vérification de la transaction :", response_json.get("message"))
     #       return False
    #except requests.exceptions.RequestException as e:
        #print("Erreur lors de l'appel à l'API CinetPay :", e)
        #return False
    #except Exception as e:
        #print("Une erreur s'est produite lors de la vérification de la transaction :", e)
        #return False

def verify_cinetpay_transaction(transaction_id, site_id, apikey,expected_amount):
    url = "https://api-checkout.cinetpay.com/v2/payment/check"
    headers = {'Content-Type': 'application/json'}
    data = {
        "transaction_id": transaction_id,
        "site_id": site_id,
        "apikey": apikey
    }

    response = requests.post(url, json=data, headers=headers)
    response_json = response.json()

    # Vérifier si la transaction a réussi en vérifiant le statut dans la réponse JSON
    if response_json.get("code") == "00" and response_json.get("data", {}).get("status") == "ACCEPTED":
        actual_amount = response_json.get("data", {}).get("amount")
        if actual_amount == expected_amount:
                return True
        else:
                print("Montant de la transaction ne correspond pas.")
                return False
    else:
            return False





def process_photo(message):
    if message.content_type == "photo":
        photo = message.photo[-1]  # Get the last photo sent by the user
        photo_id = photo.file_id
        client_id = message.chat.id
        # Get the photo file by its ID
        photo_file = bot.get_file(photo_id)
        photo_data = bot.download_file(photo_file.file_path)

        # Open the photo using PIL
        image = Image.open(io.BytesIO(photo_data))

        # Process the QR code in the image
        qr_code_data = decode_qr_code(image)

        if qr_code_data is not None:
            qr_code_text = qr_code_data.decode("utf-8")

            # Get the invoice ID from the QR code text
            invoice_id = qr_code_text

            # Verify the invoice and update the delivery state if the QR code is correct
            if verify_qr_code_from_invoice(client_id, invoice_id, photo_data):
                set_delivery_state(invoice_id, "livree")
                bot.reply_to(message, "Le QR code correspond. La livraison a été marquée comme livrée.")
            else:
                bot.reply_to(message, "Le QR code ne correspond pas à la facture en cours.")
        else:
            bot.reply_to(message, "Aucun QR code n'a été détecté dans la photo.")
    else:
        bot.reply_to(message, "Veuillez envoyer une photo contenant le QR code.")

    if message.content_type == "photo":
        photo = message.photo[-1]  # Get the last photo sent by the user
        photo_id = photo.file_id

        # Get the photo file by its ID
        photo_file = bot.get_file(photo_id)
        photo_data = bot.download_file(photo_file.file_path)

        # Open the photo using PIL
        image = Image.open(io.BytesIO(photo_data))

        # Process the QR code in the image
        qr_code_data = decode_qr_code(image)

        if qr_code_data is not None:
            qr_code_text = qr_code_data.decode("utf-8")

            # Get the invoice ID from the QR code text
            invoice_id = int(qr_code_text)

            # Verify the invoice and update the delivery state if the QR code is correct
            if invoice_id == message.chat.id :
                set_delivery_state(invoice_id, "livree")
                bot.reply_to(message, "Le QR code correspond. La livraison a été marquée comme livrée.")
            else:
                bot.reply_to(message, "Le QR code ne correspond pas à la facture en cours.")
        else:
            bot.reply_to(message, "Aucun QR code n'a été détecté dans la photo.")
    else:
        bot.reply_to(message, "Veuillez envoyer une photo contenant le QR code.")


def decode_qr_code(image):
    # Perform QR code decoding using the pyzbar library
    qr_code = pyzbar.decode(image)

    if qr_code:
        qr_code_data = qr_code[0].data
        return qr_code_data

    return None

def get_delivery_state(client_id):
    try:
        cursor = conn.cursor()
        query = "SELECT etat FROM etat_facture WHERE facture_id IN (SELECT facture_id FROM factures WHERE client_id = %s)"
        cursor.execute(query, (client_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]  # Renvoie l'état de livraison
        else:
            return None  # Aucun résultat trouvé pour le client ID donné
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la récupération de l'état de livraison:", error)
        return None



def verify_qr_code_from_invoice(client_id, invoice_id, image_path):
    try:
        # Charger l'image contenant le code QR
        image = Image.open(image_path)

        # Décoder le code QR de l'image
        decoded_qr_codes = pyzbar.decode(image)

        # Vérifier si le code QR correspond à la facture associée à l'ID du client
        for qr_code in decoded_qr_codes:
            qr_code_data = qr_code.data.decode('utf-8')

            # Vérifier si le code QR contient l'ID du client et l'ID de la facture
            if f"Facture_ID:{invoice_id},Client_ID:{client_id}" in qr_code_data:
                return True

        # Si aucun code QR valide n'est trouvé
        return False

    except Exception as error:
        print("Erreur lors de la vérification du code QR :", error)
        return False



def get_invoices_by_user(user_id):
    try:
        cursor = conn.cursor()
        query = """
        SELECT f.facture_id, f.client_id, f.lieu_livraison, ef.etat
        FROM factures f
        INNER JOIN etat_facture ef ON f.facture_id = ef.facture_id
        WHERE f.client_id = %s AND ef.etat = 'en_cours'
        """
        values = (user_id,)
        cursor.execute(query, values)
        invoices = cursor.fetchall()
        cursor.close()
        return invoices
    except (Exception, psycopg2.Error) as error:
        print("Une erreur s'est produite lors de la récupération des factures :", error)
        return []



def set_delivery_state(facture_id, etat):
    try:
        cursor = conn.cursor()
        query = "UPDATE etat_facture SET etat = %s WHERE facture_id = %s"
        values = (etat, facture_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return True
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la mise à jour de l'état de livraison :", error)
        return False


def confirm_delivery(invoice_id):
    try:
        cursor = conn.cursor()
        query = "UPDATE etat_facture SET etat = 'En cours' WHERE facture_id = %s"
        cursor.execute(query, (invoice_id,))
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la confirmation de la livraison :", error)


def get_product_images(product_name):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT pi.image FROM produits p INNER JOIN produits_image pi ON p.produit_id = pi.produit_id WHERE p.nom_produit = %s", (product_name,))
        images = cursor.fetchall()
        cursor.close()

        base_path = r"C:/Users/Public/images"  # Chemin de base de votre serveur local
    except (Exception, psycopg2.Error) as error:
        print("erreur lors de la recuperation de l'image du produit:", error)

    return [os.path.join(base_path, image[0]) for image in images]

def send_product_images(chat_id, images):
    for image in images:
        with open(image, 'rb') as photo:
            bot.send_photo(chat_id, photo)

try:
    while True:
        bot.polling(none_stop=True)
except KeyboardInterrupt:
    print("Arrêt du bot suite à une interruption manuelle.")
except Exception as e:
    print("Une erreur s'est produite lors de l'exécution du bot :", e)

