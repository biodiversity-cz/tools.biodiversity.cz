from flask import Flask, request, render_template, send_file
from demusExporter.process_file import process_uploaded_file

import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        export_type = request.form["type"]
        if uploaded_file.filename == "":
            return "Žádný soubor nebyl vybrán"

        input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        output_filename = uploaded_file.filename.rsplit(".", 1)[0] + "_" + export_type + "output.xlsx"
        output_path = os.path.join(RESULT_FOLDER, output_filename)

        uploaded_file.save(input_path)
        process_uploaded_file(input_path, output_path, export_type)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)