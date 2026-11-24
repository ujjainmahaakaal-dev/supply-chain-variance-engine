import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st
from generate_data import build_synthetic_dataset

st.set_page_config(
    page_title="Perishable Supply-Chain Variance & EBITDA Engine",
    layout="wide",
)

st.title("Post-Merger Operational Excellence: Perishable Supply-Chain Variance Engine")
st.caption(
    "Architectural Decision-Intelligence Model | Multi-Entity Roll-Up (~4 Lakh Daily Units, 4-Hour Shelf Life) | Synthetic Portfolio Data"
)

df = build_synthetic_dataset()

# Sidebar Executive Policy & ERP Tolerance Controls
st.sidebar.header("Governance & ERP Control Levers")
tolerance_pct = st.sidebar.slider(
    "ERP Pre-Indent Portion Tolerance Lock (%)",
    min_value=0, max_value=25, value=2, step=1,
    help="Hard-blocks kitchen indents exceeding standard portion norm above this threshold."
)
wafer_days_cut = st.sidebar.slider(
    "Accompaniment Rationalization (Nights Reduced / Month)",
    min_value=0, max_value=15, value=12, step=1,
)
pancake_swap_days = st.sidebar.slider(
    "High-Cost Breakfast Substitution (Days / Month @ ₹2.50/unit saving)",
    min_value=0, max_value=4, value=2, step=1,
)

# Run DuckDB Analytical Query directly on DataFrame
con = duckdb.connect()
con.register("indents", df)

summary_sql = f"""
SELECT
    Entity,
    SUM(Total_Cost_INR) AS Monthly_Spend_INR,
    SUM(CASE
        WHEN Actual_Portion > Std_Portion * (1 + {tolerance_pct}/100.0)
        THEN (Actual_Portion - Std_Portion * (1 + {tolerance_pct}/100.0)) * PAX * Unit_Rate_INR
        ELSE 0
    END) AS Recoverable_Yield_Drift_INR,
    SUM(CASE WHEN SKU_ID = 'SKU-006' THEN Total_Cost_INR ELSE 0 END) * ({wafer_days_cut}/25.0) AS Accompaniment_Saving_INR,
    SUM(CASE WHEN SKU_ID = 'SKU-003' THEN PAX * 3.0 * 2.50 ELSE 0 END) * ({pancake_swap_days}/4.0) AS Menu_Swap_Saving_INR
FROM indents
GROUP BY Entity
ORDER BY Monthly_Spend_INR DESC
"""
res = con.execute(summary_sql).df()
res["Total_Monthly_EBITDA_Lift_INR"] = (
    res["Recoverable_Yield_Drift_INR"]
    + res["Accompaniment_Saving_INR"]
    + res["Menu_Swap_Saving_INR"]
)
res["Annualized_EBITDA_Lift_INR"] = res["Total_Monthly_EBITDA_Lift_INR"] * 12

# Top Executive KPI Strip
total_spend = res["Monthly_Spend_INR"].sum()
monthly_lift = res["Total_Monthly_EBITDA_Lift_INR"].sum()
annual_lift = res["Annualized_EBITDA_Lift_INR"].sum()
lift_pct = (monthly_lift / total_spend) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Monthly Portfolio Spend", f"₹{total_spend/1e7:.2f} Cr")
c2.metric("Recoverable Yield-Drift & Mix Lift", f"₹{monthly_lift/1e5:.2f} L / mo", f"+{lift_pct:.2f}% Margin")
c3.metric("Annualized EBITDA Protection", f"₹{annual_lift/1e7:.2f} Cr / yr")
c4.metric("Active Decentralized Entities", "4 Units (Harmonized)")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Cross-Entity EBITDA Recovery Breakdown (₹ Lakhs / Month)")
    chart_df = res.melt(
        id_vars="Entity",
        value_vars=["Recoverable_Yield_Drift_INR", "Accompaniment_Saving_INR", "Menu_Swap_Saving_INR"],
        var_name="Transformation Lever",
        value_name="Monthly_Saving_INR",
    )
    chart_df["Monthly_Saving_Lakhs"] = chart_df["Monthly_Saving_INR"] / 1e5
    fig = px.bar(
        chart_df,
        x="Entity",
        y="Monthly_Saving_Lakhs",
        color="Transformation Lever",
        barmode="stack",
        labels={"Monthly_Saving_Lakhs": "Monthly EBITDA Lift (₹ Lakhs)"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Entity Benchmarking Scorecard")
    display_df = res[[
        "Entity", "Monthly_Spend_INR", "Recoverable_Yield_Drift_INR",
        "Total_Monthly_EBITDA_Lift_INR", "Annualized_EBITDA_Lift_INR"
    ]].copy()
    for col in display_df.columns[1:]:
        display_df[col] = display_df[col].map(lambda x: f"₹{x:,.0f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.subheader("DuckDB SQL Audit Trail: Top Yield-Drift Exceptions")
exceptions_sql = """
SELECT
    Entity, Weekday, SKU_ID, SKU_Name,
    COUNT(*) AS Drift_Events,
    ROUND(AVG(Std_Portion), 3) AS Std_Portion,
    ROUND(MAX(Actual_Portion), 3) AS Peak_Actual_Portion,
    ROUND(SUM((Actual_Portion - Std_Portion) * PAX * Unit_Rate_INR), 0) AS Total_Drift_Leakage_INR
FROM indents
WHERE Actual_Portion > Std_Portion
GROUP BY Entity, Weekday, SKU_ID, SKU_Name
ORDER BY Total_Drift_Leakage_INR DESC
"""
st.dataframe(con.execute(exceptions_sql).df(), use_container_width=True, hide_index=True)
