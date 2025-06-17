from htdocs import create_app
import os

app = create_app()

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
