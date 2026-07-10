from scanner.scanner_engine import ScannerEngine
import inspect

se = ScannerEngine(None, None, None, None, None)
print(inspect.getfile(se.decision_engine.__class__))
