import streamlit as st
import pandas as pd
import networkx as nx
from union_find import DisjointSetUnion
import io
from pyvis.network import Network
import streamlit.components.v1 as components
import plotly.express as px
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["social_media_virality"]
collection = db["interactions"]

st.set_page_config(page_title="Social Media Virality Analyzer", layout="wide")

st.title("🌐 Social Media Virality Analyzer")
st.markdown("""
<style>
    .main-title {
        font-size:40px !important;
        color:#00C9A7;
        text-align:center;
        font-weight:bold;
    }
    .sub-title {
        text-align:center;
        font-size:20px;
        color:#999999;
        margin-bottom:20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🚀 Analyzing Social Media Virality</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Using Disjoint Set Union (Union-Find) & Graph Clustering</p>", unsafe_allow_html=True)
st.divider()

st.markdown("### Analyzing Viral Clusters with Union-Find & Graph Clustering")

st.sidebar.header("📤 Upload Data")
st.sidebar.markdown("Upload a CSV file with user interactions")

uploaded_file = st.sidebar.file_uploader(
    "Choose interactions CSV file", 
    type=['csv'],
    help="CSV with at least 2 columns representing user interactions"
)

use_sample = st.sidebar.checkbox("Use sample data", value=True)
# --- Step 4: Load data from MongoDB ---
load_mongo = st.sidebar.checkbox("📂 Load data from MongoDB")

if load_mongo:
    df = pd.DataFrame(list(collection.find({}, {"_id": 0})))
    if not df.empty:
        st.sidebar.success(f"✅ Loaded {len(df)} records from MongoDB")
    else:
        st.sidebar.warning("⚠️ No data found in MongoDB collection.")


if use_sample and uploaded_file is None:
    df = pd.read_csv('interactions.csv')
    st.sidebar.success("✅ Using sample interactions.csv")
elif uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success(f"✅ Loaded {uploaded_file.name}")
    records = df.to_dict(orient="records")
    if records:
        collection.insert_many(records)
        st.sidebar.info(f"📦 {len(records)} records saved to MongoDB")
else:
    st.info("👈 Please upload a CSV file or check 'Use sample data' to begin analysis")
    st.markdown("""
    ### CSV Format:
    Upload any CSV file with at least 2 columns. The first two columns will be used as user interactions.
    
    **Example:**
    ```
    Alice,Bob
    Bob,Charlie
    Charlie,David
    ```
    Or with headers:
    ```
    user_a,user_b
    Alice,Bob
    Bob,Charlie
    ```
    """)
    st.stop()

if df is not None:
    if len(df.columns) < 2:
        st.error("❌ CSV must have at least 2 columns")
        st.stop()
    
    col1_name = df.columns[0]
    col2_name = df.columns[1]
    
    df = df[[col1_name, col2_name]].dropna()
    df[col1_name] = df[col1_name].astype(str).str.strip()
    df[col2_name] = df[col2_name].astype(str).str.strip()
    
    df = df[df[col1_name] != df[col2_name]]
    
    if len(df) == 0:
        st.error("❌ No valid interactions found in the CSV file")
        st.stop()
    
    df.columns = ['user_a', 'user_b']
    st.subheader("📊 Interaction Data")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.metric("Total Interactions", len(df))
    
    st.divider()
    
    G = nx.Graph()
    for _, row in df.iterrows():
        user_a = row['user_a']
        user_b = row['user_b']
        G.add_edge(user_a, user_b)
    
    all_users = list(G.nodes())
    dsu = DisjointSetUnion(all_users)
    for _, row in df.iterrows():
        dsu.union(row['user_a'], row['user_b'])
    dsu_clusters = dsu.get_clusters()
    
    nx_clusters = list(nx.connected_components(G))
    largest = len(max(dsu_clusters, key=len))
    avg = sum(len(c) for c in dsu_clusters) / len(dsu_clusters)
    st.markdown(f"""
    ### 🧩 Cluster Insights
    - Total number of viral clusters: **{len(dsu_clusters)}**
    - Size of largest cluster: **{largest}**
    - Average cluster size: **{avg:.1f}**
    - Indicates strong community formation and engagement patterns.
    """)
    st.subheader("🔍 Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Users", len(all_users))
    
    with col2:
        st.metric("🔗 Number of Clusters", len(dsu_clusters))
    
    largest_cluster = max(dsu_clusters, key=len)
    
    with col3:
        st.metric("📈 Largest Cluster Size", len(largest_cluster))
    
    with col4:
        avg_cluster_size = sum(len(c) for c in dsu_clusters) / len(dsu_clusters)
        st.metric("📊 Avg Cluster Size", f"{avg_cluster_size:.1f}")
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🌟 Viral Clusters")
        
        sorted_clusters = sorted(dsu_clusters, key=len, reverse=True)
        
        for idx, cluster in enumerate(sorted_clusters, 1):
            with st.expander(f"Cluster {idx} - {len(cluster)} users" + (" 🏆 (Most Viral)" if cluster == largest_cluster else "")):
                st.write(", ".join(sorted(cluster)))
    
    with col2:
        st.subheader("📋 Cluster Statistics")
        
        cluster_df = pd.DataFrame({
            'Cluster ID': range(1, len(dsu_clusters) + 1),
            'Size': [len(c) for c in sorted_clusters],
            'Users': [", ".join(sorted(c)[:3]) + ("..." if len(c) > 3 else "") for c in sorted_clusters]
        })
        
        st.dataframe(cluster_df, use_container_width=True)
        
    st.subheader("🌐 Cluster Network Visualization")
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    largest_cluster_nodes = set(largest_cluster)
    for node in net.nodes:
      if node['id'] in largest_cluster_nodes:
        node['color'] = 'orange'
      else:
        node['color'] = 'skyblue'
    net.save_graph("network.html")
    HtmlFile = open("network.html", 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height=600)
    st.divider()

# --- Cluster Size Bar Chart ---
    st.subheader("📈 Cluster Size Distribution")
    chart_df = pd.DataFrame({
    'Cluster ID': range(1, len(sorted_clusters) + 1),
    'Cluster Size': [len(c) for c in sorted_clusters]
    })
    fig = px.bar(
      chart_df,
      x='Cluster ID',
      y='Cluster Size',
      color='Cluster Size',
      title='Cluster Size Comparison',
      text='Cluster Size'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()
    
    st.subheader("💾 Export Results")
    bubble_df = pd.DataFrame({
      'Cluster ID': [f"C{i}" for i in range(1, len(sorted_clusters) + 1)],
      'Cluster Size': [len(c) for c in sorted_clusters]
    })
    fig_bubble = px.scatter(
      bubble_df,
      x='Cluster ID',
      y='Cluster Size',
      size='Cluster Size',
      color='Cluster Size',
      hover_name='Cluster ID',
      size_max=50,
      title='Cluster Influence Bubble Chart'
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
    cluster_map = {}
    for idx, cluster in enumerate(dsu_clusters):
        for user in cluster:
            cluster_map[user] = idx
    
    export_df = pd.DataFrame([
        {'User': user, 'Cluster_ID': cluster_map[user] + 1, 'Cluster_Size': len(dsu_clusters[cluster_map[user]])}
        for user in all_users
    ]).sort_values(['Cluster_ID', 'User'])
    
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)
    
    st.download_button(
        label="📥 Download Cluster Analysis (CSV)",
        data=csv_buffer.getvalue(),
        file_name="viral_clusters.csv",
        mime="text/csv"
    )
    
    st.dataframe(export_df, use_container_width=True)
# --- Step 5: Save cluster analysis results to MongoDB ---
result_collection = db["cluster_results"]
result_collection.delete_many({})  # clear previous results
result_collection.insert_many(export_df.to_dict(orient="records"))
st.sidebar.success("📊 Cluster results saved to MongoDB")

st.sidebar.divider()
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:gray;'>
    <b>Developed by Tanu Chaudhary</b><br>
    © 2025 | Social Media Virality Analyzer
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("### 📖 About")
st.sidebar.markdown("""
This tool uses:
- **Union-Find (DSU)** algorithm for efficient cluster detection
- **NetworkX** for graph analysis

Upload your interaction data to discover viral communities!
""")
