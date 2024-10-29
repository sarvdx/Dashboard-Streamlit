import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style="dark")

day_df = pd.read_csv("dashboard/day.csv")
day_df.head()

drop_col = ["windspeed"]

for i in day_df.columns:
    if i in drop_col:
        day_df.drop(labels=i, axis=1, inplace=True)

day_df.rename(
    columns={
        "dteday": "dateday",
        "yr": "year",
        "mnth": "month",
        "weathersit": "weather_cond",
        "cnt": "count",
    },
    inplace=True,
)

day_df["month"] = day_df["month"].map(
    {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }
)
day_df["season"] = day_df["season"].map(
    {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
)
day_df["weekday"] = day_df["weekday"].map(
    {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}
)
day_df["weather_cond"] = day_df["weather_cond"].map(
    {
        1: "Clear/Partly Cloudy",
        2: "Misty/Cloudy",
        3: "Light Snow/Rain",
        4: "Severe Weather",
    }
)

min_date = pd.to_datetime(day_df["dateday"]).dt.date.min()
max_date = pd.to_datetime(day_df["dateday"]).dt.date.max()

start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)

main_df = day_df[
    (day_df["dateday"] >= str(start_date)) & (day_df["dateday"] <= str(end_date))
]

daily_rent_df = main_df.groupby(by="dateday").agg({"count": "sum"}).reset_index()
daily_casual_rent_df = main_df.groupby(by="dateday").agg({"casual": "sum"}).reset_index()
daily_registered_rent_df = main_df.groupby(by="dateday").agg({"registered": "sum"}).reset_index()
season_rent_df = main_df.groupby(by="season")[["registered", "casual"]].sum().reset_index()
monthly_rent_df = main_df.groupby(by="month").agg({"count": "sum"})
ordered_months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]
monthly_rent_df = monthly_rent_df.reindex(ordered_months, fill_value=0)

st.header("Bike Rental Dashboard by Azwa 🚲")

st.subheader("Daily Rentals")
col1, col2, col3 = st.columns(3)

with col1:
    daily_rent_casual = daily_casual_rent_df["casual"].sum()
    st.metric("Casual User", value=daily_rent_casual)

with col2:
    daily_rent_registered = daily_registered_rent_df["registered"].sum()
    st.metric("Registered User", value=daily_rent_registered)

with col3:
    daily_rent_total = daily_rent_df["count"].sum()
    st.metric("Total User", value=daily_rent_total)

st.subheader("Monthly Rentals")
fig, ax = plt.subplots(figsize=(24, 8))
ax.plot(monthly_rent_df.index, monthly_rent_df["count"], marker="o", linewidth=2, color="tab:blue")

for index, row in enumerate(monthly_rent_df["count"]):
    ax.text(index, row + 1, str(row), ha="center", va="bottom", fontsize=12)

ax.tick_params(axis="x", labelsize=25, rotation=45)
ax.tick_params(axis="y", labelsize=20)
st.pyplot(fig)

st.subheader("Seasonly Rentals")
fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(x="season", y="registered", data=season_rent_df, label="Registered", color="tab:blue", ax=ax)
sns.barplot(x="season", y="casual", data=season_rent_df, label="Casual", color="tab:orange", ax=ax)

for index, row in season_rent_df.iterrows():
    ax.text(index, row["registered"], str(row["registered"]), ha="center", va="bottom", fontsize=12)
    ax.text(index, row["casual"], str(row["casual"]), ha="center", va="bottom", fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis="x", labelsize=20)
ax.tick_params(axis="y", labelsize=15)
ax.legend()
st.pyplot(fig)

st.subheader("Weatherly Rentals")
fig, ax = plt.subplots(figsize=(16, 8))
weather_rent_df = main_df.groupby(by="weather_cond").agg({"count": "sum"})

sns.barplot(x=weather_rent_df.index, y=weather_rent_df["count"], ax=ax)

for index, row in enumerate(weather_rent_df["count"]):
    ax.text(index, row + 1, str(row), ha="center", va="bottom", fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis="x", labelsize=20)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

st.subheader("Weekday, Workingday, and Holiday Rentals")
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15, 10))

workingday_rent_df = main_df.groupby(by="workingday").agg({"count": "sum"}).reset_index()
sns.barplot(x="workingday", y="count", data=workingday_rent_df, ax=axes[0])
    
for index, row in enumerate(workingday_rent_df["count"]):
    axes[0].text(index, row + 1, str(row), ha="center", va="bottom", fontsize=12)

axes[0].set_title("Number of Rents based on Working Day")
axes[0].tick_params(axis="x", labelsize=15)

holiday_rent_df = main_df.groupby(by="holiday").agg({"count": "sum"}).reset_index()
sns.barplot(x="holiday", y="count", data=holiday_rent_df, ax=axes[1])

for index, row in enumerate(holiday_rent_df["count"]):
    axes[1].text(index, row + 1, str(row), ha="center", va="bottom", fontsize=12)

axes[1].set_title("Number of Rents based on Holiday")
axes[1].tick_params(axis="x", labelsize=15)

weekday_rent_df = main_df.groupby(by="weekday").agg({"count": "sum"}).reset_index()
sns.barplot(x="weekday", y="count", data=weekday_rent_df, ax=axes[2])

for index, row in enumerate(weekday_rent_df["count"]):
    axes[2].text(index, row + 1, str(row), ha="center", va="bottom", fontsize=12)

axes[2].set_title("Number of Rents based on Weekday")
axes[2].tick_params(axis="x", labelsize=15)

plt.tight_layout()
st.pyplot(fig)

