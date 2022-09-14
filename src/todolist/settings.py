from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    # server_host: str = '192.168.0.4'
    server_port: int = 8000
    database_url: str = 'sqlite:///./todolist.db'

    jwt_secret: str
    jwt_algorithm: str = 'HS256'

    static_dir: str = 'src/todolist/static'


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
