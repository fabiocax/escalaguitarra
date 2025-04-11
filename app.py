"""
Aplicativo Flask mínimo para servir o Visualizador de Braço de Guitarra
"""
from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    return {
        'env': dict(os.environ),
        'routes': [str(rule) for rule in app.url_map.iter_rules()]
    }
if __name__ == '__main__':
    # Obtém a porta do ambiente ou usa 5000 como padrão
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
