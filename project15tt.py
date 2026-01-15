import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="Student Performance Analyzer", layout="wide", page_icon="📈")
st.title("Student Performance Progression & Risk Analyzer")
st.markdown("*Advanced Academic Analytics Dashboard*")

# Sidebar
st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader(r"C:\Users\Anjli\Downloads\study_performance.csv", type="csv")

# Load sample data
@st.cache_data
def load_sample_data():
    np.random.seed(42)
    n_students = 50
    data = []
    
    for i in range(n_students):
        student_id = f"S{i+1:03d}"
        for sem in ['S1', 'S2', 'S3']:
            base_scores = np.random.normal(70, 15, 3)
            scores = np.clip(base_scores + (['S1','S2','S3'].index(sem)*3), 0, 100)
            data.append({
                'student_id': student_id,
                'semester': sem,
                'math': round(scores[0], 1),
                'english': round(scores[1], 1), 
                'science': round(scores[2], 1),
                'attendance': round(np.clip(85 + np.random.normal(0, 8), 70, 98), 1)
            })
    return pd.DataFrame(data)

# Analysis function
@st.cache_data
def analyze_data(df):
    score_cols = [col for col in df.columns if any(x in col.lower() for x in ['math','english','science','score'])]
    
    df['avg_score'] = df[score_cols].mean(axis=1)
    df['consistency'] = 1 / (1 + df[score_cols].std(axis=1))
    
    # Safe grade assignment
    def get_grade(score):
        if score >= 90: return 'A+'
        elif score >= 80: return 'A' 
        elif score >= 70: return 'B'
        elif score >= 60: return 'C'
        return 'F'
    
    df['grade'] = df['avg_score'].apply(get_grade)
    df['risk'] = np.where(df['avg_score'] < 60, 'HIGH 🚨',
                         np.where(df['avg_score'] < 70, 'MEDIUM ⚠️', 'LOW ✅'))
    
    return df, score_cols

# Load data
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Real data loaded!")
else:
    df = load_sample_data()
    st.info("📊 Using sample data")

df, score_cols = analyze_data(df)

# === DASHBOARD ===
col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Students", df['student_id'].nunique())
col2.metric("📊 Avg Score", f"{df['avg_score'].mean():.1f}")
col3.metric("🚨 High Risk", (df['risk']=='HIGH 🚨').sum())
col4.metric("📈 Avg Attendance", f"{df['attendance'].mean():.1f}%")

st.markdown("---")

# Row 1: Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚨 Risk Distribution")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    df['risk'].value_counts().plot(kind='pie', ax=ax1, autopct='%1.1f%%', 
                                   colors=['#d32f2f', '#f57c00', '#388e3c'])
    ax1.set_ylabel('')
    st.pyplot(fig1)
    plt.close(fig1)

with col2:
    st.subheader("🎯 Grade Distribution") 
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    df['grade'].value_counts().plot(kind='bar', ax=ax2, color='skyblue')
    ax2.set_ylabel('Count')
    plt.xticks(rotation=0)
    st.pyplot(fig2)
    plt.close(fig2)

# Row 2: Subject performance + Risk table
col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 Subject Performance")
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    df.boxplot(column=score_cols, ax=ax3)
    plt.xticks(rotation=45)
    st.pyplot(fig3)
    plt.close(fig3)

with col2:
    st.subheader("⚠️ High Risk Students")
    risk_df = df[df['risk'] == 'HIGH 🚨'][['student_id', 'avg_score', 'grade']].head(10)
    st.dataframe(risk_df, width="stretch")

# Row 3: Top/Bottom performers
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Performers")
    top_students = df.groupby('student_id')['avg_score'].mean().nlargest(5)
    top_df = df[df['student_id'].isin(top_students.index)].groupby('student_id')['avg_score'].mean().reset_index()
    st.dataframe(top_df, width="stretch")

with col2:
    st.subheader("🚨 Bottom Performers") 
    bottom_students = df.groupby('student_id')['avg_score'].mean().nsmallest(5)
    bottom_df = df[df['student_id'].isin(bottom_students.index)].groupby('student_id')['avg_score'].mean().reset_index()
    st.dataframe(bottom_df, width="stretch")

# Download
st.markdown("---")
csv_data = df[['student_id', 'semester', 'avg_score', 'grade', 'risk', 'attendance'] + score_cols].round(2)
st.download_button("📄 Download Full Analysis", csv_data.to_csv(index=False), "student_analysis.csv")

# Footer
st.markdown("---")
st.markdown("*Professional Student Performance Analytics Dashboard*")

