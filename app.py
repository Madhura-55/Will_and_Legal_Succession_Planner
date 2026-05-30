import streamlit as st
import pandas as pd
from conversation import ConversationEngine

st.set_page_config(page_title="Smart-Will", page_icon="📜", layout="wide")
st.title("📜 Smart-Will")
st.caption("AI-powered will planner · Indian Succession Act 1925 · Hindu Succession Act 1956")

if "engine" not in st.session_state:
    st.session_state.engine = ConversationEngine()
    st.session_state.messages = []
    opening = st.session_state.engine.chat(
        "Hello Smart. Please introduce yourself briefly as Smart from Smart-Will "
        "and ask me the first question to begin creating my will."
    )
    st.session_state.messages.append({"role": "assistant", "content": opening})

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("Interview")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    engine = st.session_state.engine

    if not engine.is_complete:
        user_input = st.chat_input("Type your answer here...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Smart-Will is thinking..."):
                reply = engine.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    else:
        st.success("✅ All information collected! Your will is ready to generate.")
        if st.button("Generate Will DOCX", type="primary"):
            from generator import build_will
            doc = build_will(engine.get_will_data())
            doc.save("/tmp/smart_will.docx")
            with open("/tmp/smart_will.docx", "rb") as f:
                st.download_button(
                    label="⬇️ Download Smart-Will DOCX",
                    data=f,
                    file_name="smart_will.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

with col2:
    st.subheader("Collected Data")
    data = st.session_state.engine.will_data

    with st.container(border=True):
        st.markdown("**Testator**")
        st.write(f"Name: {data.testator_name or '—'}")
        st.write(f"Age: {data.testator_age or '—'}")
        st.write(f"Address: {data.testator_address or '—'}")
        st.write(f"Religion: {data.religion or '—'}")
        st.write(f"Family type: {data.family_type or '—'}")

    with st.container(border=True):
        st.markdown("**Assets**")
        if data.assets:
            rows = [{"Type": a.asset_type, "Description": a.description,
                     "ID": a.identifier or "—"} for a in data.assets]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("None yet")

    with st.container(border=True):
        st.markdown("**Beneficiaries**")
        if data.beneficiaries:
            rows = [{"Name": b.name, "Relation": b.relationship,
                     "Allocation": b.allocation} for b in data.beneficiaries]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("None yet")

    with st.container(border=True):
        st.markdown("**Executor**")
        st.write(data.executor_name or "—")
        st.markdown("**Witnesses**")
        if data.witnesses:
            for w in data.witnesses:
                st.write(f"• {w}")
        else:
            st.caption("None yet")

    with st.expander("Raw JSON"):
        st.json(data.model_dump())

    st.markdown(f"**Stage:** `{st.session_state.engine.current_stage}`")
