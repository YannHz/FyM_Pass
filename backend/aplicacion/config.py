from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Configuracion(BaseSettings):
    clave_qr: str = ""
    cookie_segura: bool = False
    bd_host: str = "127.0.0.1"
    bd_puerto: int = 3306
    bd_usuario: str = "fym_pass"
    bd_clave: str = ""
    bd_nombre: str = "fym_pass"
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[1] / ".env", extra="ignore")

configuracion = Configuracion()
