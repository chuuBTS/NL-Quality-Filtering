import json
from typing import Counter
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Load merged data
with open("data/filtered_chart_types_result.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Load annotation data
with open("data/annotation_result.json", "r", encoding="utf-8") as file:
    annotation_data = json.load(file)

# 1. Annotation Progress
# Total records and completed annotations
total_records = len(data)
completed_annotations = len(annotation_data)
progress = (completed_annotations / total_records) * 100

st.title("Annotation Dashboard")
st.caption("This dashboard provides an overview of the annotation progress and distribution of labeled data. "
           "You can explore the NL types, quality ratings, and error types using interactive charts below.")

# 1. Display annotation progress
# Part 1: NL Annotation Progress
st.markdown('<h4 style="color:green;">NL Annotation Progress</h3>', unsafe_allow_html=True)

try:
    # Total NL records from data
    total_nl = len(data)
    
    # Count NL annotated records
    nl_annotated = sum(1 for record in annotation_data.values() if "nl_type" in record)
    nl_progress = (nl_annotated / total_nl) * 100 if total_nl > 0 else 0

    # Progress bar for NL annotation
    st.progress(nl_progress / 100)
    st.markdown(f"**{nl_annotated} / {total_nl}** NL records annotated ({nl_progress:.2f}%)")

except Exception as e:
    st.error("Error loading NL Annotation Progress: No data or invalid format")

# Part 2: Chart Annotation Progress
st.markdown('<h4 style="color:green;">Charts Annotation Progress</h3>', unsafe_allow_html=True)
try:
    # Total charts from data
    total_charts = sum(len(record.get("generated_chart_list", [])) for record in data.values())

    # Annotated charts
    annotated_charts = 0
    for record in annotation_data.values():
        if "charts" in record:
            for chart_data in record["charts"].values():
                if "chart_quality" in chart_data and chart_data["chart_quality"] != "Not Labeled":
                    annotated_charts += 1

    chart_progress = (annotated_charts / total_charts) * 100 if total_charts > 0 else 0

    # Progress bar for chart annotation
    st.progress(chart_progress / 100)
    st.markdown(f"**{annotated_charts} / {total_charts}** charts annotated ({chart_progress:.2f}%)")

except Exception as e:
    st.error("Error loading Chart Annotation Progress: No data or invalid format")


# 2. Aggregating Annotation Results
# Convert annotation data to DataFrame for easier analysis
annotation_df = pd.DataFrame.from_dict(annotation_data, orient="index")

# Fill NaN values for ease of plotting (assuming None values mean not yet marked)
annotation_df.fillna("Not Labeled", inplace=True)

# 3. Plotting Annotation Statistics

# 3-1. Utterance Type Distribution
st.subheader("NL Type Distribution")
try:
    utterance_type_counts = annotation_df["nl_type"].value_counts()
    
    # Create two columns for pie and bar charts
    col1, col2, col3 =st.columns([3, 1, 3])

    with col1:
        fig_type_bar = px.bar(
            x=utterance_type_counts.values, 
            y=utterance_type_counts.index,
            orientation="h",
            title="NL Types (Bar)",
            text=utterance_type_counts.values
        )
        fig_type_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_type_bar)
    
    with col3:
        fig_type = px.pie(values=utterance_type_counts.values, names=utterance_type_counts.index, title="NL Types (Pie)")
        st.plotly_chart(fig_type)       
        
except Exception as e:
    st.error("Error loading chart: No data")

# 3-2.Utterance Quality Distribution
# st.subheader("NL Quality Distribution")
# try:
#     utterance_quality_counts = annotation_df["nl_quality"].value_counts()
    
#     # Create two columns for pie and bar charts
#     col1, col2, col3 =st.columns([3, 1, 3])

#     with col1:
#         fig_quality = px.bar(
#         x=utterance_quality_counts.values,
#         y=utterance_quality_counts.index,
#         orientation="h",
#         title="NL Quality (Bar)",
#         text=utterance_quality_counts.values
#         )
#         fig_quality.update_traces(textposition="outside")
#         st.plotly_chart(fig_quality)
    
#     with col3:
#         fig_quality = px.pie(values=utterance_quality_counts.values, names=utterance_quality_counts.index, title="NL Quality (Pie)")
#         st.plotly_chart(fig_quality)
    
# except Exception as e:
#     st.error("Error loading chart: No data")

# 3-3. Error Type Distribution (allowing multiple error types)
# st.subheader("Error Type Distribution")
# try:
#     error_type_counts = annotation_df["nl_error_type"].explode().value_counts()
    
#     # Create two columns for pie and bar charts
#     col1, col2, col3 =st.columns([3, 1, 3])
    
#     with col1:
#         fig_error = px.bar(
#             x=error_type_counts.index, 
#             y=error_type_counts.values, 
#             title="Error Types (Bar)",
#             text=error_type_counts.values
#         )
#         fig_error.update_traces(textposition="outside")
#         st.plotly_chart(fig_error)
        
#     with col3:
#         fig_error = px.pie(values=error_type_counts.values, names=error_type_counts.index, title="Error Types (Pie)")
#         st.plotly_chart(fig_error)
        
# except Exception as e:
#     st.error("Error loading chart: No data")

# 3-4. Chart Annotation Distribution
# st.subheader("Chart Annotation Distribution")
# try:
#     # Initialize a Counter to count occurrences of each chart annotation
#     chart_annotation_counts = Counter()

#     # Iterate over all pages and extract chart annotation data
#     for page, annotations in annotation_data.items():
#         if "chart_annotation" in annotations:
#             chart_annotation_counts.update(annotations["chart_annotation"].values())

#     # Convert the Counter to a Series for easy plotting
#     chart_annotation_counts_series = pd.Series(chart_annotation_counts)

#      # Create two columns for pie and bar charts
#     col1, col2, col3 =st.columns([3, 1, 3])
    
#     with col1:
#         fig_chart_annotation = px.bar(
#             x=chart_annotation_counts_series.index,
#             y=chart_annotation_counts_series.values,
#             title="Chart Annotation Distribution (Bar)",
#             text=chart_annotation_counts_series.values
#         )
#         st.plotly_chart(fig_chart_annotation)
    
#     with col3:
#         fig_chart_annotation = px.pie(
#             values=chart_annotation_counts_series.values,
#             names=chart_annotation_counts_series.index,
#             title="Chart Annotation Distribution (Pie)"
#         )
#         st.plotly_chart(fig_chart_annotation)

# except Exception as e:
#     st.error("Error loading chart: No data")

# 3-5. Chart Type Distribution
st.subheader("Chart Type Distribution")
try:
    # Initialize a Counter to count occurrences of each chart type (mark)
    chart_type_counts = Counter()

    # Iterate over the data in filtered_chart_types_result.json
    for record in data.values():
        # Loop through each generated chart list and count the marks (chart types)
        for chart in record.get("generated_chart_list", []):
            chart_type = chart.get("mark")
            if chart_type:
                chart_type_counts[chart_type] += 1

    # Convert the Counter to a Series for easier plotting
    chart_type_counts_series = pd.Series(chart_type_counts)

    # Create two columns for pie and bar charts
    col1, col2, col3 = st.columns([3, 1, 3])

    with col1:
        # Bar chart for chart type distribution
        fig_chart_type_bar = px.bar(
            x=chart_type_counts_series.index,
            y=chart_type_counts_series.values,
            title="Chart Type Distribution (Bar)",
            text=chart_type_counts_series.values
        )
        fig_chart_type_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_chart_type_bar)
    
    with col3:
        # Pie chart for chart type distribution
        fig_chart_type_pie = px.pie(
            values=chart_type_counts_series.values,
            names=chart_type_counts_series.index,
            title="Chart Type Distribution (Pie)"
        )
        st.plotly_chart(fig_chart_type_pie)

except Exception as e:
    st.error("Error loading Chart Type Distribution: No data or invalid format")

# 3-6. NL to Chart Count Distribution
st.subheader("NL to Chart Count Distribution")
try:
    # Initialize a list to store the number of charts per NL utterance
    nl_to_chart_counts = []

    # Iterate over the data in filtered_chart_types_result.json
    for record in data.values():
        # Count the number of charts for each NL utterance
        chart_count = len(record.get("generated_chart_list", []))
        if chart_count > 0:
            nl_to_chart_counts.append(chart_count)

    # Count the distribution of chart counts (1 chart, 2 charts, etc.)
    chart_count_distribution = Counter(nl_to_chart_counts)

    # Convert the Counter to a Series for easier plotting
    chart_count_distribution_series = pd.Series(chart_count_distribution).sort_index()

    # Bar chart for NL to chart count distribution
    fig_nl_chart_count = px.bar(
        x=chart_count_distribution_series.index,
        y=chart_count_distribution_series.values,
        title="NL to Chart Count Distribution",
        labels={"x": "Number of Charts", "y": "Number of NL Utterances"},
        text=chart_count_distribution_series.values
    )
    fig_nl_chart_count.update_traces(textposition="outside")
    st.plotly_chart(fig_nl_chart_count)

except Exception as e:
    st.error("Error loading NL to Chart Count Distribution: No data or invalid format")


# Part 1: Chart Quality Distribution
st.subheader("Chart Quality Distribution")
try:
    # Initialize a Counter to count occurrences of chart quality
    chart_quality_counts = Counter()

    # Iterate over all pages and extract chart quality data
    for page, annotations in annotation_data.items():
        if "charts" in annotations:
            for chart_id, chart_data in annotations["charts"].items():
                if "chart_quality" in chart_data:
                    chart_quality_counts[chart_data["chart_quality"]] += 1

    # Convert the Counter to a Series for easy plotting
    chart_quality_series = pd.Series(chart_quality_counts)

    # Create two columns for pie and bar charts
    col1, col2, col3 = st.columns([3, 1, 3])

    with col1:
        fig_chart_quality_bar = px.bar(
            x=chart_quality_series.index,
            y=chart_quality_series.values,
            title="Chart Quality Distribution (Bar)",
            text=chart_quality_series.values,
        )
        fig_chart_quality_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_chart_quality_bar)

    with col3:
        fig_chart_quality_pie = px.pie(
            values=chart_quality_series.values,
            names=chart_quality_series.index,
            title="Chart Quality Distribution (Pie)",
        )
        st.plotly_chart(fig_chart_quality_pie)

except Exception as e:
    st.error("Error loading Chart Quality Distribution: No data or invalid format")

# Part 2: Chart Error Type Distribution
st.subheader("Chart Error Type Distribution")
try:
    # Initialize a Counter to count occurrences of error types
    chart_error_type_counts = Counter()

    # Iterate over all pages and extract error type data
    for page, annotations in annotation_data.items():
        if "charts" in annotations:
            for chart_id, chart_data in annotations["charts"].items():
                if "error_type" in chart_data:
                    chart_error_type_counts.update(chart_data["error_type"])

    # Convert the Counter to a Series for easy plotting
    chart_error_type_series = pd.Series(chart_error_type_counts)

    # Create two columns for pie and bar charts
    col1, col2, col3 = st.columns([3, 1, 3])

    with col1:
        fig_chart_error_type_bar = px.bar(
            x=chart_error_type_series.index,
            y=chart_error_type_series.values,
            title="Chart Error Type Distribution (Bar)",
            text=chart_error_type_series.values,
        )
        fig_chart_error_type_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_chart_error_type_bar)

    with col3:
        fig_chart_error_type_pie = px.pie(
            values=chart_error_type_series.values,
            names=chart_error_type_series.index,
            title="Chart Error Type Distribution (Pie)",
        )
        st.plotly_chart(fig_chart_error_type_pie)

except Exception as e:
    st.error("Error loading Chart Error Type Distribution: No data or invalid format")
