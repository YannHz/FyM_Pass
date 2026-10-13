from pathlib import Path
import argparse
import ipaddress
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import ProxyHandler, build_opener
import webbrowser


def puerto_ocupado(direccion, puerto):
    try:
        with socket.create_connection((direccion, puerto), timeout=.5):
            return True
    except OSError:
        return False


def detectar_direccion_local():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as conexion:
            # consulta la ruta local sin enviar datos a la red
            conexion.connect(('192.0.2.1', 9))
            return conexion.getsockname()[0]
    except OSError:
        raise SystemExit('No se pudo detectar la IP. Conecta la laptop al Wi-Fi del teléfono o usa --red IP_PC.')


def iniciar():
    analizador = argparse.ArgumentParser(description='Iniciar API y web de FyM Pass. Ctrl+C detiene ambos servicios.')
    analizador.add_argument('--red', metavar='IP_PC', help='IPv4 privada de la PC o auto para detectar la dirección de la red actual')
    analizador.add_argument('--sin-navegador', action='store_true')
    opciones = analizador.parse_args()
    direccion = '127.0.0.1'
    if opciones.red:
        try:
            ip = ipaddress.IPv4Address(detectar_direccion_local() if opciones.red == 'auto' else opciones.red)
        except ipaddress.AddressValueError:
            analizador.error('Usa una IPv4 válida de esta PC en la red local.')
        if not ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified or ip.is_multicast:
            analizador.error('Usa la IPv4 privada de esta PC en la red local.')
        direccion = str(ip)
    raiz = Path(__file__).resolve().parent
    python = raiz / ('backend/.venv/Scripts/python.exe' if os.name == 'nt' else 'backend/.venv/bin/python')
    node = shutil.which('node')
    vite = raiz / 'web/node_modules/vite/bin/vite.js'
    faltantes = []
    if not python.exists():
        faltantes.append('el entorno virtual backend/.venv')
    if not node:
        faltantes.append('Node.js en PATH')
    if not vite.exists():
        faltantes.append('las dependencias web (npm --prefix web ci)')
    if not (raiz / 'backend/.env').is_file():
        faltantes.append('backend/.env configurado para MySQL')
    if faltantes:
        raise SystemExit('Falta: ' + '; '.join(faltantes) + '. Sigue la preparación del README.')
    if puerto_ocupado(direccion, 8000) or puerto_ocupado('127.0.0.1', 5173):
        raise SystemExit('Hay un servicio activo en 8000 o 5173. Cierra la instancia anterior antes de iniciar o cambiar de red.')
    entorno = os.environ.copy()
    entorno['FYM_API_URL'] = f'http://{direccion}:8000'
    registros = raiz / '.registros'
    registros.mkdir(exist_ok=True)
    servicios = [
        ('backend', [str(python), '-m', 'uvicorn', 'aplicacion.main:aplicacion', '--host', direccion, '--port', '8000']),
        ('web', [node, str(vite), '--host', '127.0.0.1', '--port', '5173', '--strictPort']),
    ]
    procesos, archivos = [], []
    try:
        for carpeta, comando in servicios:
            salida = (registros / f'{carpeta}.log').open('a', encoding='utf-8')
            archivos.append(salida)
            procesos.append(subprocess.Popen(comando, cwd=raiz / carpeta, env=entorno, stdout=salida, stderr=salida,
                stdin=subprocess.DEVNULL, start_new_session=os.name != 'nt',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0))
        limite = time.monotonic() + 30
        listo = False
        cliente = build_opener(ProxyHandler({}))
        while time.monotonic() < limite:
            if any(proceso.poll() is not None for proceso in procesos):
                raise RuntimeError('Un servicio no pudo iniciar. Revisa .registros/backend.log y web.log.')
            try:
                with cliente.open(f'http://{direccion}:8000/api/salud/base-datos', timeout=1) as respuesta:
                    salud = json.load(respuesta)
                with cliente.open('http://127.0.0.1:5173/api/salud', timeout=1) as respuesta:
                    api = json.load(respuesta)
                if salud.get('estado') == api.get('estado') == 'disponible':
                    listo = True
                    break
            except (OSError, ValueError):
                pass
            time.sleep(.3)
        if not listo:
            raise RuntimeError('No se completo el inicio. Comprueba MySQL, backend/.env y los archivos de .registros.')
        print('Web: http://127.0.0.1:5173')
        print(f'API / Flutter: http://{direccion}:8000')
        print('MySQL disponible. Mantén esta terminal abierta. Ctrl+C detiene API y web.')
        if not opciones.sin_navegador:
            webbrowser.open('http://127.0.0.1:5173')
        while all(proceso.poll() is None for proceso in procesos):
            time.sleep(.5)
        raise RuntimeError('Un servicio se detuvo. Revisa los archivos de .registros.')
    except KeyboardInterrupt:
        print('\nDeteniendo FyM Pass...')
    except RuntimeError as problema:
        raise SystemExit(str(problema))
    finally:
        for proceso in procesos:
            if proceso.poll() is None:
                proceso.terminate()
        for proceso in procesos:
            try:
                proceso.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proceso.kill()
                proceso.wait()
        for archivo in archivos:
            archivo.close()


if __name__ == '__main__':
    iniciar()
