"""
Guitar Fretboard Visualizer - Aplicativo web em Python para visualizar notas no braço da guitarra
"""
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Definição das notas musicais
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Definição da afinação padrão da guitarra (do agudo para o grave)
STANDARD_TUNING = ['E', 'B', 'G', 'D', 'A', 'E']

# Quantidade de trastes a serem exibidos
FRETS = 12

# Definição dos nomes dos intervalos
INTERVAL_NAMES = {
    0: '1P', # Primeira Justa/Uníssono
    1: '2m', # Segunda menor
    2: '2M', # Segunda Maior
    3: '3m', # Terça menor
    4: '3M', # Terça Maior
    5: '4P', # Quarta Justa
    6: 'Tr', # Trítono
    7: '5P', # Quinta Justa
    8: '6m', # Sexta menor
    9: '6M', # Sexta Maior
    10: '7m', # Sétima menor
    11: '7M', # Sétima Maior
}

def get_fretboard_notes():
    """Gera as notas em todas as posições do braço da guitarra"""
    fretboard = []
    
    for string_idx, open_note in enumerate(STANDARD_TUNING):
        string = []
        open_note_idx = NOTES.index(open_note)
        
        for fret in range(FRETS + 1):  # +1 para incluir o traste 0 (corda solta)
            note_idx = (open_note_idx + fret) % len(NOTES)
            note = NOTES[note_idx]
            string.append({
                'note': note,
                'string': string_idx + 1,  # String numbers start from 1
                'fret': fret
            })
            
        fretboard.append(string)
    
    return fretboard

def get_fretboard_with_intervals(root):
    """Gera notas e intervalos em todas as posições do braço da guitarra"""
    fretboard = []
    root_idx = NOTES.index(root)
    
    for string_idx, open_note in enumerate(STANDARD_TUNING):
        string = []
        open_note_idx = NOTES.index(open_note)
        
        for fret in range(FRETS + 1):
            note_idx = (open_note_idx + fret) % len(NOTES)
            note = NOTES[note_idx]
            
            # Calcular o intervalo em relação à nota raiz
            interval = (note_idx - root_idx) % len(NOTES)
            interval_name = INTERVAL_NAMES[interval]
            
            string.append({
                'note': note,
                'string': string_idx + 1,
                'fret': fret,
                'interval': interval,
                'interval_name': interval_name
            })
            
        fretboard.append(string)
    
    return fretboard

def get_scale_notes(root, scale_type='major'):
    """Retorna as notas de uma escala baseada na nota raiz e tipo"""
    root_idx = NOTES.index(root)
    
    # Intervalos em semitons para diferentes tipos de escalas
    intervals = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic_major': [0, 2, 4, 7, 9],
        'pentatonic_minor': [0, 3, 5, 7, 10],
        'blues': [0, 3, 5, 6, 7, 10]
    }
    
    if scale_type not in intervals:
        scale_type = 'major'
    
    scale_notes = []
    scale_intervals = []
    
    for interval in intervals[scale_type]:
        note_idx = (root_idx + interval) % len(NOTES)
        scale_notes.append(NOTES[note_idx])
        scale_intervals.append({
            'interval': interval,
            'interval_name': INTERVAL_NAMES[interval],
            'note': NOTES[note_idx]
        })
    
    return {
        'notes': scale_notes,
        'intervals': scale_intervals
    }

def get_chord_notes(root, chord_type='major'):
    """Retorna as notas de um acorde baseado na nota raiz e tipo"""
    root_idx = NOTES.index(root)
    
    # Intervalos em semitons para diferentes tipos de acordes
    intervals = {
        'major': [0, 4, 7],
        'minor': [0, 3, 7],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8],
        '7': [0, 4, 7, 10],
        'maj7': [0, 4, 7, 11],
        'm7': [0, 3, 7, 10],
        'm7b5': [0, 3, 6, 10]
    }
    
    if chord_type not in intervals:
        chord_type = 'major'
    
    chord_notes = []
    chord_intervals = []
    
    for interval in intervals[chord_type]:
        note_idx = (root_idx + interval) % len(NOTES)
        chord_notes.append(NOTES[note_idx])
        chord_intervals.append({
            'interval': interval,
            'interval_name': INTERVAL_NAMES[interval],
            'note': NOTES[note_idx]
        })
    
    return {
        'notes': chord_notes,
        'intervals': chord_intervals
    }

def get_all_triads(root):
    """Retorna todos os quatro tipos básicos de tríades para uma nota raiz"""
    triads = {}
    
    for triad_type in ['major', 'minor', 'dim', 'aug']:
        chord_data = get_chord_notes(root, triad_type)
        triads[triad_type] = {
            'notes': chord_data['notes'],
            'intervals': chord_data['intervals']
        }
    
    return triads

def get_scale_triads(root, scale_type='major'):
    """Retorna as tríades de acordes formadas a partir de uma escala"""
    scale_data = get_scale_notes(root, scale_type)
    scale_notes = scale_data['notes']
    triads = []
    
    # Obtém o tipo de cada tríade baseado na escala
    triad_types = []
    if scale_type == 'major':
        triad_types = ['major', 'minor', 'minor', 'major', 'major', 'minor', 'dim']
    elif scale_type == 'minor':
        triad_types = ['minor', 'dim', 'major', 'minor', 'minor', 'major', 'major']
    else:
        # Para outros tipos de escala, determinamos os tipos de tríade baseado nos intervalos
        scale_degrees = len(scale_notes)
        for i in range(scale_degrees):
            # Pega a nota raiz e as notas a 2 e 4 posições (em escala diatônica seria terça e quinta)
            root_note = scale_notes[i]
            third_idx = (i + 2) % scale_degrees
            fifth_idx = (i + 4) % scale_degrees
            
            third_note = scale_notes[third_idx]
            fifth_note = scale_notes[fifth_idx]
            
            # Calcula os intervalos para determinar o tipo de tríade
            root_idx = NOTES.index(root_note)
            third_idx = NOTES.index(third_note)
            fifth_idx = NOTES.index(fifth_note)
            
            third_interval = (third_idx - root_idx) % 12
            fifth_interval = (fifth_idx - root_idx) % 12
            
            # Determina o tipo de tríade
            if third_interval == 4 and fifth_interval == 7:
                triad_types.append('major')
            elif third_interval == 3 and fifth_interval == 7:
                triad_types.append('minor')
            elif third_interval == 3 and fifth_interval == 6:
                triad_types.append('dim')
            elif third_interval == 4 and fifth_interval == 8:
                triad_types.append('aug')
            else:
                # Para casos onde não temos uma tríade clássica
                triad_types.append('unknown')
    
    # Constrói as tríades
    for i, note in enumerate(scale_notes):
        if i < len(triad_types):
            triad_type = triad_types[i]
            chord_data = get_chord_notes(note, triad_type)
            
            triads.append({
                'root': note,
                'type': triad_type,
                'notes': chord_data['notes'],
                'intervals': chord_data['intervals'],
                'degree': i + 1  # Grau da escala (1-7)
            })
    
    return triads

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fretboard')
def fretboard():
    return jsonify(get_fretboard_notes())

@app.route('/api/fretboard-intervals')
def fretboard_intervals():
    root = request.args.get('root', 'C')
    
    if root not in NOTES:
        root = 'C'
    
    return jsonify(get_fretboard_with_intervals(root))

@app.route('/api/scale')
def scale():
    root = request.args.get('root', 'C')
    scale_type = request.args.get('type', 'major')
    
    if root not in NOTES:
        root = 'C'
    
    return jsonify(get_scale_notes(root, scale_type))

@app.route('/api/chord')
def chord():
    root = request.args.get('root', 'C')
    chord_type = request.args.get('type', 'major')
    
    if root not in NOTES:
        root = 'C'
    
    return jsonify(get_chord_notes(root, chord_type))

@app.route('/api/scale-triads')
def scale_triads():
    root = request.args.get('root', 'C')
    scale_type = request.args.get('type', 'major')
    
    if root not in NOTES:
        root = 'C'
    
    return jsonify(get_scale_triads(root, scale_type))

@app.route('/api/all-triads')
def all_triads():
    root = request.args.get('root', 'C')
    
    if root not in NOTES:
        root = 'C'
    
    return jsonify(get_all_triads(root))

if __name__ == '__main__':
    # Obter a porta definida pelo Heroku ou usar 5000 como padrão
    port = int(os.environ.get("PORT", 5000))
    # Definir host como 0.0.0.0 para Heroku
    app.run(host='0.0.0.0', port=port)