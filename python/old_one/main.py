from gui import AnalyzerGUI
from analysis import AnalysisCalculator

# 1. Tworzymy mózg (kalkulator)
analysis_calculator = AnalysisCalculator()

# 2. Tworzymy serce (GUI) i dajemy mu dostęp do mózgu
app = AnalyzerGUI(engine=analysis_calculator)

# 3. Odpalamy
app.run()
