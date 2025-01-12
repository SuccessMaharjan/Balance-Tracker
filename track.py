import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Database connection setup
def get_db_connection():
    conn = sqlite3.connect('transactions.db')
    return conn

# Create table if not exists (should be done once on app startup)
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_date TEXT,
            month TEXT,
            amount_bought REAL,
            amount_sold REAL,
            amount_deposited REAL,
            balance_amount REAL
        )
    """)
    conn.commit()
    conn.close()

# Function to load transactions from the database
def load_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to DataFrame for easy display
    transactions_df = pd.DataFrame(rows, columns=["ID", "Full Date", "Month", "Amount Bought", "Amount Sold", "Amount Deposited", "Balance Amount"])
    return transactions_df

# Function to save new transaction into the database
def save_transaction(transaction):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (full_date, month, amount_bought, amount_sold, amount_deposited, balance_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (transaction["Full Date"], transaction["Month"], transaction["Amount Bought"], transaction["Amount Sold"], transaction["Amount Deposited"], transaction["Balance Amount"]))
    conn.commit()
    conn.close()

# Function to calculate running balance
def calculate_running_balance(transactions):
    balance = 0
    for index, row in transactions.iterrows():
        balance += row["Amount Deposited"]
        balance -= row["Amount Bought"]
        balance += row["Amount Sold"]
        transactions.at[index, "Balance Amount"] = balance
    return transactions

# Initialize database and table
create_table()

# App title with custom style
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🌟 Stock Transaction Tracker 🌟</h1>",
    unsafe_allow_html=True,
)
st.write("Keep track of your stock transactions with ease.")

# Input form for new transaction
st.markdown("---")
st.subheader("📥 Add New Transaction")
with st.form("transaction_form"):
    cols = st.columns(3)
    full_date = cols[0].date_input("Full Date")
    amount_bought = cols[1].number_input("Amount Bought ($)", min_value=0.0, step=0.01)
    amount_sold = cols[2].number_input("Amount Sold ($)", min_value=0.0, step=0.01)
    
    cols = st.columns(3)
    amount_deposited = cols[0].number_input("Amount Deposited ($)", min_value=0.0, step=0.01)
    month = full_date.strftime("%B %Y")
    
    submitted = st.form_submit_button(
        label="➕ Add Transaction",
        use_container_width=True
    )

    if submitted:
        # Prepare the new transaction data
        new_transaction = {
            "Full Date": full_date,
            "Month": month,
            "Amount Bought": amount_bought,
            "Amount Sold": amount_sold,
            "Amount Deposited": amount_deposited,
            "Balance Amount": 0,  # Temporary; updated in the next step
        }

        # Save transaction to the database
        save_transaction(new_transaction)

        # Reload transactions from the database and recalculate balances
        transactions_df = load_transactions()
        transactions_df = calculate_running_balance(transactions_df)

        st.success("Transaction added successfully!")

# Display transaction history
st.markdown("---")
st.subheader("📊 Transaction History")
transactions_df = load_transactions()
if not transactions_df.empty:
    # Show the data table
    st.dataframe(transactions_df.style.format({"Amount Bought": "${:,.2f}", "Amount Sold": "${:,.2f}", "Amount Deposited": "${:,.2f}", "Balance Amount": "${:,.2f}"}))

    # Download as CSV button
    csv = transactions_df.to_csv(index=False)
    st.download_button(
        label="💾 Download History as CSV",
        data=csv,
        file_name="transaction_history.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Display current balance as a metric
    st.metric(label="💰 Current Balance", value=f"${transactions_df.iloc[-1]['Balance Amount']:.2f}")

    # Interactive chart
    st.markdown("### 📈 Monthly Trends")
    monthly_summary = (
        transactions_df.groupby("Month")[["Amount Bought", "Amount Sold", "Amount Deposited"]]
        .sum()
        .reset_index()
    )
    fig = px.bar(
        monthly_summary,
        x="Month",
        y=["Amount Bought", "Amount Sold", "Amount Deposited"],
        title="Monthly Transaction Summary",
        labels={"value": "Amount ($)", "variable": "Transaction Type"},
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No transactions recorded yet. Start adding some!")

# Footer
st.markdown("---")
st.markdown(
    "<h4 style='text-align: center;'>Built with ❤️ using Streamlit</h4>",
    unsafe_allow_html=True,
)