from flask import Flask, request, render_template, send_file, Blueprint, jsonify, current_app
from demusExporter.process_file import process_uploaded_file
import os

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        export_type = request.form["type"]
        if uploaded_file.filename == "":
            return "Žádný soubor nebyl vybrán"

        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        output_filename = uploaded_file.filename.rsplit(".", 1)[0] + "_" + export_type + "output.xlsx"
        output_path = os.path.join(current_app.config['RESULT_FOLDER'], output_filename)

        uploaded_file.save(input_path)
        process_uploaded_file(input_path, output_path, export_type)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")
