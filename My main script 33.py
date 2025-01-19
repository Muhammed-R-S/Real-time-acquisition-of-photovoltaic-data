import labjack.ljm as ljm
import sqlite3
import datetime
import ephem
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Function to be executed during the specified time range
def perform_task():
    # Configure LabJack connection
    handle = ljm.openS("ANY", "ANY", "ANY")  # Open the first available LabJack
    info = ljm.getHandleInfo(handle)
    print("Connected to LabJack", info)

    # Configure analog input channels
    AIN_CHANNELS = [0, 1]  # Desired analog input channels

    # Get current date and time for table name
    current_datetime = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    table_name = f"Muhammed_{current_datetime}"  # Table name with current date and time

    # Connect to SQLite database
    db_file = f"{table_name}.db"  # Desired SQLite database file name or path
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            current_amperes REAL,
            voltage_volts REAL
        )
    '''
    cursor.execute(create_table_query)
    conn.commit()

    data_list = []  # List to accumulate the data

    # Calculate sunrise and sunset times
    observer = ephem.Observer()
    observer.lat = '34.0181'  # My latitude in decimal degrees
    observer.lon = '-5.0078'  # My longitude in decimal degrees

    sunrise = ephem.localtime(observer.previous_rising(ephem.Sun(), start=observer.date)).time()
    sunset = ephem.localtime(observer.next_setting(ephem.Sun(), start=observer.date)).time()
    next_sunrise = ephem.localtime(observer.next_rising(ephem.Sun(), start=observer.date)).time()

    # Create the figure and axes for the real-time graph
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()  # Create the second y-axis

    # Set the initial limits for the y-axis
    ax1.set_ylim(0, None)  # Set the y-axis limit for current (start from 0)
    ax2.set_ylim(15, 35)  # Set the y-axis limit for voltage (start from 0)
    
    x_data = []
    y_current = []
    y_voltage = []

    # Create line plots for current and voltage
    line_current, = ax1.plot(x_data, y_current, color='blue', label='Current (Amperes)')
    line_voltage, = ax2.plot(x_data, y_voltage, color='red', label='Voltage (Volts)')
    
    # Set labels and title
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Current (Amperes)', color='blue')
    ax2.set_ylabel('Voltage (Volts)', color='red')
    ax1.set_title('Real-time Data Plot')


    # Add legend
    lines = [line_current, line_voltage]
    ax1.legend(lines, [line.get_label() for line in lines])
    
    # Format x-axis as time
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    # Show the initial graph
    plt.show(block=False)
    print("Data collection for ", current_datetime, " in progress")

    while True:
        # Check if the current time is within the specified time range
        current_time = datetime.datetime.now()
        sunrise_datetime = datetime.datetime.combine(datetime.date.today(), sunrise)
        sunset_datetime = datetime.datetime.combine(datetime.date.today(), sunset)
        next_sunrise_datetime = datetime.datetime.combine(datetime.date.today(), next_sunrise)

        if sunrise_datetime - datetime.timedelta(minutes=5) <= current_time <= sunset_datetime + datetime.timedelta(minutes=5) or next_sunrise_datetime - datetime.timedelta(minutes=5) <= current_time <= sunset_datetime + datetime.timedelta(minutes=5):

            try:
                for _ in range(12):    #12 implies 12*5 which is equals to 1 minute
                    # Read analog input data and save to database
                    timestamp = datetime.datetime.now()
                    data = [round(ljm.eReadName(handle, f"AIN{channel}"), 3) for channel in AIN_CHANNELS]
                    data[1] = round(data[1] * 18.22, 3)  # Multiply AIN1 (voltage) by 18.22
                    
                    # Update the real-time graph
                    x_data.append(timestamp)
                    y_current.append(data[0])
                    y_voltage.append(data[1])
                    line_current.set_data(x_data[-80:], y_current[-80:])  # Show only the last 80 data points
                    line_voltage.set_data(x_data[-80:], y_voltage[-80:])  # Show only the last 80 data points
                    ax1.relim()
                    ax1.autoscale_view()
                    ax2.relim()
                    ax2.autoscale_view()

                    # Redraw the updated graph
                    fig.canvas.draw()
                    fig.canvas.flush_events()

                    # Delay for 5 seconds
                    time.sleep(5)

                insert_query = f"INSERT INTO {table_name} (timestamp, current_amperes, voltage_volts) VALUES (?, ?, ?)"
                cursor.execute(insert_query, (timestamp,) + tuple(data))
                conn.commit()
                data_list.append([timestamp] + data)  # Append data to the list

            except Exception as e:
                print("An error occurred:", str(e))

        else:
            # Close the graph displaying window
            plt.close()

            # Close LabJack connection and SQLite connection
            ljm.close(handle)
            conn.close()

            # Convert data to a DataFrame
            column_names = ['Timestamp', 'Current (Amperes)', 'Voltage (Volts)']
            df = pd.DataFrame(data_list, columns=column_names)

            # Save data to Excel file
            excel_file = f"{table_name}.xls"  # desired Excel file name or path
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print("Data collection complete. Data saved to", db_file, "and", excel_file)

            # Calculate the delay until the next valid time range
            next_day_sunrise_datetime = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1),next_sunrise)
            delay = (next_day_sunrise_datetime - datetime.timedelta(minutes=5) - current_time).total_seconds()

            # Delay for the calculated time before checking the time again
            print("Data collection paused until: ", next_sunrise_datetime - datetime.timedelta(minutes=5))
            time.sleep(delay)

            # Restart the data collection process
            perform_task()


# Start the data collection process
perform_task()
