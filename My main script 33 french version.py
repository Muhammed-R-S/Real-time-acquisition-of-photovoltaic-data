
import labjack.ljm as ljm
import sqlite3
import datetime
import ephem
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Fonction à exécuter pendant la plage de temps spécifiée
def perform_task():
    # Configurer la connexion LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Ouvrez le premier LabJack disponible
    info = ljm.getHandleInfo(handle)
    print("Connecté à LabJack", info)

    # Configurer les canaux d'entrée analogiques
    AIN_CHANNELS = [0, 1]  # Canaux d'entrée analogiques souhaités

    # Obtenir la date et l'heure actuelles pour le nom de la table
    current_datetime = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    table_name = f"Muhammed_{current_datetime}"  # Nom de la table avec la date et l'heure actuelles

    # Connectez-vous à la base de données SQLite
    db_file = f"{table_name}.db"  # Nom ou chemin d'accès au fichier de base de données SQLite souhaité
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Créer une table si elle n'existe pas
    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instant_de_mesure TEXT,
            courant_amperes REAL,
            tension_volts REAL
        )
    '''
    cursor.execute(create_table_query)
    conn.commit()

    data_list = []  # Liste pour accumuler les données

    # Calculer les heures de lever et de coucher du soleil
    observer = ephem.Observer()
    observer.lat = '34.0181'  # Ma latitude en degrés décimaux
    observer.lon = '-5.0078'  # Ma longitude en degrés décimaux

    sunrise = ephem.localtime(observer.previous_rising(ephem.Sun(), start=observer.date)).time()
    sunset = ephem.localtime(observer.next_setting(ephem.Sun(), start=observer.date)).time()
    next_sunrise = ephem.localtime(observer.next_rising(ephem.Sun(), start=observer.date)).time()

    # Créer la figure et les axes du graphique en temps réel
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()  # Créer le deuxième axe y

    # Définir les limites initiales de l'axe des ordonnées
    ax1.set_ylim(0, 5)  # Définissez la limite de l'axe des y pour le courant (commencez à partir de 0)
    ax2.set_ylim(15, 35)  # Définir la limite de l'axe y pour la tension (commencer à partir de 15)
    
    x_data = []
    y_current = []
    y_voltage = []

    # Créer des traces linéaires pour le courant et la tension
    line_current, = ax1.plot(x_data, y_current, color='blue', label='Courant (Amperes)')
    line_voltage, = ax2.plot(x_data

, y_voltage, color='red', label='Tension (Volts)')
    
    # Définir les étiquettes et le titre
    ax1.set_xlabel('Instant de mesure')
    ax1.set_ylabel('Courant (Amperes)', color='blue')
    ax2.set_ylabel('Tension (Volts)', color='red')
    ax1.set_title('Graphique des données en temps réel')

    # Ajouter une légende
    lines = [line_current, line_voltage]
    ax1.legend(lines, [line.get_label() for line in lines])
    
    # Formater l'axe des abscisses en tant que temps
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    # Afficher le graphique initial
    plt.show(block=False)
    print("Collecte de données pour ", current_datetime, " en cours")

    while True:
        # Vérifier si l'heure actuelle se situe dans la plage horaire spécifiée
        current_time = datetime.datetime.now()
        sunrise_datetime = datetime.datetime.combine(datetime.date.today(), sunrise)
        sunset_datetime = datetime.datetime.combine(datetime.date.today(), sunset)
        next_sunrise_datetime = datetime.datetime.combine(datetime.date.today(), next_sunrise)

        if sunrise_datetime - datetime.timedelta(minutes=5) <= current_time <= sunset_datetime + datetime.timedelta(minutes=5) or next_sunrise_datetime - datetime.timedelta(minutes=5) <= current_time <= sunset_datetime + datetime.timedelta(minutes=5):

            try:
                for _ in range(10):    #12 implique 10*3 qui est égal à 30 SECONDES
                    # Lire les données d'entrée analogiques et les enregistrer dans la base de données
                    instant_de_mesure = datetime.datetime.now().strftime("%H:%M:%S")
                    data = [round(ljm.eReadName(handle, f"AIN{channel}"), 3) for channel in AIN_CHANNELS]
                    data[1] = round(data[1] * 18.22, 3)  # Multipliez AIN1 (tension) par 18.22
                    
                    # Mettre à jour le graphique en temps réel
                    x_data.append(current_time)
                    y_current.append(data[0])
                    y_voltage.append(data[1])
                    line_current.set_data(x_data[-80:], y_current[-80:])  # Afficher uniquement les 80 derniers points de données
                    line_voltage.set_data(x_data[-80:], y_voltage[-80:])  # Afficher uniquement les 80 derniers points de données
                    ax1.relim()
                    ax1.autoscale_view()
                    ax2.relim()
                    ax2.autoscale_view()

                    # Redessiner le graphique mis à jour
                    fig.canvas.draw()
                    fig.canvas.flush_events()

                    # Délai de 3 secondes
                    time.sleep(3)

                insert_query = f"INSERT INTO {table_name} (instant_de_mesure, courant_amperes, tension_volts) VALUES (?, ?, ?)"
                cursor.execute(insert_query, (instant_de_mesure,) + tuple(data))
                conn.commit()
                data_list.append([instant_de_mesure] + data)  # Ajouter des données à la liste

            except Exception as e:
                print("Une erreur s'est produite :", str(e))

        else:
            # Fermer la fenêtre d'affichage du graphique
            plt.close()

            # Fermer la connexion LabJack et la connexion SQLite
            ljm.close(handle)
            conn.close()

            # Convertir des données en DataFrame
           

            df = pd.DataFrame(data_list, columns=["Instant de mesure", "Courant (Amperes)", "Tension (Volts)"])

            # Enregistrer les données dans un fichier Excel
            excel_file = f"{table_name}.xlsx"  # Nom du fichier Excel souhaité
            df.to_excel(excel_file, index=False)
            print("Les données ont été enregistrées dans le fichier Excel :", excel_file)
            break

# Appeler la fonction pour effectuer la tâche
perform_task()