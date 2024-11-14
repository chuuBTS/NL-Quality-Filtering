import json
from typing import Counter
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

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
    
    # Create two columns for pie and bar charts
    col1, col2, col3 =st.columns([3, 1, 3])

    with col1:
        fig_type_bar = px.bar(
            x=utterance_type_counts.values, 
            y=utterance_type_counts.index,
            orientation="h",
            title="NL Utterance Types (Bar)",
            text=utterance_type_counts.values
        )
        fig_type_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_type_bar)
    
    with col3:
        fig_type = px.pie(values=utterance_type_counts.values, names=utterance_type_counts.index, title="NL Utterance Types (Pie)")
        st.plotly_chart(fig_type)       
        
except Exception as e:
    st.error("Error loading chart: No data")

# 3-2.Utterance Quality Distribution
st.subheader("NL Utterance Quality Distribution")
try:
    utterance_quality_counts = annotation_df["nl_quality"].value_counts()
    
    # Create two columns for pie and bar charts
    col1, col2, col3 =st.columns([3, 1, 3])

    with col1:
        fig_quality = px.bar(
        x=utterance_quality_counts.values,
        y=utterance_quality_counts.index,
        orientation="h",
        title="NL Utterance Quality (Bar)",
        text=utterance_quality_counts.values
        )
        fig_quality.update_traces(textposition="outside")
        st.plotly_chart(fig_quality)
    
    with col3:
        fig_quality = px.pie(values=utterance_quality_counts.values, names=utterance_quality_counts.index, title="NL Utterance Quality (Pie)")
        st.plotly_chart(fig_quality)
    
except Exception as e:
    st.error("Error loading chart: No data")

# 3-3. Error Type Distribution (allowing multiple error types)
st.subheader("Error Type Distribution")
try:
    error_type_counts = annotation_df["nl_error_type"].explode().value_counts()
    
    # Create two columns for pie and bar charts
    col1, col2, col3 =st.columns([3, 1, 3])
    
    with col1:
        fig_error = px.bar(
            x=error_type_counts.index, 
            y=error_type_counts.values, 
            title="Error Types (Bar)",
            text=error_type_counts.values
        )
        fig_error.update_traces(textposition="outside")
        st.plotly_chart(fig_error)
        
    with col3:
        fig_error = px.pie(values=error_type_counts.values, names=error_type_counts.index, title="Error Types (Pie)")
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

     # Create two columns for pie and bar charts
    col1, col2, col3 =st.columns([3, 1, 3])
    
    with col1:
        fig_chart_annotation = px.bar(
            x=chart_annotation_counts_series.index,
            y=chart_annotation_counts_series.values,
            title="Chart Annotation Distribution (Bar)",
            text=chart_annotation_counts_series.values
        )
        st.plotly_chart(fig_chart_annotation)
    
    with col3:
        fig_chart_annotation = px.pie(
            values=chart_annotation_counts_series.values,
            names=chart_annotation_counts_series.index,
            title="Chart Annotation Distribution (Pie)"
        )
        st.plotly_chart(fig_chart_annotation)

except Exception as e:
    st.error("Error loading chart: No data")