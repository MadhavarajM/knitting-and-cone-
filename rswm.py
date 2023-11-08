import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.image as mpimg
import csv
import os




def production(csv_file_speed, csv_file_error, csv_file_reidle, ax):
    # Read the CSV file into a Pandas DataFrame, using a comma as the separator
    data_hourly = pd.read_csv(csv_file_speed, sep=',')
    data_hourly['DATE/TIME'] = pd.to_datetime(data_hourly['DATE/TIME'], format='%d:%m:%Y/%H:%M:%S')
    # Extract the hour from the 'DATE/TIME' column
    data_hourly['Hour'] = data_hourly['DATE/TIME'].dt.hour
    data_hourly['NO OF CONES'] = 18
    # Group the data by 'Hour' and calculate the sum of 'NO OF CONES' for each hour
    hourly_data = data_hourly.groupby('Hour')['NO OF CONES'].sum().reset_index()
   

    # Plot the production data on the left side of the double bar graph
    ax.bar(hourly_data['Hour'] - 0.2, hourly_data['NO OF CONES'], width=0.2, color='blue', label='Number of Cones Packaged')
    ax.tick_params(axis='x', colors='black', labelsize=16)
    ax.tick_params(axis='y', colors='black', labelsize=16)

    gap_above_bar = 5  # Adjust this value to control the gap above the bars
    for i, count in enumerate(hourly_data['NO OF CONES']):
        ax.text(hourly_data['Hour'][i] - 0.2, count + gap_above_bar, str(int(count)), ha='center', va='bottom', fontsize=12, rotation='vertical')


    # Create a second set of axes (ax2) with the same y scaling
    ax2 = ax.twinx()
    ax2.set_ylabel('Idle Time (in seconds)', fontsize=18)
    ax2.tick_params(axis='y', colors='black', labelsize=16)

    # Read the CSV file into a Pandas DataFrame, using a comma as the separator
    data_hourly = pd.read_csv(csv_file_error)
    data_hourly['IDLE START'] = pd.to_datetime(data_hourly['IDLE START'])
    data_hourly['IDLE END'] = pd.to_datetime(data_hourly['IDLE END'])

    # Create a list to hold the durations for each hour, initialized with zeros for each hour of the day
    hourly_durations = [0] * 24

    # Iterate through the rows and distribute the idle time
    for index, row in data_hourly.iterrows():
        start_hour = row['IDLE START'].hour  # Extract the starting hour
        end_hour = row['IDLE END'].hour  # Extract the ending hour
        # Calculate the duration for this row (in seconds)
        duration = (row['IDLE END'] - row['IDLE START']).total_seconds()
        # If start and end hours are the same, add the duration to that hour
        if start_hour == end_hour:
            hourly_durations[start_hour] += duration
        else:
            # Add 3600 seconds for each full hour in between
            for hour in range(start_hour + 1, end_hour):
                hourly_durations[hour] += 3600
            # Subtract the portion of time before the start hour and after the end hour
            hourly_durations[start_hour] += (3600 - row['IDLE START'].minute * 60 - row['IDLE START'].second)
            hourly_durations[end_hour] += (row['IDLE END'].minute * 60 + row['IDLE END'].second)

    total_count = sum(hourly_durations)
    # Plot the second bar graph on ax2
    ax2.bar(np.arange(24), hourly_durations, width=0.2, color='red', alpha=0.7, label='Total Alarm Idle Time (seconds)')

    # Annotate each bar with its value for "Total Idle Time"
    for i, count in enumerate(hourly_durations):
        ax2.text(i, count + 7, str(int(count)), ha='center', va='bottom', fontsize=12, rotation='vertical')

    # Create a third set of axes (ax3) sharing the y scaling with ax2
    #ax3 = ax2.twinx()

    # Read the CSV file into a Pandas DataFrame, using a comma as the separator
    data_hourly = pd.read_csv(csv_file_reidle)
    # Convert 'IDLE START' and 'IDLE END' columns to datetime objects
    data_hourly['IDLE START'] = pd.to_datetime(data_hourly['IDLE START'])
    data_hourly['IDLE END'] = pd.to_datetime(data_hourly['IDLE END'])

    # Create a list to hold the durations for each hour, initialized with zeros for each hour of the day
    hourly_durations = [0] * 24

    # Iterate through the rows and distribute the idle time
    for index, row in data_hourly.iterrows():
        start_hour = row['IDLE START'].hour  # Extract the starting hour
        end_hour = row['IDLE END'].hour  # Extract the ending hour
        # Calculate the duration for this row (in seconds)
        duration = (row['IDLE END'] - row['IDLE START']).total_seconds()
        # If start and end hours are the same, add the duration to that hour
        if start_hour == end_hour:
            hourly_durations[start_hour] += duration
        else:
            # Add 3600 seconds for each full hour in between
            for hour in range(start_hour + 1, end_hour):
                hourly_durations[hour] += 3600
            # Subtract the portion of time before the start hour and after the end hour
            hourly_durations[start_hour] += (3600 - row['IDLE START'].minute * 60 - row['IDLE START'].second)
            hourly_durations[end_hour] += (row['IDLE END'].minute * 60 + row['IDLE END'].second)

    total_count_2 = sum(hourly_durations)
    # Plot the third bar graph on ax3
    ax2.bar(np.arange(24) + 0.2, hourly_durations, width=0.2, color='lightgreen', alpha=0.7, label='Total Idle Time (seconds)')

    # Annotate each bar with its value for "Total Idle Time"
    for i, count in enumerate(hourly_durations):
        ax2.text(np.arange(24)[i] + 0.2, count + 7, str(int(count)), ha='center', va='bottom', fontsize=12, rotation='vertical')

    # Legends for ax and ax2
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    # Return the total counts
    return total_count, total_count_2  
def plot_error_occurrence_idle(csv_file_error, ax):
    try:
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(csv_file_error)
        # Remove the 'empty carton not available' error from the DataFrame
        excluded_error_description = "EMPTY CARTON NOT AVAILABLE"
        df = df[df['ERROR DESCRIPTION'] != excluded_error_description]
        # Calculate the error occurrence count for each error
        error_counts = df['ERROR DESCRIPTION'].value_counts()
        # Calculate the idle time for each error in seconds
        df['IDLE START'] = pd.to_datetime(df['IDLE START'])
        df['IDLE END'] = pd.to_datetime(df['IDLE END'])
        df['IDLE TIME (s)'] = (df['IDLE END'] - df['IDLE START']).dt.total_seconds()
        # Create the positions for the grouped bar plot
        x = np.arange(len(error_counts))
        bar_width = 0.4
        # Create the first plot (error occurrence count)
        ax1 = ax.bar(x, error_counts, width=bar_width, color='blue', label='Alarm Occurrence Count')
        ax.set_ylabel('Count', color='black', fontsize=24)
        ax.tick_params(axis='y', colors='black', labelsize=24)
        ax.tick_params(axis='x', colors='black', labelsize=7.3)
        # Create the second plot (idle time for each error)
        ax2 = ax.twinx()
        ax2.bar(x + bar_width, df.groupby('ERROR DESCRIPTION')['IDLE TIME (s)'].sum(), width=bar_width, color='green', label='Alarm Idle Time (seconds)')
        ax2.set_ylabel('Idle Time (seconds)', color='black', fontsize=24)
        ax2.tick_params(axis='y', colors='black')
        ax2.tick_params(axis='y', colors='black', labelsize=24)
        # Set x-axis labels and tick positions
        ax.set_xticks(x + bar_width / 2)
        ax.set_xticklabels(error_counts.index, rotation=90)
        # Annotate the first plot (error occurrence count)
        for i, count in enumerate(error_counts):
            ax.text(i, count + 0.1, str(count), ha='center', va='bottom', rotation='vertical')
        # Annotate the second plot (idle time for each error)
        for i, idle_time in enumerate(df.groupby('ERROR DESCRIPTION')['IDLE TIME (s)'].sum()):
            ax2.text(i + bar_width, idle_time + 9, str(idle_time), ha='center', va='bottom', fontsize=12, rotation='vertical')
        # Combine legends from both plots
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')
        ax.set_title('Alarm Occurrence Count and Idle Time for Each Alarm', fontsize=30)
    except Exception as e:
        print(f"An error occurred: {str(e)}")  
def plot_reidle_occurrence_idle(csv_file_reidle, ax):
    try:
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(csv_file_reidle)
        # Calculate the error occurrence count for each error
        error_counts = df['NAME DESCRIPTION'].value_counts()
        # Calculate the idle time for each error in seconds
        df['IDLE START'] = pd.to_datetime(df['IDLE START'])
        df['IDLE END'] = pd.to_datetime(df['IDLE END'])
        df['IDLE TIME (s)'] = (df['IDLE END'] - df['IDLE START']).dt.total_seconds()
        # Create the positions for the grouped bar plot
        x = np.arange(len(error_counts))
        bar_width = 0.4
        # Create the first plot (error occurrence count)
        ax1 = ax.bar(x, error_counts, width=bar_width, color='blue', label='Machine Idle Occurrence Count')
        ax.set_ylabel('Count', color='black',fontsize=24)
        ax.tick_params(axis='y', colors='black', labelsize=24)
        ax.tick_params(axis='x', colors='black', labelsize=7)
        # Create the second plot (idle time for each error)
        ax2 = ax.twinx()
        ax2.bar(x + bar_width, df.groupby('NAME DESCRIPTION')['IDLE TIME (s)'].sum(), width=bar_width, color='green', label='Machine Idle Time (seconds)')
        ax2.set_ylabel('Idle Time (seconds)', color='black',fontsize=24)
        ax2.tick_params(axis='y', colors='black')
        ax2.tick_params(axis='y', colors='black', labelsize=24)
        # Set x-axis labels and tick positions
        ax.set_xticks(x + bar_width / 2)
        ax.set_xticklabels(error_counts.index, rotation=90)
        # Annotate the first plot (error occurrence count)
        for i, count in enumerate(error_counts):
            ax.text(i, count + 0.1, str(count), ha='center', va='bottom', fontsize=12, rotation='vertical')
        # Annotate the second plot (idle time for each error)
        for i, idle_time in enumerate(df.groupby('NAME DESCRIPTION')['IDLE TIME (s)'].sum()):
            ax2.text(i + bar_width, idle_time + 7, str(idle_time), ha='center', va='bottom', fontsize=12, rotation='vertical')
        # Combine legends from both plots
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')
        ax.set_title('Machine Idle Occurrence Count and Idle Time',fontsize=24)
        ax.set_xlabel('Alarm Type',fontsize=16)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
def speed(csv_file_speed, ax):
   
    
        data = pd.read_csv(csv_file_speed)
        data['DATE/TIME'] = pd.to_datetime(data['DATE/TIME'], format='%d:%m:%Y/%H:%M:%S')
        data['Cones_per_hour'] = 18 * 3600 / data[' BOX TIME']
        mask = data['Cones_per_hour'] <= 1000
        # Create a new array for 'TIME' that corresponds to the mask
        filtered_time = data['DATE/TIME'][mask]
        # Create a new array for 'Cones_per_hour' that corresponds to the mask
        filtered_cones_per_hour = data['Cones_per_hour'][mask]
        # Plot the filtered data
        ax.plot(filtered_time, filtered_cones_per_hour, marker='o', linestyle='None', color='blue')
        ax.set_title('Cones Production Rate per Hour', fontsize=24)
        ax.set_xlabel('Time of the Day (in Hr)', fontsize=20)
        ax.set_ylabel('Packing Speed', fontsize=20)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        date_format = mdates.DateFormatter('%H')
        ax.xaxis.set_major_formatter(date_format)
        ax.tick_params(axis='x', colors='black', labelsize=16)
        ax.tick_params(axis='y', colors='black', labelsize=16)
def speed_dist_1(csv_file_speed,ax):
    # Read the CSV file into a Pandas DataFrame, using a comma as the separator
    data = pd.read_csv(csv_file_speed)
    
    # Convert the 'TIME' column to datetime format
    data['DATE/TIME'] = pd.to_datetime(data['DATE/TIME'], format='%d:%m:%Y/%H:%M:%S')
   
    # Calculate the packaging speed in cones per hour for the selected mode
    data['Cones_per_hour'] = 18 * 3600 / data[' BOX TIME']

    print(data)

    
    # Define bin edges for the histogram
    bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,1100, float('inf')]
    
    # Create a histogram of packaging speeds with specified bins
    ax.hist(data['Cones_per_hour'], bins=bins, color='blue', edgecolor='black')
    
    # Set the title, x-axis label, and y-axis label for the plot
    ax.set_title('Packing Speed Distribution for Boxes', fontsize=30)
    ax.set_xlabel('Packaging Speed (Cones per Hour)', fontsize=24)
    ax.set_ylabel('No of Boxes', fontsize=24)
    
    # Set the x-axis to display major tick marks at specified intervals using ticker.MultipleLocator
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=100))
    ax.tick_params(axis='x', colors='black', labelsize=20)
    ax.tick_params(axis='y', colors='black', labelsize=20)    
def speed_dist_2(csv_file_speed,ax):
    # Read the CSV file into a Pandas DataFrame, using a comma as the separator
    data = pd.read_csv(csv_file_speed)
    
    # Convert the 'TIME' column to datetime format
    data['DATE/TIME'] = pd.to_datetime(data['DATE/TIME'], format='%d:%m:%Y/%H:%M:%S')
    
    data = data[data[' Mode Select '].str.strip() == 'Pallet']

    # Calculate the packaging speed in cones per hour for the selected mode
    data['Cones_per_hour'] = 18 * 3600 / data[' BOX TIME']
    
    # Define bin edges for the histogram
    bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,1100, float('inf')]
    
    # Create a histogram of packaging speeds with specified bins
    ax.hist(data['Cones_per_hour'], bins=bins, color='blue', edgecolor='black')
    
    # Set the title, x-axis label, and y-axis label for the plot
    ax.set_title('Packing Speed Distribution for Pallet', fontsize=30)
    ax.set_xlabel('Packaging Speed (Pallet per Hour)', fontsize=24)
    ax.set_ylabel('No of Pallet', fontsize=24)
    
    # Set the x-axis to display major tick marks at specified intervals using ticker.MultipleLocator
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=100))
    ax.tick_params(axis='x', colors='black', labelsize=20)
    ax.tick_params(axis='y', colors='black', labelsize=20)
def entry(csv_file_speed):
        # Read the CSV file into a Pandas DataFrame
    data = pd.read_csv(csv_file_speed)

    # Get the number of rows
    num_rows = data.shape[0]

    return num_rows
def net_wt(csv_file_speed):
    df = pd.read_csv(csv_file_speed)

    # Round the 'ACT NET WT' column to 2 decimal places
    df['ACT NET WT'] = df['ACT NET WT'].round(2)


    # Filter rows with 'Pallet' in the MODE column
    pallet_data = df[df[' Mode Select '] == ' Pallet  ']

    # Filter rows with '18 Box' in the MODE column
    box_data = df[(df[' Mode Select '] == ' 18Box ')]


    # Calculate the sum of (ACT NET WT * NO OF CONES) for Pallet and 18 Box separately
    pallet_net_wt_sum = (pallet_data['ACT NET WT']).sum()
    box_net_wt_sum = (box_data['ACT NET WT']).sum()

    pallet_wt = pallet_net_wt_sum.round(2)
    box_wt = box_net_wt_sum.round(2)

    

    return pallet_wt, box_wt
def check_error_file(csv_file_error):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_error)
    # Check the "IDLE START" time of the first row
    first_row_idle_start = df.loc[0, 'IDLE START']
    # Check if it begins with "00:00:00" and delete the row if it doesn't
    if not first_row_idle_start.startswith('00:00:00'):
        df.drop(0, inplace=True)
    # Get the directory and base name of the original CSV file
    output_directory = os.path.dirname(csv_file_error)
    output_basename = os.path.basename(csv_file_error)
    # Create the path for the modified CSV file with the same name
    output_file = os.path.join(output_directory, output_basename)
    # Save the modified DataFrame to the new CSV file with the same name
    df.to_csv(output_file, index=False)
def check_idle_file(csv_file_reidle):
    df = pd.read_csv(csv_file_reidle)
    first_row_idle_start = df.loc[0, 'IDLE START']
    if not first_row_idle_start.startswith('00:00:00'):
        df.drop(0, inplace=True)
    output_directory = os.path.dirname(csv_file_reidle)
    output_basename = os.path.basename(csv_file_reidle)
    output_file = os.path.join(output_directory, output_basename)
    df.to_csv(output_file, index=False)



user_date = input("Enter the date in the format DD_MM_YYYY:")
csv_file_error =  f"lagnam/rswm/rswm/AlarmIdle_07_11_2023.csv"
csv_file_reidle = f"lagnam/rswm/rswm/MachineIdle_07_11_2023.csv"
csv_file_speed = f"lagnam/rswm/rswm/ProductionData_07_11_2023.csv"
#check_error_file(csv_file_error)
#check_idle_file(csv_file_reidle)
fig, ax = plt.subplots(figsize=(21, 29.7))
box  = entry(csv_file_speed)
pallete_wt , box_wt = net_wt(csv_file_speed)
total_error , total_reidle = production(csv_file_speed, csv_file_error,csv_file_reidle,ax)
ax.set_title('Number of Cones Packaged, Alarm Idle Time and Machine Idle Time', fontsize = 24)
ax.set_xlabel('Time of the Day (in Hr)', fontsize = 18)
ax.set_ylabel('No of Cones Packaged', fontsize = 18)
ax.set_xticks(np.arange(24))
ax.set_xticklabels(np.arange(24))
ax.legend(loc='upper left')
fig_additional_1, ax_additional_1 = plt.subplots(figsize=(21, 10))
fig_additional_2, ax_additional_2 = plt.subplots(figsize=(21, 30.5))
fig_additional_3, ax_additional_3 = plt.subplots(figsize=(21, 29.7))
fig_additional_7, ax_additional_7 = plt.subplots(figsize=(21, 29.7))
fig_additional_4, ax_additional_4 = plt.subplots(figsize=(21, 29.7))
fig_additional_5, ax_additional_5 = plt.subplots(figsize=(21, 30))
speed(csv_file_speed,ax_additional_1)
plot_error_occurrence_idle(csv_file_error,ax_additional_2)
speed_dist_1(csv_file_speed,ax_additional_3)
speed_dist_2(csv_file_speed,ax_additional_7)
plot_reidle_occurrence_idle(csv_file_reidle,ax_additional_4)
plt.subplots_adjust(hspace= -0.1)
table_data = [
["Total Boxes packed", f"{box} boxes"],
["Total Pallets packed", f"0 cones"],
["Total Alarm Idle time", f"{total_error} seconds"],
["Total Machine Idle time",f"{total_reidle} seconds"],
["Total Box Weight",f"{box_wt} kg"],
["Total Pallet Weight",f"{pallete_wt} kg"]]
table = ax_additional_5.table(cellText=table_data, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(18)
table.scale(1, 4) 
ax_additional_5.axis('off')
ax_additional_5.text(0.25, 1, "INDOTEXNOLOGY PVT LIMITED", fontsize=40)
ax_additional_5.text(0.26, 0.90, f"RSWM REPORT - {user_date}", fontsize=35)


pdf_file = f'RSWM_ACP_REPORT_{user_date}.pdf'
with PdfPages(pdf_file) as pdf_pages:
    pdf_pages.savefig(fig_additional_5)
    pdf_pages.savefig(fig_additional_3)
    #pdf_pages.savefig(fig_additional_7)
    pdf_pages.savefig(fig)
    pdf_pages.savefig(fig_additional_1)
    pdf_pages.savefig(fig_additional_2)
    pdf_pages.savefig(fig_additional_4)


