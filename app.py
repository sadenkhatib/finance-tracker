import streamlit as st
import pandas as pd
import plotly.express as px
from categoriser import categorise

st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")

st.title("💰 Personal Finance Tracker")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Upload your bank CSV", type="csv")
    st.markdown("---")
    st.caption("Expected columns: Date, Description, Amount, Transaction Type, Category, Account Name")

# ── Load & process data ────────────────────────────────────────────────────────
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Category"] = df["Description"].apply(categorise)
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Week"] = df["Date"].dt.to_period("W").astype(str)
    df["Year"] = df["Date"].dt.year.astype(str)
    return df

if uploaded_file is None:
    st.info("Upload a CSV file using the sidebar to get started.")
    st.stop()

df = load_data(uploaded_file)

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    time_period = st.selectbox("Group by", ["Month", "Week", "Year"])

    all_categories = sorted(df["Category"].unique())
    selected_categories = st.multiselect("Categories", all_categories, default=all_categories)

    all_accounts = sorted(df["Account Name"].unique())
    selected_accounts = st.multiselect("Accounts", all_accounts, default=all_accounts)

filtered = df[
    df["Category"].isin(selected_categories) &
    df["Account Name"].isin(selected_accounts)
]

debits = filtered[filtered["Transaction Type"] == "debit"]
credits = filtered[filtered["Transaction Type"] == "credit"]

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Transactions", "Trends", "Budget"])

# ── Tab 1: Overview ────────────────────────────────────────────────────────────
with tab1:
    total_spent = debits["Amount"].sum()
    total_income = credits["Amount"].sum()
    net = total_income - total_spent
    top_category = debits.groupby("Category")["Amount"].sum().idxmax() if not debits.empty else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spent", f"${total_spent:,.2f}")
    col2.metric("Total Income", f"${total_income:,.2f}")
    col3.metric("Net Balance", f"${net:,.2f}", delta=f"${net:,.2f}")
    col4.metric("Top Category", top_category)

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Spending by Category")
        cat_totals = debits.groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(cat_totals, names="Category", values="Amount", hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader(f"Spending Over Time ({time_period})")
        time_totals = debits.groupby(time_period)["Amount"].sum().reset_index()
        fig2 = px.line(time_totals, x=time_period, y="Amount", markers=True)
        fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)

# ── Tab 2: Transactions ────────────────────────────────────────────────────────
with tab2:
    st.subheader("All Transactions")

    search = st.text_input("Search by description")
    display = filtered.copy()
    if search:
        display = display[display["Description"].str.contains(search, case=False)]

    display = display.sort_values("Date", ascending=False)
    st.dataframe(
        display[["Date", "Description", "Amount", "Transaction Type", "Category", "Account Name"]],
        use_container_width=True,
        hide_index=True,
    )

# ── Tab 3: Trends ──────────────────────────────────────────────────────────────
with tab3:
    st.subheader(f"Monthly Spend by Category")
    monthly_cat = debits.groupby(["Month", "Category"])["Amount"].sum().reset_index()
    fig3 = px.bar(monthly_cat, x="Month", y="Amount", color="Category", barmode="stack")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Top 10 Merchants")
    top_merchants = debits.groupby("Description")["Amount"].sum().nlargest(10).reset_index()
    fig4 = px.bar(top_merchants, x="Amount", y="Description", orientation="h")
    fig4.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig4, use_container_width=True)

# ── Tab 4: Budget ──────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Monthly Budget")
    st.caption("Set a monthly budget for each category and see how you're tracking.")

    categories = sorted(debits["Category"].unique())
    latest_month = debits["Month"].max()
    monthly_spend = debits[debits["Month"] == latest_month].groupby("Category")["Amount"].sum()

    for cat in categories:
        spent = monthly_spend.get(cat, 0)
        budget = st.number_input(f"{cat} budget ($)", min_value=0, value=500, step=50, key=cat)

        if budget > 0:
            pct = min(spent / budget, 1.0)
            over = spent > budget
            color = "🔴" if over else "🟢"
            label = f"{color} {cat}: ${spent:,.2f} / ${budget:,.2f}"
            st.write(label)
            st.progress(pct)

            if over:
                excess = spent - budget
                st.caption(f"⚠️ You're ${excess:,.2f} over budget this month.")
        st.markdown("---")
