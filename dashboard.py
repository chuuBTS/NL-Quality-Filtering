import json
import streamlit as st
import pandas as pd
import plotly.express as px

# Load annotation data
with open("data/annotation_result.json", "r", encoding="utf-8") as file:
    annotation_data = json.load(file)

# 1. Annotation Progress
# Total records and completed annotations
total_records = 8442
completed_annotations = len(annotation_data)
progress = (completed_annotations / total_records) * 100

st.title("Annotation Dashboard")
st.caption("This dashboard provides an overview of the annotation progress and distribution of labeled data. "
           "You can explore the NL utterance types, quality ratings, and error types using interactive charts below.")

# 1. Display annotation progress
st.subheader("Annotation Progress")
st.progress(progress / 100)
st.markdown(f"**{completed_annotations} / {total_records}** records annotated ({progress:.2f}%)")

# 2. Aggregating Annotation Results
# Convert annotation data to DataFrame for easier analysis
annotation_df = pd.DataFrame.from_dict(annotation_data, orient="index")

# Fill NaN values for ease of plotting (assuming None values mean not yet marked)
annotation_df.fillna("Not Labeled", inplace=True)

# Calculate counts for each NL utterance type, quality, and error type
utterance_type_counts = annotation_df["nl_utterance_type"].value_counts()
utterance_quality_counts = annotation_df["nl_utterance_quality"].value_counts()
error_type_counts = annotation_df["error_type"].explode().value_counts()

# 3. Plotting Annotation Statistics

# Utterance Type Distribution
st.subheader("NL Utterance Type Distribution")
fig_type = px.pie(values=utterance_type_counts.values, names=utterance_type_counts.index, title="NL Utterance Types")
st.plotly_chart(fig_type)

# Utterance Quality Distribution
st.subheader("NL Utterance Quality Distribution")
#fig_quality = px.pie(values=utterance_quality_counts.values, names=utterance_quality_counts.index, title="NL Utterance Quality")
utterance_quality_percentages = (utterance_quality_counts / utterance_quality_counts.sum() * 100).round(2)
fig_quality = px.bar(
    x=utterance_quality_counts.index, 
    y=utterance_quality_counts.values, 
    title="NL Utterance Quality",
    text=utterance_quality_percentages.apply(lambda x: f"{x}%")  # Display percentage on bars
)
fig_quality.update_traces(textposition="outside")
st.plotly_chart(fig_quality)

# Error Type Distribution (allowing multiple error types)
st.subheader("Error Type Distribution")
fig_error = px.pie(values=error_type_counts.values, names=error_type_counts.index, title="Error Types")
# error_type_percentages = (error_type_counts / error_type_counts.sum() * 100).round(2)
# fig_error = px.bar(
#     x=error_type_counts.index, 
#     y=error_type_counts.values, 
#     title="Error Types",
#     text=error_type_percentages.apply(lambda x: f"{x}%")  # Display percentage on bars
# )
# fig_error.update_traces(textposition="outside")
st.plotly_chart(fig_error)
