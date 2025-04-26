#!/usr/bin/env python3
import requests
import json

def test_api_endpoint():
    try:
        response = requests.get("http://localhost:5000/api/cycle_analytics")
        if response.status_code == 200:
            data = response.json()
            print("API responde correctamente")
            print("Datos recibidos:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: Código de respuesta {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        return False

if __name__ == "__main__":
    print("Probando endpoint de API...")
    test_api_endpoint() 