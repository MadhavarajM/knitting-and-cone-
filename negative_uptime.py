import psycopg2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
from datetime import timedelta
import shutil



def log():
    log_file_path = "/home/kniti/projects/knit-i/knitting-core/system_stats.log"
    timestamps = []
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                try:
                    # Split the line based on ':'
                    parts = line.split(': ')
                    if len(parts) >= 2:
                        timestamp_str = parts[0]
                        timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f+05:30')
                        timestamps.append(timestamp)
                    else:
                        print(f"Skipping line: {line}")
                except Exception as e:
                    print(f"Error processing line: {line}")
    except FileNotFoundError:
        print(f"File not found: {log_file_path}")

    return timestamps

def postgre(user_date):
        timestamps = []
        # Read the log file
        with open("/home/kniti/projects/knit-i/knitting-core/system_stats.log", "r") as file:
            for line in file:
                if user_date in line and "PostgreSQL: Not Running" in line:
                    # Extract the timestamp from the line and convert it to a datetime object
                    timestamp_str = line.split()[1]
                    timestamp = datetime.datetime.strptime(timestamp_str, "%H:%M:%S.%f+05:30:")
                    timestamps.append(timestamp)
        return timestamps


def docker(user_date):
        timestamps = []
        # Read the log file
        with open("/home/kniti/projects/knit-i/knitting-core/system_stats.log", "r") as file:
            for line in file:
                if user_date in line and "Docker_ml: Not Running" in line:
                    # Extract the timestamp from the line and convert it to a datetime object
                    timestamp_str = line.split()[1]
                    timestamp = datetime.datetime.strptime(timestamp_str, "%H:%M:%S.%f+05:30:")
                    timestamps.append(timestamp)
        return timestamps

def docker_alarm(user_date):
        timestamps = []
        # Read the log file
        with open("/home/kniti/projects/knit-i/knitting-core/system_stats.log", "r") as file:
            for line in file:
                if user_date in line and "Docker_alarm: Not Running" in line:
                    # Extract the timestamp from the line and convert it to a datetime object
                    timestamp_str = line.split()[1]
                    timestamp = datetime.datetime.strptime(timestamp_str, "%H:%M:%S.%f+05:30:")
                    timestamps.append(timestamp)
        return timestamps


def generate_plot(user_date, missing_minutes_per_hour, timestamp, timestamp_db,timestamp_docker,timestamp_alarm,pdf_pages):
    print("Code is running it will take time")   
    
    path = "/home/kniti"
    stat = shutil.disk_usage(path)
    free_space_gb = stat.free / 1e9

    all_minutes_within_hour_log = []  # Accumulate all minutes data
    
    for hour_key, missing_minutes in missing_minutes_per_hour.items():
        # Extract the datetime objects from missing_minutes
        missing_minutes_datetime = missing_minutes
        
        # Create corresponding datetimes with the same date and hour
        datetimes = [minute.replace(second=0, microsecond=0) for minute in missing_minutes_datetime]
       
        # Convert datetimes to minutes within the hour
        minutes_within_hour_log = [t.hour * 60 + t.minute for t in datetimes]

        # Append the minutes data to the accumulated list
        all_minutes_within_hour_log.extend(minutes_within_hour_log)

    minute_counts = {}
    for minute in all_minutes_within_hour_log:
        if minute in minute_counts:
            minute_counts[minute] += 1
        else:
            minute_counts[minute] = 1
    # Extract minutes and corresponding counts
    minutes = list(minute_counts.keys())
    counts = [1 if minute_counts[minute] > 1 else minute_counts[minute] for minute in minutes]
 

# Define your PostgreSQL connection parameters
    db_params = {
        'dbname': 'knitting',
        'user': 'postgres',
        'password': '55555',
        'host': 'localhost'
    }

# The SQL queries
    sql_query1 = """
            SELECT
                timestamp
            FROM
                uptime_status
            WHERE
                DATE(timestamp) = %s
            GROUP BY
                timestamp
            HAVING
                COUNT(CASE WHEN software_status = '0' THEN 1 ELSE NULL END) = 1;
        """

    sql_query2 = """
        SELECT
            timestamp
        FROM
            uptime_status
        WHERE
            DATE(timestamp) = %s
        GROUP BY
            timestamp
        HAVING
            COUNT(CASE WHEN camera_status = '0' THEN 1 ELSE NULL END) = 1;
    """

    sql_query3 = """
        SELECT
            timestamp
        FROM
            uptime_status
        WHERE
            DATE(timestamp) = %s
        GROUP BY
            timestamp
        HAVING
            COUNT(CASE WHEN controller_status = '0' THEN 1 ELSE NULL END) = 1;
    """

    sql_query4 = """
SELECT
    timestamp
FROM
    uptime_status
WHERE
    DATE(timestamp) = %s
GROUP BY
    timestamp
HAVING
    COUNT(CASE WHEN image_status = '0' THEN 1 ELSE NULL END) = 1;

"""
    
    sql_query5 = """
    SELECT
        timestamp
    FROM
        uptime_status
    WHERE
        DATE(timestamp) = %s
    GROUP BY
        timestamp
    HAVING
        COUNT(CASE WHEN machine_status = '0' THEN 1 ELSE NULL END) > 0;
"""
    
    sql_query6 = """SELECT
    timestamp
FROM
    uptime_status
WHERE
    DATE(timestamp) = %s
GROUP BY
    timestamp
HAVING
    COUNT(CASE WHEN machine_status = '1' AND image_status = '0' THEN 1 ELSE NULL END) > 0;

"""

    timestamps_log = timestamp
    timestamp_gre = timestamp_db
    timestamp_dck = timestamp_docker
    timestamp_alm = timestamp_alarm
    target_date = user_date

    # Connect to the database
    connection = psycopg2.connect(**db_params)

    # Create a cursor object
    cursor = connection.cursor()

    cursor.execute(sql_query1, (target_date,))
    timestamps_software = cursor.fetchall()
    
    cursor.execute(sql_query2, (target_date,))
    timestamps_camera = cursor.fetchall()
    
    cursor.execute(sql_query3, (target_date,))
    timestamps_controller = cursor.fetchall()

    cursor.execute(sql_query4, (target_date,))
    timestamps_image = cursor.fetchall()

    cursor.execute(sql_query5, (target_date,))
    timestamps_machine = cursor.fetchall()

    cursor.execute(sql_query6, (target_date,))
    timestamps_image2 = cursor.fetchall()
    
    minutes_within_hour_log = [t.hour * 60 + t.minute for t in timestamps_log]
    minutes_within_hour_software = [timestamp[0].hour * 60 + timestamp[0].minute for timestamp in timestamps_software]
    minutes_within_hour_camera = [timestamp[0].hour * 60 + timestamp[0].minute for timestamp in timestamps_camera]
    minutes_within_hour_controller = [timestamp[0].hour * 60 + timestamp[0].minute for timestamp in timestamps_controller]
    minutes_within_hour_image = [timestamp[0].hour * 60 + timestamp[0].minute for timestamp in timestamps_image]
    minutes_within_hour_machine = [timestamp[0].hour * 60 + timestamp[0].minute for timestamp in timestamps_machine]
    minutes_within_hour_db = [t.hour * 60 + t.minute for t in timestamp_gre]
    minutes_within_hour_image2 = [timestamp[0].hour * 60 + timestamp[0].minute for timestamp in timestamps_image2]
    minutes_within_hour_docker = [t.hour * 60 + t.minute for t in timestamp_dck]
    minutes_within_hour_alarm = [t.hour * 60 + t.minute for t in timestamp_alm]

    bar_width = 0.1  # Adjust this value as needed

    # Create subplots with shared x-axis
    fig, (ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8,ax9,ax10,ax11) = plt.subplots(11 , 1, figsize=(40, 40), sharex=True)


    # Plot the first query result in the lower subplot
    bars1 = ax1.bar(minutes_within_hour_log, [1] * len(minutes_within_hour_log), width=bar_width, align='center', color='green')
    bars2 = ax2.bar(minutes, [1] * len(counts), width=0.1, align='center', color='red')
    bars3 = ax3.bar(minutes_within_hour_software, [1] * len(minutes_within_hour_software), width=bar_width, align='edge', color='red')
    bar3_3 = ax3.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars4 = ax4.bar(minutes_within_hour_camera, [1] * len(minutes_within_hour_camera), width=bar_width, align='edge', color='red')
    bar4_4 = ax4.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars5 = ax5.bar(minutes_within_hour_controller, [1] * len(minutes_within_hour_controller), width=bar_width, align='edge', color='red')
    bar5_5 = ax5.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars6 = ax6.bar(minutes_within_hour_image, [1] * len(minutes_within_hour_image), width=bar_width, align='edge', color='red')
    bar6_6 = ax6.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars7 = ax7.bar(minutes_within_hour_image2, [1] * len(minutes_within_hour_image2), width=bar_width, align='edge', color='red')
    bar7_7 = ax7.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars8 = ax8.bar(minutes_within_hour_machine, [1] * len(minutes_within_hour_machine), width=bar_width, align='edge', color='red')
    bar8_8 = ax8.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars9 = ax9.bar(minutes_within_hour_db, [1] * len(minutes_within_hour_db), width=bar_width, align='center', color='red')
    bar9_9 = ax9.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars10 = ax10.bar(minutes_within_hour_docker, [1] * len(minutes_within_hour_docker), width=bar_width, align='center', color='red')
    bar10_10 = ax10.bar(minutes, counts, width=0.1, align='center', color='blue')
    bars11 = ax11.bar(minutes_within_hour_alarm, [1] * len(minutes_within_hour_alarm), width=bar_width, align='center', color='red')
    bar11_11 = ax11.bar(minutes, counts, width=0.1, align='center', color='blue')
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    ax1.set_title(f'KPT_MACHINE1_NEGATIVE_UPTIME_FOR-{user_date}', fontsize = 24)
    ax11.set_xlabel(f'Free space : {free_space_gb} GB', fontsize = 24, loc='right')
    ax1.set_title(f'Pdf generated at : {formatted_datetime}', fontsize = 24, loc='right')
    ax1.set_title(f'Version : 1.2.1.0', fontsize = 24, loc='left')
    plt.xticks(range(0, 1440, 60), [f'{i // 60:02}:{i % 60:02}' for i in range(0, 1440, 60)])

    legend1 = ax1.legend(['Knit-i on  Status'], loc='upper left', fontsize='25')
    legend2 = ax2.legend(['Knit-i off Status'], loc='upper left', fontsize='25')
    legend3 = ax3.legend(['Software off Status'], loc='upper left', fontsize='25')
    legend4 = ax4.legend(['Camera off Status'], loc='upper left', fontsize='25')
    legend5 = ax5.legend(['Controller off Status'], loc='upper left', fontsize='25')
    legend6 = ax6.legend(['Image off status'], loc='upper left', fontsize='25')
    legend7 = ax7.legend(['Machine On Image off Status'], loc='upper left', fontsize='25')
    legend8 = ax8.legend(['Machine off Status'], loc='upper left', fontsize='25')
    legend9 = ax9.legend(['Db off status'], loc='upper left', fontsize='25')
    legend10 = ax10.legend(['Docker-ML off status'], loc='upper left', fontsize='25')
    legend11 = ax11.legend(['Docker-alarm off status'], loc='upper left', fontsize='25')


    # Add the legends to the subplots
    ax1.add_artist(legend1)
    ax2.add_artist(legend2)
    ax3.add_artist(legend3)
    ax4.add_artist(legend4)
    ax5.add_artist(legend5)
    ax6.add_artist(legend6)
    ax7.add_artist(legend7)
    ax8.add_artist(legend8)
    ax9.add_artist(legend9)
    ax10.add_artist(legend10)
    ax11.add_artist(legend11)

    
    plt.tight_layout()
    pdf_pages.savefig()
    plt.close()

if __name__ == '__main__':
    user_input_date = input("Enter date (YYYY-MM-DD): ")
    pdf_file = f"uptime_report/KPT_MACHINE1_Negative_Uptime_status{user_input_date}.pdf"
    pdf_pages = PdfPages(pdf_file)
    timestamps = log()
    filtered_timestamps = [t for t in timestamps if t.date() == datetime.datetime.strptime(user_input_date, '%Y-%m-%d').date()]
    missing_minutes_per_hour = {}
    filtered_timestamps.sort()
    first_timestamp = min(filtered_timestamps)
    last_timestamp = max(filtered_timestamps)
    current_hour = datetime.datetime(first_timestamp.year, first_timestamp.month, first_timestamp.day)
    current_minute = 0  # Initialize current_minute to 0

    while current_hour <= last_timestamp:
        hour_key = current_hour.strftime('%Y-%m-%d %H')

        # Check if the hour is not in filtered_timestamps
        if hour_key not in [ts.strftime('%Y-%m-%d %H') for ts in filtered_timestamps]:
            # If not in filtered_timestamps, add all 60 minutes for this hour
            if hour_key not in missing_minutes_per_hour:
                missing_minutes_per_hour[hour_key] = []

            for missing_minute in range(current_minute, 60):
                missing_minutes_per_hour[hour_key].append(current_hour + timedelta(minutes=missing_minute))
            current_minute = 0  # Reset current_minute after adding all missing minutes

        current_hour += timedelta(hours=1)
        
    if first_timestamp.minute != 0:
    # Calculate the missing minutes before the current time
        missing_minutes_before_current = first_timestamp.minute
        if hour_key not in missing_minutes_per_hour:
            missing_minutes_per_hour[hour_key] = []
        for missing_minute in range(1, int(missing_minutes_before_current)):
            # Create a timedelta for the missing minutes
            missing_minute_timedelta = timedelta(minutes=missing_minute)
            # Add the missing minute timedelta to missing_minutes_before_current
            missing_minute_timestamp = first_timestamp - missing_minute_timedelta 
            missing_minutes_per_hour[hour_key].append(missing_minute_timestamp)
                    
    for i in range(len(filtered_timestamps) - 1):
        current_time = filtered_timestamps[i]
        next_time = filtered_timestamps[i + 1]
        
        # Calculate the time difference in minutes between current and next timestamps
        time_diff = (next_time - current_time).total_seconds() / 60

        # Check if the time difference is greater than 1 minute
        if time_diff > 1:
            # Identify the hour of the current timestamp
            hour_key = current_time.strftime('%Y-%m-%d %H:00:00')

            # Initialize the missing minutes list for this hour if not already created
            if hour_key not in missing_minutes_per_hour:
                missing_minutes_per_hour[hour_key] = []

            # Append the missing minutes to the list
            for missing_minute in range(1, int(time_diff)):
                missing_minutes_per_hour[hour_key].append(
                    current_time + timedelta(minutes=missing_minute)
                )
    
    timestamp_db = postgre(user_input_date)
    timestamp_docker = docker(user_input_date)
    timestamp_alarm = docker_alarm(user_input_date)
    with pdf_pages:
        generate_plot(user_input_date,missing_minutes_per_hour,filtered_timestamps,timestamp_db,timestamp_docker,timestamp_alarm,pdf_pages)




