import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import preswald

# Load dataset and clean columns
df = pd.read_csv("data/healthcare_dataset.csv")
df.columns = df.columns.str.strip().str.upper()

# Parse date columns for length of stay
df["DATE OF ADMISSION"] = pd.to_datetime(df["DATE OF ADMISSION"], errors="coerce")
df["DISCHARGE DATE"] = pd.to_datetime(df["DISCHARGE DATE"], errors="coerce")
df["LENGTH OF STAY"] = (df["DISCHARGE DATE"] - df["DATE OF ADMISSION"]).dt.days

# Clean rows with critical missing values for analysis
df_clean = df.dropna(subset=["AGE", "GENDER", "MEDICAL CONDITION", "BILLING AMOUNT", "DATE OF ADMISSION"])

# Page header
preswald.text("# 🏥 Healthcare Data Dashboard")
preswald.text(f"Total Patient Records: **{len(df_clean)}**")

# -------------------- Gender Split --------------------
preswald.text("## 👤 Gender Distribution")
preswald.text("""
This bar chart displays the distribution of patients by gender. It helps identify any imbalance in the gender representation among patients and may reveal trends in healthcare access or conditions that are more prevalent in one gender.
""")

if "GENDER" in df_clean.columns:
    gender_counts = df_clean["GENDER"].value_counts().reset_index()
    gender_counts.columns = ["Gender", "Count"]

    fig_gender_bar = px.bar(
        gender_counts,
        x="Count",
        y="Gender",
        orientation='h',
        color="Gender",
        text="Count",
        color_discrete_sequence=['#FFD166', '#118AB2'],
        title="👤 Gender Split"
    )
    fig_gender_bar.update_traces(
        textfont_size=14,
        textposition='outside',
        marker_line_color='white',
        marker_line_width=2
    )
    fig_gender_bar.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(categoryorder='total ascending'),
        title_font=dict(size=24, family='Verdana'),
        margin=dict(l=50, r=30, t=80, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=True
    )
    preswald.plotly(fig_gender_bar)

# -------------------- Age Distribution --------------------
preswald.text("## 🎂 Age Distribution")
preswald.text("""
This histogram shows how patients are distributed by age. Recognizing age group trends allows hospitals to tailor care—such as pediatrics for younger ages or geriatric services for older populations.
""")

if "AGE" in df_clean.columns:
    fig_age = px.histogram(
        df_clean,
        x="AGE",
        nbins=20,
        title="🎂 Age Distribution",
        color_discrete_sequence=["#118AB2"]
    )
    fig_age.update_layout(
        bargap=0.1,
        autosize=True,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    preswald.plotly(fig_age)

# -------------------- Top 10 Medical Conditions --------------------
preswald.text("## 🩺 Top Medical Conditions")
preswald.text("""
This bar chart highlights the top 10 most commonly diagnosed medical conditions in the dataset. It helps clinicians and hospital admins focus on high-frequency issues and better allocate staff and resources.
""")

if "MEDICAL CONDITION" in df_clean.columns:
    cond_counts = df_clean["MEDICAL CONDITION"].value_counts().nlargest(10).reset_index()
    cond_counts.columns = ["Medical Condition", "Count"]
    fig_cond = px.bar(cond_counts, x="Medical Condition", y="Count", color="Count",
                      color_continuous_scale="Turbo", title="Top 10 Medical Conditions")
    preswald.plotly(fig_cond)

# -------------------- Billing by Admission Type --------------------
preswald.text("## 💰 Billing by Admission Type")
preswald.text("""
This box plot displays the variation in billing amounts across different admission types. It helps assess how costs differ between emergency, elective, and other types of hospital admissions.
""")

if "BILLING AMOUNT" in df_clean.columns and "ADMISSION TYPE" in df_clean.columns:
    fig_billing = px.box(df_clean, x="ADMISSION TYPE", y="BILLING AMOUNT", color="ADMISSION TYPE",
                         title="Billing Amount by Admission Type",
                         color_discrete_sequence=px.colors.qualitative.Set2)
    preswald.plotly(fig_billing)

# -------------------- Heatmap: Age vs Length of Stay --------------------
preswald.text("## 🔥 Age vs Length of Stay")
preswald.text("""
This heatmap shows how patient age correlates with the length of hospital stay. Hotter regions indicate where many patients cluster. It can reveal whether certain age groups tend to stay longer.
""")

if "AGE" in df_clean.columns and "LENGTH OF STAY" in df_clean.columns:
    fig_los_heat = px.density_heatmap(
        df_clean,
        x="AGE",
        y="LENGTH OF STAY",
        nbinsx=20,
        nbinsy=15,
        title="🔥 Patient Age vs Length of Stay",
        color_continuous_scale="Viridis"
    )

    fig_los_heat.update_layout(
        xaxis_title="Age",
        yaxis_title="Length of Stay (Days)",
        template="plotly_white",
        height=450
    )

    preswald.plotly(fig_los_heat)

# -------------------- Blood Type by Gender --------------------
preswald.text("## 🩸 Blood Type Distribution by Gender")
preswald.text("""
This stacked bar chart illustrates how different blood types are distributed across genders. It helps with inventory planning in blood banks and understanding genetic distributions.
""")

if "BLOOD TYPE" in df_clean.columns and "GENDER" in df_clean.columns:
    blood_gender = df_clean.groupby(["BLOOD TYPE", "GENDER"]).size().reset_index(name="Count")
    sorted_bloods = blood_gender.groupby("BLOOD TYPE")["Count"].sum().sort_values(ascending=False).index
    blood_gender["BLOOD TYPE"] = pd.Categorical(blood_gender["BLOOD TYPE"], categories=sorted_bloods, ordered=True)
    blood_gender = blood_gender.sort_values("BLOOD TYPE")

    fig_blood_gender = px.bar(
        blood_gender,
        x="BLOOD TYPE",
        y="Count",
        color="GENDER",
        barmode="stack",
        title="🩸 Blood Type Distribution by Gender",
        color_discrete_sequence=["#8B0000", "#DC143C", "#FF6347"],
        category_orders={"BLOOD TYPE": sorted_bloods.tolist()}
    )

    fig_blood_gender.update_layout(
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#1a1a1a",
        font=dict(color="white"),
        title_font_size=22,
        xaxis=dict(title="Blood Type", showgrid=False),
        yaxis=dict(title="Count", showgrid=True, gridcolor="#333"),
        legend_title_text="Gender",
        height=450,
        margin=dict(l=40, r=30, t=60, b=40)
    )

    preswald.plotly(fig_blood_gender)

# -------------------- Billing Trend Over Time --------------------
preswald.text("## 📈 Billing Over Time")
preswald.text("""
This line chart tracks total billing amounts over time (monthly). It reveals seasonal trends, spikes, or dips in hospital revenue or service usage that can help in operational forecasting.
""")

if "DATE OF ADMISSION" in df_clean.columns and "BILLING AMOUNT" in df_clean.columns:
    df_clean["MONTH"] = df_clean["DATE OF ADMISSION"].dt.to_period("M").dt.to_timestamp()
    billing_monthly = df_clean.groupby("MONTH")["BILLING AMOUNT"].sum().reset_index()
    fig_billing_time = px.line(billing_monthly, x="MONTH", y="BILLING AMOUNT",
                               title="Total Billing Amount Over Time", markers=True,
                               color_discrete_sequence=["#EF476F"])
    preswald.plotly(fig_billing_time)

# -------------------- Correlation Heatmap --------------------
preswald.text("## 📊 Correlation Heatmap")
preswald.text("""
This heatmap shows correlations among numerical fields like age, billing amount, and length of stay. Strong correlations (positive or negative) help in building predictive models or identifying underlying patterns.
""")

numerical_cols = ["AGE", "BILLING AMOUNT", "LENGTH OF STAY"]
if all(col in df_clean.columns for col in numerical_cols):
    corr = df_clean[numerical_cols].corr()
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', title="Correlation Heatmap")
    preswald.plotly(fig_corr)

# -------------------- Top 5 Highest Billing Patients --------------------
preswald.text("## 💸 Top 5 Highest Billing Patients")
preswald.text("""
This table showcases the five patients with the highest billing amounts. Useful for reviewing high-cost cases and understanding what conditions or admission types drive healthcare expenses.
""")

top_billed = df_clean.sort_values("BILLING AMOUNT", ascending=False).head(5)
preswald.table(top_billed[["NAME", "BILLING AMOUNT", "MEDICAL CONDITION", "HOSPITAL", "ADMISSION TYPE"]])

# -------------------- Animated Billing vs Age (by Month) --------------------
preswald.text("## 🌀 Explore Billing vs Age (Month-by-Month)")
preswald.text("""
This animated scatter plot allows exploration of how billing and age correlate over different months. Each point's size represents length of stay, offering a dynamic view of patient characteristics over time.
""")

if "DATE OF ADMISSION" in df_clean.columns:
    df_clean["ADMISSION MONTH"] = df_clean["DATE OF ADMISSION"].dt.to_period("M").dt.to_timestamp()

    months = df_clean["ADMISSION MONTH"].dropna().sort_values().unique()
    frames = []

    for month in months:
        month_data = df_clean[df_clean["ADMISSION MONTH"] == month]
        trace = go.Scatter(
            x=month_data["AGE"],
            y=month_data["BILLING AMOUNT"],
            mode='markers',
            marker=dict(size=month_data["LENGTH OF STAY"], color=month_data["AGE"], colorscale="Viridis", showscale=False),
            name=str(month),
            text=month_data["MEDICAL CONDITION"],
            hovertemplate="Age: %{x}<br>Billing: %{y}<br>Condition: %{text}<extra></extra>",
            visible=False
        )
        frames.append(trace)

    frames[0]['visible'] = True

    fig_manual = go.Figure(data=frames)

    fig_manual.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {"label": str(month), "method": "update", "args": [{"visible": [i == j for i in range(len(months))]}]}
                    for j, month in enumerate(months)
                ],
                "direction": "down",
                "showactive": True,
                "x": 1.40,
                "y": 0.50,
                "xanchor": "right",
                "yanchor": "top"
            }
        ],
        title="🌀 Explore Billing vs Age (Month-by-Month)",
        xaxis_title="Age",
        yaxis_title="Billing Amount"
    )

    preswald.plotly(fig_manual)
    
    
# -------------------- Sunburst: Admission Type → Medical Condition → Gender --------------------
preswald.text("## 🌈 Hierarchical Breakdown: Admission → Condition → Gender")
preswald.text("""
This sunburst chart offers a multi-level hierarchical view of patient data. The inner circle represents admission types (e.g., Emergency, Routine),
the next layer breaks it down by medical condition, and the outermost layer shows gender distribution.
This helps quickly visualize which conditions dominate each admission type and how they vary across genders,
revealing hidden patterns in the dataset.
""")

if all(col in df_clean.columns for col in ["ADMISSION TYPE", "MEDICAL CONDITION", "GENDER"]):
    fig_sunburst = px.sunburst(
        df_clean,
        path=["ADMISSION TYPE", "MEDICAL CONDITION", "GENDER"],
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    preswald.plotly(fig_sunburst)


preswald.text("---")
preswald.text("📘 Dashboard created and visualized by **Samarth Sharma** using Preswald.")
  
