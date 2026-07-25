from core.sector_rotation_engine import SectorRotationEngine
import logging

logging.basicConfig(level=logging.DEBUG)
engine = SectorRotationEngine()
print(engine.get_sector_data())
