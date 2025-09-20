from db import Base, engine
from models.user import User

print("📦 Criando tabelas no banco...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")