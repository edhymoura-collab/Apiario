from src.config.database import database


async def seed_sample_data() -> None:
    if await database.count("colmeias") == 0:
        await database.insert("colmeias", {
            "codigo": "C-001",
            "nome": "Colmeia Norte 01",
            "localizacao": "Setor A",
            "status": "ativa",
            "observacoes": "Colmeia ativa e monitorada",
        })

    if await database.count("lotes") == 0:
        await database.insert("lotes", {
            "codigo_lote": "LOT-001",
            "variedade_florada": "Eucalipto",
            "data_extracao": "2026-10-18",
            "umidade": 17.5,
            "pureza": 98.2,
            "quantidade_potes": 120,
            "laboratorio": "Laboratório de Qualidade",
            "storytelling": "Mel premium e rastreável",
            "auditado": True,
        })
