from flask import Flask, request, jsonify, render_template, send_from_directory,send_file, redirect, session, url_for
import os
import csv
import uuid
import zipfile
import shutil
from zipfile import ZipFile
import re
import tempfile
import io
import atexit
import time

app = Flask(__name__)

global_user_input = None

# Specify the folder where uploaded files will be saved
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Specify the folder where generated HTML files will be saved as "HTML files"
HTML_FOLDER = 'HTML files'
app.config['HTML_FOLDER'] = HTML_FOLDER


parsed_csv_data=[]

@app.route('/download_template_csv', methods=['GET'])
def download_template_csv():
    try:
        # Path to your template CSV file
        template_csv_path = 'template.csv'
        
        # Set the Content-Disposition header for the download
        response = send_file(
            template_csv_path,
            as_attachment=True,
            download_name='template.csv'
        )

        return response
    except Exception as e:
        print(f"Error in download_template_csv: {str(e)}")
        return "Download failed.", 500


@app.route('/generate_and_download_xml', methods=['POST'])
def generate_and_download_xml():
    try:
        user_input = request.form.get('xml_user_input')

        # Check if user input is provided
        if not user_input:
            return "Please enter some words.", 400

        # Split the user input into a list of words (split by space, comma, or newline)
        words = re.split(r'[ ,\n]+', user_input)

        # Generate the dynamic part of the XML content based on the words
        dynamic_xml_content = "".join([f'<members>{word}</members>\n' for word in words])

        # Combine the static and dynamic parts to create the full XML content
        xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
<types>
{dynamic_xml_content}
<name>CustomLabel</name> 
</types> 
<types> 
<members>es</members>
<members>ar</members>
<name>Translations</name> 
</types>
<version>51.0</version>
</Package>"""

        
        
         # Create a temporary file to store the XML content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
            temp_file.write(xml_content.encode('utf-8'))
            temp_file_path = temp_file.name  # Get the file path

        # Send the temporary file to the client for download
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name='package.xml'
        )
        # Explicitly delete the temporary file after serving
        os.remove(temp_file_path)
    except Exception as e:
        print(f"Error in generate_and_download_xml: {str(e)}")
        return "Download failed.", 500
    #     # Specify the path where you want to save the generated XML file
    #     xml_output_path = 'generated_xml.xml'  # Replace with your desired directory and filename

    #     # Write the XML content to the .xml file
    #     with open(xml_output_path, 'w') as xml_file:
    #         xml_file.write(xml_content)

    #     # Send the .xml file to the client for download
    #     return send_file(xml_output_path, as_attachment=True)
    # except Exception as e:
    #     print(f"Error in generate_and_download_xml: {str(e)}")
    #     return "Download failed.", 500

# def cleanup():
#     try:
#         # Remove the ZIP file when the program exits
#         zip_file_path = 'downloaded_files.zip'
#         if os.path.exists(zip_file_path):
#             os.remove(zip_file_path)
#             print(f"ZIP file '{zip_file_path}' removed successfully.")
#         else:
#             print(f"ZIP file '{zip_file_path}' not found.")
#     except Exception as e:
#         print(f"Error during cleanup: {str(e)}")

# # Register the cleanup function to be called at exit
# atexit.register(cleanup)






@app.route('/download_zip', methods=['GET'])
def download_zip():
    try:
    #     # Create an in-memory ZIP file
    #     zip_buffer = io.BytesIO()

    #     # Create a ZIP archive in memory
    #     with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
    #         zipf.write('HTML files', 'HTML files')
    #         zipf.write('Article_details.csv', 'Article_details.csv')
    #         zipf.write('articleproperites.properties', 'articleproperites.properties')
    #         zipf.write('target.zip', 'target.zip')

    #     # Seek back to the beginning of the buffer before sending
    #     zip_buffer.seek(0)

    #     # Send the ZIP file to the client for download
    #     response = send_file(
    #         zip_buffer,
    #         as_attachment=True,
    #         download_name='downloaded_files.zip'  # Provide a custom download name
    #     )

    #     return response
    # except Exception as e:
    #     print(f"Error in download_zip: {str(e)}")
    #     return "Download failed.", 500
        # Create a folder to contain HTML files folder, new CSV file, and static files
        os.makedirs('downloaded_files', exist_ok=True)
        # Copy the HTML files folder to the downloaded_files folder
        shutil.copytree('HTML files', 'downloaded_files/HTML files')

        # Copy the new CSV file to the downloaded_files folder
        shutil.copy('Article_details.csv', 'downloaded_files/Article_details.csv')

        # Copy static files to the downloaded_files folder
        shutil.copy('target.zip', 'downloaded_files/target.zip')
        shutil.copy('articleproperites.properties', 'downloaded_files/articleproperites.properties')
        
        # Create a ZIP archive
        with ZipFile('downloaded_files.zip', 'w') as zipf:
            # Add the downloaded_files folder and its contents to the ZIP archive
            for root, dirs, files in os.walk('downloaded_files'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, 'downloaded_files')
                    zipf.write(file_path, arcname)

        # Send the ZIP file to the client for download without specifying the download location
        response = send_file('downloaded_files.zip', as_attachment=True,mimetype='application/zip',  # Explicitly set the MIME type to ZIP
)
         # Set the Content-Disposition header
        response.headers["Content-Disposition"] = f"attachment; filename=downloaded_files.zip"

        # Remove the downloaded_files folder and its contents from the source directory
        shutil.rmtree('downloaded_files')
        # Clean up: Delete 'Article_details.csv' and 'HTML files' folder
        os.remove('Article_details.csv')
        shutil.rmtree('HTML files')
        shutil.rmtree('uploads')
        #os.remove('downloaded_files.zip')
        
        



       
        return response
    except Exception as e:
        print(f"Error in download_zip: {str(e)}")
        return "Download failed. Click GO button first", 500



def process_structure(input_text):
    lines = input_text.strip().split("\n")
    html_content = []
    ul_stack = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r"^\d+\.", line):
            ul_level = len(re.findall(r"\d+\.", line))
            while ul_level < len(ul_stack):
                html_content.append("</ul>")
                ul_stack.pop()
            while ul_level > len(ul_stack):
                html_content.append("<ul>")
                ul_stack.append(ul_level)
            line = line.lstrip("1234567890. ").strip()
            html_content.append(f"<li>{line}</li>")
        else:
            while ul_stack:
                html_content.append("</ul>")
                ul_stack.pop()
            html_content.append(f"<p>{line}</p>")

    while ul_stack:
        html_content.append("</ul>")
        ul_stack.pop()

    return "\n".join(html_content)





def generate_and_save_html_files(data_folder):
    try:
        # Iterate through the parsed CSV data and generate HTML files
        for row in parsed_csv_data:
            if not os.path.exists(data_folder):
                os.makedirs(data_folder, exist_ok=True)
            
            # Generate a random filename using uuid
            random_filename = str(uuid.uuid4()) + ".html"

            # Create the full path to the HTML file
            html_file_path = os.path.join(data_folder, random_filename)

            # Save the HTML file path to the row data
            row['html_file_path'] = html_file_path.replace('\\','/')

            # Customize this part to generate HTML content based on the row data
            # For example, you can access row['column_name'] to get data from a specific column
            # and use it to construct HTML content.
            # Construct the HTML content as per your requirements.
            
            #content=row['Answer']
            # Generate HTML content with structured paragraphs, bullet points, and sub-bullet points
            if re.search(r'<\s*(?:html|p|span)', row['Answer'], re.IGNORECASE):
                # If the content already contains HTML tags, directly use it as the HTML content
                html_content = row['Answer']
            else:
                # Process the content to generate HTML
                content = row['Answer']
                # Generate HTML content with structured paragraphs, bullet points, and sub-bullet points
                html_content = process_structure(content)
            

            # Save the HTML content to the HTML file
            with open(html_file_path, 'w', encoding='utf-8-sig') as html_file:
                html_file.write(html_content)
    except Exception as e:
        print(f"Error in generate_and_save_html_files: {str(e)}")


@app.route('/')
def index():
    return render_template('index.html')


def generate_and_save_new_csv(parsed_csv_data):
    dcg_name = next((key for key in parsed_csv_data[0].keys() if key.startswith('datacategorygroup')), None)
    # Define custom headings for the new CSV file
    new_fieldnames = ['IsMasterLanguage', 'Article_Content__c', 'Footer_Content__c', 'Sequence__c', 'Title', dcg_name, 'Channels', 'Language']

    # Create a list to store rows for the new CSV file
    new_csv_data = []

    for row in parsed_csv_data:
       

        # Create a new row with custom headings and values
        new_row = {
            'IsMasterLanguage': row['IsMasterLanguage'],
            'Article_Content__c': row['html_file_path'],
            'Footer_Content__c': '',
            'Sequence__c': row['Sequence__c'],
            'Title': row['Title'],
            dcg_name: row[dcg_name],
            'Channels': 'application+sites+csp',
            'Language': row['Language'],
        }

        # Append the new row to the new_csv_data list
        new_csv_data.append(new_row)

    # Specify the path where you want to save the new CSV file
    new_csv_output_path = 'Article_details.csv'  # Replace with your desired directory and filename

    # Write the new CSV content to the file
    with open(new_csv_output_path, 'w', newline='', encoding='utf-8-sig') as new_csv_file:
        csv_writer = csv.DictWriter(new_csv_file, fieldnames=new_fieldnames)
        csv_writer.writeheader()  # Write the header row
        csv_writer.writerows(new_csv_data)  # Write the data rows

    print("New CSV file generated successfully in", new_csv_output_path)






@app.route('/upload', methods=['POST'])
def upload_file():
    global parsed_csv_data  # Access the global parsed CSV data
    try:
        csv_File = request.files.get('csv_File')
        #user_input = request.form.get('user_input')
        #global global_user_input
        #global_user_input=user_input

        # Check if both the CSV file and user input are provided
        if not csv_File:
            return "Please provide CSV File", 400

        # Save the uploaded CSV file to the specified folder
        if csv_File:
        # Ensure that the folder specified in UPLOAD_FOLDER exists by creating it if necessary
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            filename = os.path.join(app.config['UPLOAD_FOLDER'], csv_File.filename)
            csv_File.save(filename)
        
            # Parse the uploaded CSV file and store it in the global variable
            with open(filename, 'r', encoding='utf-8-sig') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                parsed_csv_data = list(csv_reader)
        # Process the CSV file and user input as needed
        # Here, you can add code to process the uploaded file and user input
        print(parsed_csv_data)
        
        html_folder = app.config['HTML_FOLDER']
        print(f"HTML folder path: {html_folder}")
        generate_and_save_html_files(html_folder)
        print(parsed_csv_data)
        # Call the function and pass parsed_csv_data as an argument
        generate_and_save_new_csv(parsed_csv_data)
        
        #download_zip()


        # Redirect to the download_zip endpoint to trigger the download
        return "Yo"
    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        return "Upload failed.", 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
    

# app.run(debug=True, use_reloader=False)

