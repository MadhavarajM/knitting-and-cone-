import psycopg2
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib import colors
from io import BytesIO
from PIL import Image as PilImage
import os

# Get user input for the desired date
user_date = input("Enter the date (YYYY-MM-DD): ")

# Establish a connection to the PostgreSQL database
try:
    conn = psycopg2.connect(
        host="localhost", database="knitting", user="postgres", password="55555"
    )

    # Define your SQL query with the user-provided date
    query = f"""
    SELECT dd.defect_id, dd.file_path, dd.filename, TO_CHAR(dd.timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, dd.coordinate, dt.defect_name
    FROM defect_details AS dd
    INNER JOIN alarm_status AS a ON dd.defect_id = a.defect_id
    INNER JOIN defect_type AS dt ON dd.defecttyp_id = dt.defecttyp_id
    WHERE DATE(dd.timestamp) = '{user_date}';
    """

    # Use pandas to read the data directly into a DataFrame
    df = pd.read_sql_query(query, conn)

    df.sort_values(by=['formatted_timestamp'], ascending=[True], inplace=True)

    columns_to_drop = ['defect_id', 'coordinate']
    filtered_df = df.drop(columns_to_drop, axis=1)

    # Split the formatted_timestamp column into separate date and time columns
    date_time_split = filtered_df['formatted_timestamp'].str.split(' ', expand=True)
    filtered_df['Date'] = date_time_split[0]
    filtered_df['Time'] = date_time_split[1]
    filtered_df.drop('formatted_timestamp', axis=1, inplace=True)

    # Sort the DataFrame by 'Date', 'Time', and 'Defect_name' columns
    filtered_df.sort_values(by=['Date', 'Time', 'defect_name'], ascending=[True, True, True], inplace=True)
    filtered_df = filtered_df[['Date', 'Time', 'defect_name', 'filename', 'file_path']]

    # Create a PDF document
    pdf_buffer = BytesIO()
    pdf_title = f"Alarm Log for {user_date}"  # Set the PDF title dynamically
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, title=pdf_title)
    elements = []

    static_path = "/home/kniti/projects/knit-i/knitting-core" 
    for _, row in filtered_df.iterrows():
        # Create a table for the new page with the desired columns (excluding file_path and filename)
        table_data = [row[['Date', 'Time', 'defect_name']].tolist()]  # Table row
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))  # Add space after the table

        file_path = row['file_path'].strip("/")  # Remove leading/trailing slashes
        filename = row['filename']  # Get the filename from the current row
        full_file_path = os.path.normpath(os.path.join(static_path, file_path))
        print(full_file_path)
        for root, dirs, files in os.walk(full_file_path):
            for file in files:
                if file == filename:
                    image_path = os.path.join(root, file)  # Construct the full image path

                    try:
                        pil_image = PilImage.open(image_path)
                        pil_image.thumbnail((200, 200))  # Resize the image as needed
                        img = Image(image_path, 450, 255)  # Use the full image path
                        elements.append(img)
                        elements.append(Spacer(1, 12))  # Add space after the image
                    except Exception as e:
                        print(f"Error loading image at {image_path}: {e}")
    # Build the PDF document
    doc.build(elements)

    # Save the PDF to a file
    pdf_filename = f'log_report/KPT_MACHINE1_Alarm_Log_{user_date}.pdf'  # Set the PDF filename dynamically
    with open(pdf_filename, 'wb') as f:
        f.write(pdf_buffer.getvalue())
        print(f"PDF saved as {pdf_filename}")

except (Exception, psycopg2.Error) as error:
    import traceback
    traceback.print_exc()
    print("Error connecting to the database:", error)
