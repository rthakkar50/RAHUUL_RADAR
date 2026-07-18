import sys, os
sys.path.append(os.getcwd())

with open("core/relative_strength_engine.py", "r") as f:
    content = f.read()

# Add config constants
if "SHORT_TERM_WEIGHT_5D" not in content:
    content = content.replace(
        "    SECTOR_ALPHA_WEIGHT = 0.30",
        "    SECTOR_ALPHA_WEIGHT = 0.30\n    SHORT_TERM_WEIGHT_5D = 0.60\n    SHORT_TERM_WEIGHT_20D = 0.40\n    LONG_TERM_WEIGHT_50D = 0.60\n    LONG_TERM_WEIGHT_100D = 0.40\n    MOMENTUM_MAX_SPREAD = 10.0"
    )

# Update _default_rs_data
content = content.replace(
    '            "score": 50,\n            "classification": "Neutral",',
    '            "score": 50,\n            "momentum": 50,\n            "classification": "Neutral",'
)

# Update _update_rs_cache inside the universe loop
old_composite_logic = """                    # Composite RS Score (0-100 scale)
                    # Weights: 100D (30%), 50D (30%), 20D (20%), 5D (10%), 1D (10%)
                    composite = (rs_100d * 0.3) + (rs_50d * 0.3) + (rs_20d * 0.2) + (rs_5d * 0.1) + (rs_1d * 0.1)
                    
                    # Normalize raw composite roughly into 0-100
                    # Assuming a +/- 50% relative outperformance is the absolute extreme limit
                    normalized_score = max(0, min(100, (composite + 25) * 2))
                    
                    classification = "Neutral"
                    if normalized_score >= 95: classification = "Market Leader"
                    elif normalized_score >= 85: classification = "Strong Leader"
                    elif normalized_score >= 70: classification = "Outperforming"
                    elif normalized_score >= 55: classification = "Neutral"
                    elif normalized_score >= 40: classification = "Weak"
                    else: classification = "Underperformer"
                    
                    temp_rs_data[sym] = {
                        "score": round(normalized_score, 1),
                        "classification": classification,
                        "1d": round(rs_1d, 2),"""

new_composite_logic = """                    # Composite RS Score (0-100 scale)
                    # Weights: 100D (30%), 50D (30%), 20D (20%), 5D (10%), 1D (10%)
                    composite = (rs_100d * 0.3) + (rs_50d * 0.3) + (rs_20d * 0.2) + (rs_5d * 0.1) + (rs_1d * 0.1)
                    
                    # Normalize raw composite roughly into 0-100
                    # Assuming a +/- 50% relative outperformance is the absolute extreme limit
                    normalized_score = max(0, min(100, (composite + 25) * 2))
                    
                    # Calculate Relative Momentum
                    short_term_rs = (rs_5d * self.SHORT_TERM_WEIGHT_5D) + (rs_20d * self.SHORT_TERM_WEIGHT_20D)
                    long_term_rs = (rs_50d * self.LONG_TERM_WEIGHT_50D) + (rs_100d * self.LONG_TERM_WEIGHT_100D)
                    
                    raw_momentum = short_term_rs - long_term_rs
                    
                    # Normalize raw momentum to 0-100 scale using MOMENTUM_MAX_SPREAD (10.0 => 50% swing per 10 spread)
                    momentum_score = max(0, min(100, (raw_momentum + self.MOMENTUM_MAX_SPREAD) * (100 / (2 * self.MOMENTUM_MAX_SPREAD))))
                    
                    classification = "Neutral"
                    if normalized_score >= 95: classification = "Market Leader"
                    elif normalized_score >= 85: classification = "Strong Leader"
                    elif normalized_score >= 70: classification = "Outperforming"
                    elif normalized_score >= 55: classification = "Neutral"
                    elif normalized_score >= 40: classification = "Weak"
                    else: classification = "Underperformer"
                    
                    temp_rs_data[sym] = {
                        "score": round(normalized_score, 1),
                        "momentum": round(momentum_score, 1),
                        "classification": classification,
                        "1d": round(rs_1d, 2),"""

content = content.replace(old_composite_logic, new_composite_logic)

with open("core/relative_strength_engine.py", "w") as f:
    f.write(content)

print("Patched relative strength engine")
