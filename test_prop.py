from dataclasses import dataclass
@dataclass
class A:
    adjusted_score: float
    @property
    def total_score(self): return self.adjusted_score

a = A(50.0)
try:
    a.total_score = 60.0
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {type(e).__name__} {e}")
