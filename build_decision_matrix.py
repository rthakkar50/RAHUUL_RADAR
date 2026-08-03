print("=== DECISION TRANSLATION MATRIX ===")
matrix = [
    ("ENTER NOW", "IntradayScannerService", "L551", "ENTER NOW | BUY", "Included in buys list (L557), sent to API & Flutter table"),
    ("RETEST FIRST", "IntradayScannerService", "L551", "RETEST FIRST | BUY", "Concatenated string. Included in buys list (L557). Excluded from API/Flutter buy_count exact match."),
    ("WAIT", "IntradayScannerService", "L551", "WAIT | BUY", "Concatenated string. Included in buys list (L557) because 'BUY' in string!"),
    ("REJECT", "IntradayScannerService", "L551", "REJECT | BUY", "Concatenated string. Included in buys list (L557) because 'BUY' in string!")
]

for orig, file_func, line, trans, notes in matrix:
    print(f"Original: {orig:<12} | Stage: {file_func:<22} | Line: {line:<5} | Transformed: {trans:<20} | Notes: {notes}")
