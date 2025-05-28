from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import math

app = Flask(__name__)
CORS(app)

def distancia(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def evalua_ruta(ruta, coord):
    total = 0
    for i in range(len(ruta) - 1):
        total += distancia(coord[ruta[i]], coord[ruta[i + 1]])
    total += distancia(coord[ruta[-1]], coord[ruta[0]])
    return total

def busqueda_tabu(ruta_inicial, coord, max_iteraciones, tamanio_tabu):
    estado_actual = ruta_inicial[:]
    mejor_estado = estado_actual[:]
    mejor_valor = evalua_ruta(mejor_estado, coord)

    lista_tabu = []
    historial = []

    for iteracion in range(max_iteraciones):
        vecinos = []

        # Generar vecinos intercambiando dos ciudades (excepto la ciudad de inicio)
        for _ in range(50):  # Número de vecinos por iteración
            i, j = random.sample(range(1, len(estado_actual)), 2)
            vecino = estado_actual[:]
            vecino[i], vecino[j] = vecino[j], vecino[i]
            movimiento = (min(i, j), max(i, j))  # Representar el cambio
            if movimiento not in lista_tabu:
                vecinos.append((vecino, movimiento))

        # Si no hay vecinos válidos, se detiene
        if not vecinos:
            break

        # Escoger el mejor vecino que no esté en la lista tabú
        mejor_vecino = None
        mejor_vecino_valor = float('inf')

        for vecino, movimiento in vecinos:
            valor = evalua_ruta(vecino, coord)
            if valor < mejor_vecino_valor:
                mejor_vecino = (vecino, movimiento)
                mejor_vecino_valor = valor

        # Actualizar estado actual
        estado_actual = mejor_vecino[0]

        # Actualizar lista tabú
        lista_tabu.append(mejor_vecino[1])
        if len(lista_tabu) > tamanio_tabu:
            lista_tabu.pop(0)

        # Actualizar mejor solución
        if mejor_vecino_valor < mejor_valor:
            mejor_estado = estado_actual[:]
            mejor_valor = mejor_vecino_valor

        historial.append({'iteracion': iteracion + 1, 'distancia': round(mejor_vecino_valor, 4)})

    return mejor_estado, historial

@app.route('/resolver-tsp', methods=['POST'])
def resolver_tsp():
    try:
        data = request.get_json()

        ciudades = data['ciudades']
        origen = data['origen']
        iteraciones = int(data['iteraciones'])  # nuevo parámetro
        tamanio_tabu = int(data['tamano_tabu'])  # nuevo parámetro

        if origen not in ciudades:
            return jsonify({"error": "La ciudad de origen no está en el diccionario de ciudades."}), 400

        ruta = list(ciudades.keys())
        ruta.remove(origen)
        random.shuffle(ruta)
        ruta = [origen] + ruta

        ruta_final, historial = busqueda_tabu(ruta, ciudades, iteraciones, tamanio_tabu)
        distancia_final = evalua_ruta(ruta_final, ciudades)

        return jsonify({
            'ruta': ruta_final,
            'distancia': round(distancia_final, 4),
            'historial': historial
        })

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
