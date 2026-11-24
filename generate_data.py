import numpy as np
import pandas as pd


def build_synthetic_dataset(seed: int = 42) -> pd.DataFrame:
    """
    Generates a 30-day synthetic operational dataset across 4 decentralized
    perishable-fulfillment entities (~4,00,000 daily units scale, 4-hour shelf life).
    100% synthetic textbook figures for public portfolio demonstration.
    """
    rng = np.random.default_rng(seed)
    entities = ["Unit-North", "Unit-South", "Unit-East", "Unit-West"]
    days = pd.date_range("2026-10-01", periods=30, freq="D")

    catalog = [
        ("SKU-001", "Steamed Grain Staple", "Staple", "Kg", 0.20, 32.00),
        ("SKU-002", "Lentil Curry Base", "Protein/Gravy", "Kg", 0.12, 28.00),
        ("SKU-003", "Savory Rice Pancake", "Breakfast", "Nos", 3.00, 7.50),
        ("SKU-005", "Fermented Dairy Side", "Accompaniment", "Kg", 0.08, 45.00),
        ("SKU-006", "Crisp Lentil Wafer", "Accompaniment", "Nos", 1.00, 2.20),
        ("SKU-007", "Millet Porridge Dumpling", "Breakfast", "Kg", 0.20, 44.00),
        ("SKU-008", "Spiced Tamarind Broth", "Gravy", "Kg", 0.10, 34.00),
        ("SKU-009", "Spiced Protein Curry", "Executive Meal", "Kg", 0.25, 240.00),
    ]

    rows = []
    for d in days:
        dow = d.day_name()
        for ent in entities:
            base_pax = {
                "Unit-North": 38000,
                "Unit-South": 35000,
                "Unit-East": 32000,
                "Unit-West": 28333,
            }[ent]
            pax = int(base_pax * rng.uniform(0.95, 1.05))

            for sku_id, name, cat, uom, std_por, std_rate in catalog:
                if sku_id == "SKU-003" and dow != "Thursday":
                    continue
                if sku_id == "SKU-006" and d.day % 6 == 0:
                    continue

                eff_pax = 15 if sku_id == "SKU-009" else pax
                por = std_por

                # Controlled yield-drift anomalies across decentralized units
                if ent == "Unit-South" and sku_id in ["SKU-007", "SKU-008"] and dow == "Wednesday":
                    por = std_por * 1.25  # +25% portion drift
                if ent == "Unit-West" and sku_id == "SKU-001" and d.day % 4 == 0:
                    por = std_por * 1.12  # +12% staple drift
                if ent == "Unit-East" and sku_id == "SKU-009" and d.day % 5 == 0:
                    por = 1.50  # Uncalibrated small-batch outlier

                qty = round(eff_pax * por, 2)
                cost = round(qty * std_rate, 2)
                rows.append([
                    d.strftime("%Y-%m-%d"), dow, ent, sku_id, name, cat, uom,
                    eff_pax, std_por, por, qty, std_rate, cost
                ])

    df = pd.DataFrame(rows, columns=[
        "Date", "Weekday", "Entity", "SKU_ID", "SKU_Name", "Category", "UoM",
        "PAX", "Std_Portion", "Actual_Portion", "Issued_Qty", "Unit_Rate_INR", "Total_Cost_INR"
    ])
    return df
