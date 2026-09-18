import streamlit as st

from src.tools import get_airport_metrics
from src.agents.react_agent import ReActAgent
from src.guardrails.approval import HumanApproval


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Airport Operations AI Copilot",
    page_icon="✈️",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("✈️ Airport Operations AI Copilot")

st.write(
    "AI-powered assistant for investigating airport operations, "
    "retrieving policies, recommending actions, and managing "
    "human approval for sensitive actions."
)


# ============================================================
# SESSION STATE
# ============================================================

if "agent" not in st.session_state:
    st.session_state["agent"] = ReActAgent()

if "approval_handler" not in st.session_state:
    st.session_state["approval_handler"] = HumanApproval()

if "agent_result" not in st.session_state:
    st.session_state["agent_result"] = None

if "approval_request" not in st.session_state:
    st.session_state["approval_request"] = None


agent = st.session_state["agent"]
approval_handler = st.session_state["approval_handler"]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Airport Configuration")

airport_code = st.sidebar.selectbox(
    "Select Airport",
    ["SFO", "LAX", "JFK"]
)

st.sidebar.markdown("---")

st.sidebar.subheader("System Components")

st.sidebar.write("✅ RAG Knowledge Base")
st.sidebar.write("✅ FAISS Vector Search")
st.sidebar.write("✅ Operations Investigator")
st.sidebar.write("✅ Policy & Compliance Agent")
st.sidebar.write("✅ Resolution Agent")
st.sidebar.write("✅ ReAct Agent")
st.sidebar.write("✅ Short-term Memory")
st.sidebar.write("✅ Long-term Memory")
st.sidebar.write("✅ Guardrails")
st.sidebar.write("✅ Human-in-the-Loop")


# ============================================================
# OPERATIONAL DASHBOARD
# ============================================================

st.header(f"📊 {airport_code} Operational Dashboard")

metrics_result = get_airport_metrics(airport_code)

if metrics_result.get("status") == "success":

    metrics = metrics_result

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Completion Rate",
            f"{metrics['completion_rate']:.0f}%"
        )

    with col2:
        st.metric(
            "Average ETA",
            f"{metrics['average_eta']:.0f} min"
        )

    with col3:
        st.metric(
            "Queue Size",
            f"{metrics['queue_size']}"
        )

    with col4:
        st.metric(
            "Surge Multiplier",
            f"{metrics['surge_multiplier']:.1f}x"
        )

    st.markdown("### Additional Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Active Drivers",
            f"{metrics['active_drivers']}"
        )

    with col2:
        st.metric(
            "Cancellation Rate",
            f"{metrics['cancellation_rate']:.0f}%"
        )

    with col3:
        st.metric(
            "Request Volume",
            f"{metrics['request_volume']}"
        )

    with col4:
        st.metric(
            "Timestamp",
            metrics["timestamp"]
        )

else:

    st.error(
        metrics_result.get(
            "message",
            "Unable to retrieve airport metrics."
        )
    )


# ============================================================
# QUERY INPUT
# ============================================================

st.header("💬 Ask the Copilot")

query = st.text_area(
    "Enter your operational question",
    placeholder=(
        "Example: What is happening at SFO and should we "
        "increase surge to 1.4x?"
    ),
    height=100
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🔍 Analyze",
    type="primary",
    use_container_width=True
):

    if not query.strip():

        st.warning("Please enter a question before analyzing.")

    else:

        # Reset approval from any previous analysis
        st.session_state["approval_request"] = None

        with st.spinner(
            "Copilot is investigating airport operations..."
        ):

            result = agent.run(query)

        st.session_state["agent_result"] = result

        st.rerun()


# ============================================================
# DISPLAY RESULTS
# ============================================================

result = st.session_state.get("agent_result")


if result:

    # --------------------------------------------------------
    # BASIC RESULT VALIDATION
    # --------------------------------------------------------

    if result.get("status") != "success":

        st.error(
            result.get(
                "message",
                "Agent execution failed."
            )
        )

    else:

        workflow_result = result.get(
            "result",
            {}
        )

        investigation = workflow_result.get(
            "investigation",
            {}
        )

        compliance = workflow_result.get(
            "compliance",
            {}
        )

        resolution = workflow_result.get(
            "resolution",
            {}
        )

        requested_multiplier = workflow_result.get(
            "requested_multiplier"
        )

        # ====================================================
        # COPILOT RECOMMENDATION
        # ====================================================

        st.header("🤖 Copilot Recommendation")

        recommended_action = resolution.get(
            "recommended_action",
            "No recommendation available"
        )

        approval_required = compliance.get(
            "approval_required",
            False
        )

        if approval_required:

            st.warning(
                "⚠️ Human approval is required before "
                "the requested action can be executed."
            )

        elif recommended_action == "monitor":

            st.info(
                "The current situation can be monitored "
                "without taking a sensitive action."
            )

        elif recommended_action == "driver_incentive":

            st.info(
                "The agent recommends a driver incentive "
                "to address the operational issue."
            )

        elif recommended_action == "block_requested_action":

            st.error(
                "The requested action is blocked because "
                "it violates the applicable policy."
            )

        else:

            st.info(
                f"Recommended action: {recommended_action}"
            )

        st.write(
            f"**Recommended Action:** "
            f"`{recommended_action}`"
        )


        # ====================================================
        # OPERATIONAL FINDINGS
        # ====================================================

        st.header("🚦 Operational Findings")

        overall_status = investigation.get(
            "overall_status",
            "unknown"
        )

        st.write(
            f"**Overall Operational Status:** "
            f"`{overall_status}`"
        )

        findings = investigation.get(
            "findings",
            []
        )

        if findings:

            for finding in findings:

                if isinstance(finding, dict):

                    metric = finding.get(
                        "metric",
                        "Operational metric"
                    )

                    value = finding.get(
                        "value",
                        "N/A"
                    )

                    threshold = finding.get(
                        "threshold",
                        "N/A"
                    )

                    severity = finding.get(
                        "severity",
                        "N/A"
                    )

                    st.write(
                        f"- **{metric}**: "
                        f"{value} "
                        f"(threshold: {threshold}) "
                        f"— severity: `{severity}`"
                    )

                else:

                    st.write(f"- {finding}")

        else:

            st.success(
                "No significant operational findings."
            )


        # ====================================================
        # POLICY & COMPLIANCE
        # ====================================================

        st.header("📚 Policy & Compliance")

        compliance_status = compliance.get(
            "compliance_status",
            "unknown"
        )

        st.write(
            f"**Compliance Status:** "
            f"`{compliance_status}`"
        )

        st.write(
            f"**Approval Required:** "
            f"`{approval_required}`"
        )

        if requested_multiplier is not None:

            st.write(
                f"**Requested Surge Multiplier:** "
                f"`{requested_multiplier}x`"
            )

        compliance_findings = compliance.get(
            "findings",
            []
        )

        if compliance_findings:

            st.markdown("**Policy Findings:**")

            for finding in compliance_findings:

                st.write(f"- {finding}")


        # ====================================================
        # RESOLUTION
        # ====================================================

        st.header("🛠️ Resolution")

        st.write(
            f"**Recommended Action:** "
            f"`{recommended_action}`"
        )

        recommendations = resolution.get(
            "recommendations",
            []
        )

        if recommendations:

            for recommendation in recommendations:

                priority = recommendation.get(
                    "priority",
                    "N/A"
                )

                reason = recommendation.get(
                    "reason",
                    "No reason provided."
                )

                execution_allowed = recommendation.get(
                    "execution_allowed",
                    False
                )

                st.write(
                    f"**Priority:** `{priority}`"
                )

                st.write(
                    f"**Reason:** {reason}"
                )

                st.write(
                    f"**Execution Allowed:** "
                    f"`{execution_allowed}`"
                )


        # ====================================================
        # AGENT ACTIVITY TRACE
        # ====================================================

        st.header("🧠 Agent Activity Trace")

        trace = result.get(
            "trace",
            []
        )

        if trace:

            with st.expander(
                "View agent reasoning / activity trace",
                expanded=True
            ):

                for step in trace:

                    iteration = step.get(
                        "iteration",
                        "?"
                    )

                    step_type = step.get(
                        "type",
                        "unknown"
                    )

                    tool = step.get(
                        "tool"
                    )

                    content = step.get(
                        "content",
                        ""
                    )

                    if tool:

                        st.write(
                            f"**Iteration {iteration} — "
                            f"{step_type} — {tool}**"
                        )

                    else:

                        st.write(
                            f"**Iteration {iteration} — "
                            f"{step_type}**"
                        )

                    st.write(content)

                    st.markdown("---")

        else:

            st.info("No agent trace available.")


        # ====================================================
        # RAG / POLICY TRACE
        # ====================================================

        st.header("🔎 RAG / Policy Retrieval Trace")

        sources = compliance.get(
            "sources",
            []
        )

        retrieved_chunks = compliance.get(
            "retrieved_chunks",
            []
        )

        with st.expander(
            "View retrieved policy information",
            expanded=False
        ):

            if sources:

                st.markdown("### Source Documents")

                for source in sources:

                    st.write(
                        f"- `{source}`"
                    )

            else:

                st.write(
                    "No source documents available."
                )

            if retrieved_chunks:

                st.markdown("### Retrieved Chunks")

                for index, chunk in enumerate(
                    retrieved_chunks,
                    start=1
                ):

                    st.markdown(
                        f"**Chunk {index}**"
                    )

                    if isinstance(chunk, dict):

                        source = chunk.get(
                            "source",
                            "Unknown source"
                        )

                        content = chunk.get(
                            "content",
                            str(chunk)
                        )

                        st.write(
                            f"**Source:** `{source}`"
                        )

                        st.write(content)

                    else:

                        st.write(chunk)

                    st.markdown("---")

            else:

                st.write(
                    "No retrieved chunks available."
                )


        # ====================================================
        # HUMAN-IN-THE-LOOP APPROVAL
        # ====================================================

        st.header("👤 Human Approval")

        if approval_required:

            st.warning(
                "This action requires explicit human "
                "approval before execution."
            )

            # -----------------------------------------------
            # CREATE APPROVAL REQUEST
            # -----------------------------------------------

            approval_request = st.session_state.get(
                "approval_request"
            )

            if approval_request is None:

                recommendations = resolution.get(
                    "recommendations",
                    []
                )

                reason = (
                    "High-risk action requires human approval."
                )

                if recommendations:

                    reason = recommendations[0].get(
                        "reason",
                        reason
                    )

                approval_request = (
                    approval_handler.request_approval(
                        airport_code=airport_code,
                        action=resolution.get(
                            "recommended_action",
                            "request_human_approval"
                        ),
                        risk_level="high",
                        reason=reason,
                        requested_multiplier=(
                            requested_multiplier
                        )
                    )
                )

                st.session_state[
                    "approval_request"
                ] = approval_request

            # -----------------------------------------------
            # APPROVAL DETAILS
            # -----------------------------------------------

            approval_status = approval_request.get(
                "status",
                "pending"
            )

            st.write(
                f"**Approval ID:** "
                f"`{approval_request.get('approval_id', 'N/A')}`"
            )

            st.write(
                f"**Approval Status:** "
                f"`{approval_status}`"
            )

            st.write(
                f"**Risk Level:** "
                f"`{approval_request.get('risk_level', 'N/A')}`"
            )

            st.write(
                f"**Action:** "
                f"`{approval_request.get('action', 'N/A')}`"
            )

            if (
                approval_request.get(
                    "requested_multiplier"
                ) is not None
            ):

                st.write(
                    f"**Requested Surge:** "
                    f"`{approval_request['requested_multiplier']}x`"
                )

            st.write(
                f"**Reason:** "
                f"{approval_request.get('reason', 'N/A')}"
            )

            # -----------------------------------------------
            # APPROVAL BUTTONS
            # -----------------------------------------------

            if approval_status == "pending":

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approve Action",
                        type="primary",
                        use_container_width=True,
                        key="approve_action"
                    ):

                        updated_request = (
                            approval_handler.process_approval(
                                approval_request,
                                "approve",
                                approver=(
                                    "airport_operations_manager"
                                )
                            )
                        )

                        st.session_state[
                            "approval_request"
                        ] = updated_request

                        st.success(
                            "Action approved by "
                            "airport_operations_manager."
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "❌ Reject Action",
                        use_container_width=True,
                        key="reject_action"
                    ):

                        updated_request = (
                            approval_handler.process_approval(
                                approval_request,
                                "reject",
                                approver=(
                                    "airport_operations_manager"
                                )
                            )
                        )

                        st.session_state[
                            "approval_request"
                        ] = updated_request

                        st.error(
                            "Action rejected by "
                            "airport_operations_manager."
                        )

                        st.rerun()

            elif approval_status == "approved":

                st.success(
                    "✅ Action approved by "
                    f"{approval_request.get('approved_by', 'human operator')}."
                )

                if approval_request.get(
                    "approval_timestamp"
                ):

                    st.write(
                        f"**Approval Timestamp:** "
                        f"{approval_request['approval_timestamp']}"
                    )

            elif approval_status == "rejected":

                st.error(
                    "❌ Action rejected by "
                    f"{approval_request.get('approved_by', 'human operator')}."
                )

                if approval_request.get(
                    "approval_timestamp"
                ):

                    st.write(
                        f"**Decision Timestamp:** "
                        f"{approval_request['approval_timestamp']}"
                    )

        else:

            st.info(
                "No human approval is required "
                "for this request."
            )


        # ====================================================
        # EXECUTION RESULT
        # ====================================================

        st.header("⚙️ Execution Result")

        approval_request = st.session_state.get(
            "approval_request"
        )

        execution_allowed = False

        # -----------------------------------------------
        # APPROVAL OVERRIDES EXECUTION DECISION
        # -----------------------------------------------

        if approval_request:

            approval_status = approval_request.get(
                "status"
            )

            if approval_status == "approved":

                execution_allowed = True

            else:

                execution_allowed = False

        else:

            if recommendations:

                execution_allowed = recommendations[0].get(
                    "execution_allowed",
                    False
                )


        # -----------------------------------------------
        # DISPLAY EXECUTION STATUS
        # -----------------------------------------------

        if execution_allowed:

            st.success(
                "✅ Action approved and ready for execution."
            )

            st.write(
                "**Execution Status:** `Approved`"
            )

            st.write(
                f"**Airport:** `{airport_code}`"
            )

            if requested_multiplier is not None:

                st.write(
                    f"**Surge Multiplier:** "
                    f"`{requested_multiplier}x`"
                )

            st.info(
                "In this synthetic case study, the approval "
                "workflow is demonstrated without modifying "
                "a real airport system."
            )

        else:

            if approval_request:

                if approval_request.get("status") == "rejected":

                    st.error(
                        "❌ Action was rejected and "
                        "has not been executed."
                    )

                elif approval_request.get("status") == "pending":

                    st.warning(
                        "⏳ Action is pending human approval "
                        "and has not been executed."
                    )

                else:

                    st.info(
                        "Action has not been executed."
                    )

            elif compliance.get("approval_required"):

                st.warning(
                    "⏳ Human approval is required before "
                    "this action can be executed."
                )

            else:

                st.info(
                    "Action has not been executed."
                )


        # ====================================================
        # MEMORY INFORMATION
        # ====================================================

        st.header("🧠 Conversation Memory")

        previous_memories = result.get(
            "previous_memories",
            []
        )

        if previous_memories:

            with st.expander(
                "View retrieved long-term memories",
                expanded=False
            ):

                for memory in previous_memories:

                    st.write(
                        f"- {memory}"
                    )

        else:

            st.write(
                "No previous long-term memories were retrieved."
            )


        # ====================================================
        # AGENT ITERATION SUMMARY
        # ====================================================

        st.header("🔄 Agent Execution Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Iterations Used",
                result.get(
                    "iterations",
                    0
                )
            )

        with col2:

            st.metric(
                "Maximum Iterations",
                result.get(
                    "max_iterations",
                    5
                )
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Airport Operations AI Copilot | "
    "RAG + FAISS + Multi-Agent Workflow + "
    "Guardrails + Human-in-the-Loop"
)
