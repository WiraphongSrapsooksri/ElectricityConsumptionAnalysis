import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Function to format numbers in "K" or "M"
def format_number(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return f"{value:.2f}"

# Function to convert month number to name
def month_name(month_num):
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    return month_names.get(month_num, "")

# Load Dataset
@st.cache
def load_data():
    data = pd.read_csv("combined_dataset.csv", parse_dates=["DateTime"])
    data['MonthName'] = data['Month'].apply(lambda x: month_name(int(x)))  # Add MonthName column
    return data

# Main App
def main():
    st.title("Electricity Consumption Dashboard")

    # Load Data
    data = load_data()

    # Sidebar Filters
    st.sidebar.title("Filters")
    year_filter = st.sidebar.multiselect("Select Year(s)", options=data['Year'].unique(), default=data['Year'].unique())
    month_filter = st.sidebar.multiselect("Select Month(s)", options=data['Month'].unique(), default=data['Month'].unique())
    day_filter = st.sidebar.slider("Select Day Range", min_value=1, max_value=31, value=(1, 31))

    # Dynamic Header Title
    if len(year_filter) > 0:
        start_year = min(year_filter)
        end_year = max(year_filter)
        duration = len(year_filter)
        dynamic_title = f"Electricity Consumption Analysis for {start_year} - {end_year} (Over {duration} Year{'s' if duration > 1 else ''})"
    else:
        dynamic_title = "Electricity Consumption Analysis"

    st.markdown(f"## {dynamic_title}")

    # Filter Data
    filtered_data = data[
        (data['Year'].isin(year_filter)) &
        (data['Month'].isin(month_filter)) &
        (data['DateTime'].dt.day.between(day_filter[0], day_filter[1]))
    ]

    # Overview Metrics
    st.markdown("### Overall Metrics")
    total_energy = filtered_data['Total'].sum()
    avg_energy = filtered_data['Total'].mean()
    st.metric("Total Energy (kWh)", f"{total_energy:,.2f}")
    st.metric("Average Energy per Interval (kWh)", format_number(avg_energy))

    # Yearly Analysis
    st.markdown(f"### Yearly Electricity Consumption ({start_year} - {end_year})")
    yearly_data = filtered_data.groupby('Year')['Total'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = sns.barplot(x='Year', y='Total', data=yearly_data, ax=ax, color="skyblue")
    for i, bar in enumerate(bars.patches):
        value = yearly_data.iloc[i]['Total']
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(yearly_data['Total']) * 0.01,
                format_number(value), ha='center', va='bottom', fontsize=10)
    ax.set_title("Yearly Electricity Consumption")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Energy (kWh)")
    st.pyplot(fig)

    # Interactive Line Chart for Monthly Data
    st.markdown("### Monthly Electricity Consumption (Interactive)")
    monthly_data = filtered_data.groupby(['Year', 'Month', 'MonthName'])['Total'].sum().reset_index()
    fig = px.line(
        monthly_data,
        x="MonthName",
        y="Total",
        color="Year",
        markers=True,
        title="Monthly Electricity Consumption",
        labels={"MonthName": "Month", "Total": "Total Energy (kWh)", "Year": "Year"},
    )
    fig.update_traces(mode="lines+markers", hovertemplate="Month: %{x}<br>Total: %{y:,.2f} kWh<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

    # # Daily Trends
    # st.markdown("### Daily Trends")
    # daily_data = filtered_data.groupby(filtered_data['DateTime'].dt.hour)['Total'].mean().reset_index()
    # fig, ax = plt.subplots(figsize=(10, 6))
    # sns.lineplot(x='DateTime', y='Total', data=daily_data, ax=ax, marker="o", color="blue")
    # ax.set_title("Average Electricity Usage by Hour")
    # ax.set_xlabel("Hour")
    # ax.set_ylabel("Average Energy (kWh)")
    # st.pyplot(fig)

    # Daily Trends (Interactive Line Chart)
    st.markdown("### Daily Trends (Interactive)")
    daily_data = filtered_data.groupby(filtered_data['DateTime'].dt.hour)['Total'].mean().reset_index()
    fig = px.line(
        daily_data,
        x="DateTime",
        y="Total",
        title="Average Electricity Usage by Hour",
        labels={"DateTime": "Hour", "Total": "Average Energy (kWh)"},
    )
    fig.update_traces(mode="lines+markers", hovertemplate="Hour: %{x}<br>Average: %{y:,.2f} kWh<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)


    # # Heatmap
    # st.markdown("### Hourly Electricity Usage Heatmap")
    # heatmap_data = filtered_data.pivot_table(index=filtered_data['DateTime'].dt.hour, 
    #                                          columns=filtered_data['DateTime'].dt.day, 
    #                                          values='Total', aggfunc='mean')
    # fig, ax = plt.subplots(figsize=(12, 8))
    # sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax, cbar_kws={'label': 'Energy (kWh)'})
    # ax.set_title("Hourly Electricity Usage Heatmap")
    # st.pyplot(fig)
    # Hourly Electricity Usage Heatmap (Interactive)
    st.markdown("### Hourly Electricity Usage Heatmap (Interactive)")
    heatmap_data = filtered_data.pivot_table(index=filtered_data['DateTime'].dt.hour, 
                                             columns=filtered_data['DateTime'].dt.day, 
                                             values='Total', aggfunc='mean').reset_index()

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.iloc[:, 1:].values,  # Heatmap values
        x=heatmap_data.columns[1:],  # Day columns
        y=heatmap_data['DateTime'],  # Hour index
        colorscale='YlGnBu',
        hoverongaps=False,
        colorbar=dict(title="Energy (kWh)")
    ))
    fig.update_layout(
        title="Hourly Electricity Usage Heatmap",
        xaxis=dict(title="Day"),
        yaxis=dict(title="Hour"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # # Interactive Table
    # st.markdown("### Filtered Data Table")
    # st.dataframe(filtered_data)

    # Language Selection
    st.sidebar.title("Language / ภาษา")
    language = st.sidebar.radio("Choose Language / เลือกภาษา", options=["English", "ภาษาไทย"])

    # Summary Section
    st.markdown("## Summary Insights / สรุปข้อมูล")

    # Helper function for bilingual text
    def bilingual_text(th, en):
        return th if language == "ภาษาไทย" else en

    # 1. Year with maximum and minimum electricity usage
    yearly_usage = filtered_data.groupby('Year')['Total'].sum()
    max_year = yearly_usage.idxmax()
    min_year = yearly_usage.idxmin()
    st.markdown(f"- {bilingual_text('ปีที่ใช้ไฟฟ้ามากที่สุด:', 'Year with the highest electricity usage:')} {max_year} ({format_number(yearly_usage[max_year])} kWh)")
    st.markdown(f"- {bilingual_text('ปีที่ใช้ไฟฟ้าน้อยที่สุด:', 'Year with the lowest electricity usage:')} {min_year} ({format_number(yearly_usage[min_year])} kWh)")

    # 2. Month with maximum and minimum electricity usage
    monthly_usage = filtered_data.groupby('Month')['Total'].sum()
    max_month = monthly_usage.idxmax()
    min_month = monthly_usage.idxmin()
    max_month_name = month_name(int(max_month))
    min_month_name = month_name(int(min_month))
    st.markdown(f"- {bilingual_text('เดือนที่ใช้ไฟฟ้ามากที่สุด:', 'Month with the highest electricity usage:')} {max_month_name} ({format_number(monthly_usage[max_month])} kWh)")
    st.markdown(f"- {bilingual_text('เดือนที่ใช้ไฟฟ้าน้อยที่สุด:', 'Month with the lowest electricity usage:')} {min_month_name} ({format_number(monthly_usage[min_month])} kWh)")

    # 3. Hour with maximum and minimum electricity usage
    hourly_usage = filtered_data.groupby(filtered_data['DateTime'].dt.hour)['Total'].sum()
    max_hour = hourly_usage.idxmax()
    min_hour = hourly_usage.idxmin()
    st.markdown(f"- {bilingual_text('ช่วงเวลาที่ใช้ไฟฟ้ามากที่สุด:', 'Hour with the highest electricity usage:')} {max_hour}:00 ({format_number(hourly_usage[max_hour])} kWh)")
    st.markdown(f"- {bilingual_text('ช่วงเวลาที่ใช้ไฟฟ้าน้อยที่สุด:', 'Hour with the lowest electricity usage:')} {min_hour}:00 ({format_number(hourly_usage[min_hour])} kWh)")

    # 4. DateTime with the highest electricity usage
    max_total = filtered_data['Total'].max()
    max_total_row = filtered_data[filtered_data['Total'] == max_total]
    max_datetime = max_total_row['DateTime'].iloc[0]
    st.markdown(f"- {bilingual_text('วันที่และเวลาที่ใช้ไฟฟ้ามากที่สุด:', 'DateTime with the highest electricity usage:')} {max_datetime} ({format_number(max_total)} kWh)")

    # 5. RATE Analysis (A, B, C)
    st.markdown(bilingual_text("### การวิเคราะห์ RATE (A, B, C)", "### RATE Analysis (A, B, C)"))
    rate_stats = {}
    for rate in ['RATE A', 'RATE B', 'RATE C']:
        max_rate = filtered_data[rate].max()
        min_rate = filtered_data[rate].min()
        avg_rate = filtered_data[rate].mean()
        std_rate = filtered_data[rate].std()
        rate_stats[rate] = {
            "Max": max_rate,
            "Min": min_rate,
            "Avg": avg_rate,
            "Std Dev": std_rate
        }
        st.markdown(f"- **{rate}:**")
        st.markdown(f"  - {bilingual_text('ค่าสูงสุด:', 'Maximum:')} {format_number(max_rate)}")
        st.markdown(f"  - {bilingual_text('ค่าต่ำสุด:', 'Minimum:')} {format_number(min_rate)}")
        st.markdown(f"  - {bilingual_text('ค่าเฉลี่ย:', 'Average:')} {format_number(avg_rate)}")
        st.markdown(f"  - {bilingual_text('ส่วนเบี่ยงเบนมาตรฐาน:', 'Standard Deviation:')} {format_number(std_rate)}")

    # Additional Insights
    st.markdown(bilingual_text("### การวิเคราะห์เพิ่มเติม", "### Additional Insights"))
    # Identify the most frequent hour with peak usage
    peak_hour_freq = filtered_data[filtered_data['Total'] == filtered_data['Total'].max()]['DateTime'].dt.hour.mode()[0]
    st.markdown(f"- {bilingual_text('ช่วงเวลาที่เกิด Peak สูงสุดบ่อยที่สุด:', 'Most frequent peak usage hour:')} {peak_hour_freq}:00")

    # Find the distribution of usage across weekdays
    filtered_data['Weekday'] = filtered_data['DateTime'].dt.day_name()
    weekday_usage = filtered_data.groupby('Weekday')['Total'].sum().sort_values(ascending=False)
    st.markdown(f"- {bilingual_text('วันที่ใช้ไฟฟ้ามากที่สุดในสัปดาห์:', 'Weekday with the highest total electricity usage:')} {weekday_usage.idxmax()} ({format_number(weekday_usage.max())} kWh)")
    st.markdown(f"- {bilingual_text('วันที่ใช้ไฟฟ้าน้อยที่สุดในสัปดาห์:', 'Weekday with the lowest total electricity usage:')} {weekday_usage.idxmin()} ({format_number(weekday_usage.min())} kWh)")

    # Interactive Table
    st.markdown("### Filtered Data Table")
    st.dataframe(filtered_data)
# Run the App
if __name__ == "__main__":
    main()
