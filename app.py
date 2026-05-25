import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE SETTINGS
st.set_page_config(
    page_title="Excel Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Excel Data Analyzer")
st.write("Upload your Excel file and explore your data!")

# UPLOAD EXCEL FILE
uploaded_file = st.file_uploader(
    "📁 Upload your Excel file",
    type=["xlsx", "xls"]
)

if uploaded_file is not None:

    # READ THE FILE
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded! {len(df)} rows and {len(df.columns)} columns found.")

    # SHOW RAW DATA
    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df, use_container_width=True)

    # BASIC STATISTICS
    st.subheader("📈 Basic Statistics")
    st.write(df.describe())

    # CHART SETTINGS
    st.subheader("🎨 Create Your Chart")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols    = df.select_dtypes(include="object").columns.tolist()

    col1, col2, col3 = st.columns(3)
    with col1:
        chart_type = st.selectbox("Chart type", ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])
    with col2:
        x_axis = st.selectbox("X axis", text_cols + numeric_cols)
    with col3:
        y_axis = st.selectbox("Y axis", numeric_cols)

    # DRAW CHART
    if chart_type == "Bar Chart":
        fig = px.bar(df, x=x_axis, y=y_axis, color=x_axis)
    elif chart_type == "Line Chart":
        fig = px.line(df, x=x_axis, y=y_axis)
    elif chart_type == "Pie Chart":
        fig = px.pie(df, names=x_axis, values=y_axis)
    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_axis, y=y_axis)

    st.plotly_chart(fig, use_container_width=True)

    # ──────────────────────────────────────
    # CHATBOT SECTION
    # ──────────────────────────────────────
    st.subheader("🤖 Chat with Your Data!")
    st.write("Ask me anything about your Excel data!")

    # Store chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):

        # Show user message
        with st.chat_message("user"):
            st.write(prompt)

        # Save user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate answer
        response = ""

        if "row" in prompt.lower() or "rows" in prompt.lower():
            response = f"📊 Your data has **{len(df)} rows**."

        elif "column" in prompt.lower() or "columns" in prompt.lower():
            response = f"📋 Your data has **{len(df.columns)} columns**: {', '.join(df.columns.tolist())}"

        elif "average" in prompt.lower() or "mean" in prompt.lower():
            if numeric_cols:
                avgs = df[numeric_cols].mean().round(2)
                response = "📈 Averages:\n"
                for col, val in avgs.items():
                    response += f"- **{col}**: {val}\n"
            else:
                response = "❌ No numeric columns found to calculate average."

        elif "maximum" in prompt.lower() or "max" in prompt.lower():
            if numeric_cols:
                maxs = df[numeric_cols].max()
                response = "📈 Maximum values:\n"
                for col, val in maxs.items():
                    response += f"- **{col}**: {val}\n"
            else:
                response = "❌ No numeric columns found."

        elif "minimum" in prompt.lower() or "min" in prompt.lower():
            if numeric_cols:
                mins = df[numeric_cols].min()
                response = "📈 Minimum values:\n"
                for col, val in mins.items():
                    response += f"- **{col}**: {val}\n"
            else:
                response = "❌ No numeric columns found."

        elif "sum" in prompt.lower() or "total" in prompt.lower():
            if numeric_cols:
                sums = df[numeric_cols].sum().round(2)
                response = "💰 Total values:\n"
                for col, val in sums.items():
                    response += f"- **{col}**: {val}\n"
            else:
                response = "❌ No numeric columns found."

        elif "missing" in prompt.lower() or "null" in prompt.lower():
            missing = df.isnull().sum()
            response = "🔍 Missing values:\n"
            for col, val in missing.items():
                response += f"- **{col}**: {val} missing\n"

        else:
            response = f"🤖 I can answer questions like:\n- How many rows?\n- How many columns?\n- What is the average?\n- What is the maximum?\n- What is the minimum?\n- What is the total?\n- Any missing values?"

        # Show bot response
        with st.chat_message("assistant"):
            st.write(response)

        # Save bot response
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.info("👆 Please upload an Excel file to get started!")
