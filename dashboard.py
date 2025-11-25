import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Zoo Dashboard", page_icon="🐾", layout="wide")

st.title("🐾 Zoo Animal Life Expectancy Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("AZA_MLE_Jul2018 (1).csv", encoding="ISO-8859-1", on_bad_lines="skip")
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("-", "_")
    df = df.dropna(subset=["Overall_MLE"])
    return df

df = load_data()

st.sidebar.header("Filter Options")
taxon_classes = df["TaxonClass"].dropna().unique()
selected_class = st.sidebar.selectbox("Select Taxon Class:", ["All"] + list(taxon_classes))

filtered_df = df.copy()
if selected_class != "All":
    filtered_df = filtered_df[filtered_df["TaxonClass"] == selected_class]

search_species = st.sidebar.text_input("🔍 Search for a Species (Common Name):")
if search_species:
    filtered_df = filtered_df[filtered_df["Species_Common_Name"].str.contains(search_species, case=False, na=False)]

st.subheader("📊 Summary Statistics")
col1, col2 = st.columns(2)
col1.metric("Total Species", len(filtered_df["Species_Common_Name"].unique()))
col2.metric("Average Overall MLE", f"{filtered_df['Overall_MLE'].mean():.2f}")

tab1, tab2, tab3 = st.tabs(["📈 Overall Distribution", "🏆 Top Species", "⚥ Male vs Female Comparison"])

with tab1:
    st.subheader("Distribution of Median Life Expectancy")
    fig1 = px.histogram(filtered_df, x="Overall_MLE", nbins=30,
                        title="Overall MLE Distribution",
                        color="TaxonClass")
    st.plotly_chart(fig1, use_container_width=True)


with tab2:
    st.subheader("Top 10 Species by Overall Median Life Expectancy")
    top_species = filtered_df.sort_values(by="Overall_MLE", ascending=False).head(10)
    fig2 = px.bar(top_species, x="Species_Common_Name", y="Overall_MLE",
                  color="TaxonClass", text_auto=True,
                  title="Top 10 Species by Life Expectancy")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Male vs Female Median Life Expectancy")
    comparison_df = filtered_df.dropna(subset=["Male_MLE", "Female_MLE"])
    if not comparison_df.empty:
        fig3 = px.bar(comparison_df.head(20),
                      x="Species_Common_Name",
                      y=["Male_MLE", "Female_MLE"],
                      barmode="group",
                      title="Top 20 Species (Male vs Female MLE)")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No male/female data available for this filter.")

st.subheader("📋 Filtered Data Table")
st.dataframe(filtered_df)

if st.button("💾 Save Filtered Data as CSV"):
    filtered_df.to_csv("filtered_aza_mle.csv", index=False)
    st.success("Filtered data saved as 'filtered_aza_mle.csv' ✅")
