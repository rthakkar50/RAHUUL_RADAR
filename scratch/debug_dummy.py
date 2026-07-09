from core.master_signal_pipeline import MasterSignalPipeline
from tests.test_master_signal_pipeline import DummyEngine, FaultyEngine

import builtins
orig_hasattr = builtins.hasattr

def debug_hasattr(obj, name):
    print(f"hasattr({obj}, '{name}') called")
    return orig_hasattr(obj, name)

builtins.hasattr = debug_hasattr

engines = {
    'trend': DummyEngine('BULL'),
    'momentum': FaultyEngine(),
    'volume': DummyEngine('HIGH')
}
pipeline = MasterSignalPipeline(engines=engines)
results = pipeline.collect_results(symbol='RELIANCE')
print(results)
