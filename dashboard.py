import json
from typing import Counter
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

# 3. Plotting Annotation Statistics

# 3-1. Utterance Type Distribution
st.subheader("NL Utterance Type Distribution")
try:
    utterance_type_counts = annotation_df["nl_type"].value_counts()
    fig_type = px.pie(values=utterance_type_counts.values, names=utterance_type_counts.index, title="NL Utterance Types")
    st.plotly_chart(fig_type)
except Exception as e:
    st.error("Error loading chart: No data")

# 3-2.Utterance Quality Distribution
st.subheader("NL Utterance Quality Distribution")
try:
    utterance_quality_counts = annotation_df["nl_quality"].value_counts()
    #fig_quality = px.pie(values=utterance_quality_counts.values, names=utterance_quality_counts.index, title="NL Utterance Quality")
    utterance_quality_percentages = (utterance_quality_counts / utterance_quality_counts.sum() * 100).round(2)
    fig_quality = px.bar(
        x=utterance_quality_counts.values,
        y=utterance_quality_counts.index,
        orientation="h",
        title="NL Utterance Quality",
        text=utterance_quality_percentages.apply(lambda x: f"{x}%")  # Display percentage on bars
    )
    fig_quality.update_traces(textposition="outside")
    st.plotly_chart(fig_quality)
except Exception as e:
    st.error("Error loading chart: No data")

# 3-3. Error Type Distribution (allowing multiple error types)
st.subheader("Error Type Distribution")
try:
    error_type_counts = annotation_df["nl_error_type"].explode().value_counts()
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
except Exception as e:
    st.error("Error loading chart: No data")

# 3-4. Chart Annotation Distribution
st.subheader("Chart Annotation Distribution")
try:
    # Initialize a Counter to count occurrences of each chart annotation
    chart_annotation_counts = Counter()

    # Iterate over all pages and extract chart annotation data
    for page, annotations in annotation_data.items():
        if "chart_annotation" in annotations:
            chart_annotation_counts.update(annotations["chart_annotation"].values())

    # Convert the Counter to a Series for easy plotting
    chart_annotation_counts_series = pd.Series(chart_annotation_counts)

    # Plot the chart annotation distribution using a bar chart
    fig_chart_annotation = px.bar(
        x=chart_annotation_counts_series.index,
        y=chart_annotation_counts_series.values,
        title="Chart Annotation Distribution"
    )
    st.plotly_chart(fig_chart_annotation)
except Exception as e:
    st.error("Error loading chart: No data")