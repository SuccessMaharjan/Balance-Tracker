import streamlit as st
import pandas as pd
import plotly.express as px

# Initialize session state for storing transactions
if "transactions" not in st.session_state:
    st.session_state["transactions"] = []

# Function to calculate balance for each transaction
def calculate_running_balance(transactions):
    balance = 0
    for transaction in transactions:
        balance += transaction["Amount Deposited"]
        balance -= transaction["Amount Bought"]
        balance += transaction["Amount Sold"]
        transaction["Balance Amount"] = balance
    return transactions

# App title with custom style
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🌟 Stock Transaction Tracker 🌟</h1>",
    unsafe_allow_html=True,
)
st.write("Keep track of your stock transactions with ease.")

# Input form
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
        new_transaction = {
            "Full Date": full_date,
            "Month": month,
            "Amount Bought": amount_bought,
            "Amount Sold": amount_sold,
            "Amount Deposited": amount_deposited,
            "Balance Amount": 0,  # Temporary; updated in the next step
        }
        st.session_state["transactions"].append(new_transaction)
        st.session_state["transactions"] = calculate_running_balance(st.session_state["transactions"])
        st.success("Transaction added successfully!")

# Display transaction history
st.markdown("---")
st.subheader("📊 Transaction History")
if st.session_state["transactions"]:
    transactions_df = pd.DataFrame(st.session_state["transactions"])

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