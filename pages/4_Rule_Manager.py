import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Rule Manager",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Fraud Rule Management")

# =====================================
# Initialize Rules
# =====================================

DEFAULT_RULES = [
    {
        "Rule ID": "AMOUNT001",
        "Rule Name": "Large Amount",
        "Threshold": "10000000",
        "Score": 30,
        "Status": "Enabled"
    },
    {
        "Rule ID": "DEVICE001",
        "Rule Name": "New Device",
        "Threshold": "-",
        "Score": 20,
        "Status": "Enabled"
    },
    {
        "Rule ID": "COUNTRY001",
        "Rule Name": "High Risk Country",
        "Threshold": "IR,RU,KP,SY",
        "Score": 25,
        "Status": "Enabled"
    },
    {
        "Rule ID": "MERCHANT001",
        "Rule Name": "High Risk Merchant",
        "Threshold": "HIGH",
        "Score": 20,
        "Status": "Enabled"
    },
    {
        "Rule ID": "VELOCITY001",
        "Rule Name": "Velocity Rule",
        "Threshold": "5",
        "Score": 20,
        "Status": "Enabled"
    },
    {
        "Rule ID": "TIME001",
        "Rule Name": "Night Transaction",
        "Threshold": "23:00-06:00",
        "Score": 15,
        "Status": "Enabled"
    }
]

if "rules" not in st.session_state:

    st.session_state.rules = pd.DataFrame(DEFAULT_RULES)

rules = st.session_state.rules.copy()

# =====================================
# Sidebar
# =====================================

st.sidebar.header("Rule Filter")

keyword = st.sidebar.text_input(
    "Search Rule"
)

status = st.sidebar.multiselect(
    "Status",
    ["Enabled", "Disabled"],
    default=["Enabled", "Disabled"]
)

filtered = rules.copy()

if keyword:

    filtered = filtered[
        filtered["Rule ID"].str.contains(keyword, case=False)
        |
        filtered["Rule Name"].str.contains(keyword, case=False)
    ]

filtered = filtered[
    filtered["Status"].isin(status)
]

# =====================================
# KPI
# =====================================

total = len(filtered)

enabled = len(
    filtered[
        filtered["Status"] == "Enabled"
    ]
)

disabled = len(
    filtered[
        filtered["Status"] == "Disabled"
    ]
)

avg_score = round(
    filtered["Score"].mean(),
    1
)

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Total Rules",
    total
)

c2.metric(
    "Enabled",
    enabled
)

c3.metric(
    "Disabled",
    disabled
)

c4.metric(
    "Average Score",
    avg_score
)

st.divider()

# =====================================
# Rule Table
# =====================================

st.subheader("📋 Rule List")

st.dataframe(

    filtered,

    use_container_width=True,

    height=350

)

st.divider()

# =====================================
# Select Rule
# =====================================

rule_id = st.selectbox(

    "Select Rule",

    filtered["Rule ID"]

)

selected = filtered[
    filtered["Rule ID"] == rule_id
].iloc[0]
# =====================================
# Rule Detail
# =====================================

st.subheader("📝 Rule Detail")

col1, col2 = st.columns(2)

with col1:

    threshold = st.text_input(
        "Threshold",
        value=str(selected["Threshold"])
    )

    score = st.number_input(
        "Risk Score",
        min_value=0,
        max_value=100,
        value=int(selected["Score"])
    )

with col2:

    status = st.selectbox(
        "Status",
        ["Enabled", "Disabled"],
        index=0 if selected["Status"] == "Enabled" else 1
    )

    st.text_input(
        "Rule Name",
        value=selected["Rule Name"],
        disabled=True
    )

# =====================================
# Save Rule
# =====================================

if st.button(
    "💾 Save Rule",
    use_container_width=True
):

    idx = rules.index[
        rules["Rule ID"] == rule_id
    ][0]

    rules.loc[idx, "Threshold"] = str(threshold)
    rules.loc[idx, "Score"] = int(score)
    rules.loc[idx, "Status"] = status

    st.session_state.rules = rules

    st.success("Rule updated successfully.")

    st.rerun()

st.divider()

# =====================================
# Quick Toggle
# =====================================

st.subheader("⚡ Quick Enable / Disable")

toggle_rule = st.selectbox(
    "Rule",
    rules["Rule ID"],
    key="toggle_rule"
)

if st.button(
    "Toggle Status",
    use_container_width=True
):

    idx = rules.index[
        rules["Rule ID"] == toggle_rule
    ][0]

    current = rules.loc[idx, "Status"]

    rules.loc[idx, "Status"] = (
        "Disabled"
        if current == "Enabled"
        else "Enabled"
    )

    st.session_state.rules = rules

    st.success("Rule status updated.")

    st.rerun()

st.divider()

# =====================================
# Add New Rule
# =====================================

st.subheader("➕ Add New Rule")

a1, a2 = st.columns(2)

with a1:

    new_id = st.text_input(
        "Rule ID"
    )

    new_name = st.text_input(
        "Rule Name"
    )

with a2:

    new_threshold = st.text_input(
        "Threshold"
    )

    new_score = st.number_input(
        "Score",
        min_value=0,
        max_value=100,
        value=10,
        key="new_score"
    )

if st.button(
    "Add Rule",
    use_container_width=True
):

    if not new_id.strip():

        st.error("Rule ID is required.")

    elif not new_name.strip():

        st.error("Rule Name is required.")

    elif new_id in rules["Rule ID"].values:

        st.error("Rule ID already exists.")

    else:

        new_rule = pd.DataFrame([{

            "Rule ID": new_id,

            "Rule Name": new_name,

            "Threshold": new_threshold,

            "Score": int(new_score),

            "Status": "Enabled"

        }])

        rules = pd.concat(
            [rules, new_rule],
            ignore_index=True
        )

        st.session_state.rules = rules

        st.success("Rule added successfully.")

        st.rerun()

st.divider()

# =====================================
# Delete Rule
# =====================================

st.subheader("🗑️ Delete Rule")

confirm = st.checkbox(
    "I understand this action cannot be undone."
)

if st.button(
    "Delete Selected Rule",
    disabled=not confirm,
    type="primary",
    use_container_width=True
):

    rules = rules[
        rules["Rule ID"] != rule_id
    ].reset_index(drop=True)

    st.session_state.rules = rules

    st.success("Rule deleted successfully.")

    st.rerun()

st.divider()
# =====================================
# Rule Statistics
# =====================================

st.subheader("📊 Rule Statistics")

col1, col2 = st.columns(2)

with col1:

    status_df = (
        rules["Status"]
        .value_counts()
        .reset_index()
    )

    status_df.columns = [
        "Status",
        "Count"
    ]

    fig = px.pie(
        status_df,
        names="Status",
        values="Count",
        title="Enabled vs Disabled Rules"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    score_df = rules.sort_values(
        "Score",
        ascending=False
    )

    fig = px.bar(
        score_df,
        x="Rule ID",
        y="Score",
        color="Status",
        title="Rule Risk Score"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================
# Top Risk Rules
# =====================================

st.subheader("🔥 Top Risk Rules")

top_rules = rules.sort_values(
    "Score",
    ascending=False
)

st.dataframe(
    top_rules,
    use_container_width=True,
    height=300
)

st.divider()

# =====================================
# Rule Summary
# =====================================

st.subheader("📈 Score Summary")

summary = pd.DataFrame({

    "Metric": [

        "Maximum Score",
        "Minimum Score",
        "Average Score",
        "Total Enabled",
        "Total Disabled"

    ],

    "Value": [

        rules["Score"].max(),
        rules["Score"].min(),
        round(rules["Score"].mean(), 2),
        len(rules[rules["Status"]=="Enabled"]),
        len(rules[rules["Status"]=="Disabled"])

    ]

})

st.dataframe(
    summary,
    use_container_width=True
)

st.divider()

# =====================================
# Threshold Distribution
# =====================================

st.subheader("🎯 Rule Threshold")

threshold_df = rules[[
    "Rule ID",
    "Threshold"
]]

st.dataframe(
    threshold_df,
    use_container_width=True
)

st.divider()

# =====================================
# Rule Configuration Preview
# =====================================

st.subheader("⚙ Current Rule Configuration")

st.json(
    rules.to_dict(
        orient="records"
    )
)

st.divider()