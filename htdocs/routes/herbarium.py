from flask import Response, Flask, request, render_template, send_file, Blueprint, jsonify, current_app, url_for, redirect, flash
from demusexporter.process_file import process_uploaded_file as demus_process
from museionexporter.process_file import process_uploaded_file as museion_process
from slide_label_generator.process_file import process_uploaded_file as slide_label_process
from museionexporter.exportTypes import ExportTypes
from werkzeug.utils import secure_filename
from io import BytesIO
from barcode import Code39
from barcode.writer import ImageWriter
from PIL import Image
import os

herbarium_bp = Blueprint('herbarium', __name__)

@herbarium_bp.route("/demusConvertor", methods=["GET", "POST"])
def demus():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        export_type = request.form["type"]
        dwc_description = request.form["dwc_description"]
        dwc_rights = request.form["dwc_rights"]

        if uploaded_file.filename == "":
            return "Žádný soubor nebyl vybrán"

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        name_part = filename.rsplit(".", 1)[0]
        output_filename = f"{name_part}_{export_type}_output"
        uploaded_file.save(input_path)

        if export_type == ExportTypes.DWC.value:
            output_filename += ".zip"
            output_mime = 'application/zip'
        else:
            output_filename += ".xlsx"
            output_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        output_path = os.path.join(current_app.config['RESULT_FOLDER'], output_filename)

        try:
            demus_process(input_path, output_path, export_type, dwc_description, '', '', dwc_rights)
            return stream_file(output_path, output_filename, output_mime)
        except Exception as e:
            current_app.logger.exception("Chyba při zpracování souboru")
            flash(f"Chyba při zpracování souboru: {str(e)}", "error")
            return redirect(request.url)
        finally:
            for path in (input_path, output_path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as cleanup_err:
                    current_app.logger.warning(f"Soubor {path} se nepodařilo smazat: {cleanup_err}")

    return render_template("herbarium/demusConvertor.html")

@herbarium_bp.route("/museionConvertor", methods=["GET", "POST"])
def museion():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        export_type = request.form["type"]
        dwc_description = request.form["dwc_description"]
        dwc_rights = request.form["dwc_rights"]

        if uploaded_file.filename == "":
            return "Žádný soubor nebyl vybrán"

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        name_part = filename.rsplit(".", 1)[0]
        output_filename = f"{name_part}_{export_type}_output"
        uploaded_file.save(input_path)

        if export_type == ExportTypes.DWC.value:
            output_filename += ".zip"
        else:
            output_filename += ".xlsx"

        output_path = os.path.join(current_app.config['RESULT_FOLDER'], output_filename)
        try:
            museion_process(input_path, output_path, export_type, dwc_description, '', '', dwc_rights)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            current_app.logger.exception("Chyba při zpracování souboru")
            flash(f"Chyba při zpracování souboru: {str(e)}", "error")
            return redirect(request.url)
        finally:
            for path in (input_path, output_path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as cleanup_err:
                    current_app.logger.warning(f"Soubor {path} se nepodařilo smazat: {cleanup_err}")

    return render_template("herbarium/museionConvertor.html")

@herbarium_bp.route("/slideLabels", methods=["GET", "POST"])
def slide_label():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return "Žádný soubor nebyl vybrán"

        # Načtení marginů z formuláře (jsou čísla)
        try:
            margin_top = int(request.form.get("marginTop", 15))
            margin_bottom = int(request.form.get("marginBottom", 15))
            margin_left = int(request.form.get("marginLeft", 10))
            margin_right = int(request.form.get("marginRight", 10))
            space_x = int(request.form.get("space_x", 1))
            space_y = int(request.form.get("space_y", 1))
        except ValueError:
            return "Neplatná hodnota marginu nebo paddingu"

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        name_part = filename.rsplit(".", 1)[0]
        output_filename = f"{name_part}_output"
        uploaded_file.save(input_path)

        output_filename += ".pdf"

        output_path = os.path.join(current_app.config['RESULT_FOLDER'], output_filename)
        try:
            slide_label_process(
                input_path,
                output_path,
                margin_top=margin_top,
                margin_bottom=margin_bottom,
                margin_left=margin_left,
                margin_right=margin_right,
                space_x=space_x,
                space_y=space_y
            )
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            current_app.logger.exception("Chyba při zpracování souboru")
            flash(f"Chyba při zpracování souboru: {str(e)}", "error")
            return redirect(request.url)
        finally:
            for path in (input_path, output_path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as cleanup_err:
                    current_app.logger.warning(f"Soubor {path} se nepodařilo smazat: {cleanup_err}")

    return render_template("herbarium/slideLabels.html")

@herbarium_bp.route("/barcodeGenerator", methods=["GET"])
def barcodeGenerator():
        title = request.args.get("title","")
        subtitle = request.args.get("subtitle","")
        prefix = request.args.get("prefix","")
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)

        query_params = {k: v for k, v in {
            "title": title,
            "subtitle": subtitle,
            "prefix": prefix,
            "start": start,
            "end": end
        }.items() if v is not None}

        values = []
        if start is not None and end is not None and prefix is not None:
            values = [f"{prefix} {i}" for i in range(start, end + 1)]

        return render_template(
            "herbarium/barcodeGenerator.html",
            title=title,
            subtitle=subtitle,
            prefix=prefix,
            start=start if start is not None else "",
            end=end if end is not None else "",
            queryParams=query_params,
            values=values)

@herbarium_bp.route("/barcode/<path:text>")
def barcode(text):
    if not text:
        img = Image.new("RGB", (1, 20), color=(255, 255, 255))
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "max-age=86400"})

    barcode = Code39(
        text,
        writer=ImageWriter(),
        add_checksum=False
    )

    options = {
        "module_width": 0.2,
        "module_height": 5.0,
        "write_text": False,
        "text_distance": 0,
        "quiet_zone": 0.8
    }

    buf = BytesIO()
    barcode.write(buf, options=options)
    buf.seek(0)

    return Response(buf.getvalue(), mimetype="image/png", headers={"Cache-Control": "max-age=86400"})

def stream_file(path, filename=None, mimetype="text/csv"):
    def generate():
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(1024 * 1024)  # 1 MB
                if not chunk:
                    break
                yield chunk

    headers = {}
    if filename:
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return Response(
        generate(),
        mimetype=mimetype,
        headers=headers,
    )