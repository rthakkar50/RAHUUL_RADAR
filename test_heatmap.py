from ui.heatmap import HeatmapWorker
from PySide6.QtCore import QCoreApplication
import sys

app = QCoreApplication(sys.argv)

def on_finished(res):
    print("Finished:", res)
    app.quit()
    
def on_error(err):
    print("Error:", err)
    app.quit()

worker = HeatmapWorker(["^CNXIT", "^CNXAUTO"])
worker.finished.connect(on_finished)
worker.error.connect(on_error)
worker.run()
app.exec()
