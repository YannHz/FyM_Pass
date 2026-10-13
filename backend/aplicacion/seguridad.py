import base64
import hashlib
import hmac
import secrets


def generar_hash_clave(clave: str) -> str:
    sal = secrets.token_bytes(16)
    resumen = hashlib.scrypt(clave.encode(), salt=sal, n=16384, r=8, p=1)
    return "scrypt$" + base64.b64encode(sal).decode() + "$" + base64.b64encode(resumen).decode()


def verificar_clave(clave: str, valor: str) -> bool:
    try:
        algoritmo, sal, esperado = valor.split("$")
        if algoritmo != "scrypt":
            return False
        resumen = hashlib.scrypt(clave.encode(), salt=base64.b64decode(sal), n=16384, r=8, p=1)
        return hmac.compare_digest(resumen, base64.b64decode(esperado))
    except (ValueError, TypeError):
        return False


def resumir_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
