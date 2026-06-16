"""
人口数据分析看板 - app.py
运行命令：streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="中国人口数据分析看板",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("📊 中国人口数据分析看板")
st.markdown("---")

# 加载数据
@st.cache_data
def load_data():
    # 读取 date 文件夹中的数据文件
    df = pd.read_csv('人口数据.csv', encoding='utf-8')
    
    # 确保数值列类型正确
    numeric_cols = ['户数合计', '家庭户户数', '集体户户数', '人口合计', 
                    '男', '女', '性别比', '家庭户人口合计', '家庭户男', 
                    '家庭户女', '家庭户性别比', '集体户人口合计', 
                    '集体户男', '集体户女', '集体户性别比']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 计算衍生指标
    df['家庭户均人口'] = df['家庭户人口合计'] / df['家庭户户数']
    df['集体户人口占比'] = (df['集体户人口合计'] / df['人口合计']) * 100
    return df

try:
    df = load_data()
    st.success(f"✅ 数据加载成功！共 {len(df)} 个省份/地区")
except Exception as e:
    st.error(f"❌ 数据加载失败：{e}")
    st.info("请确保 date/人口数据.csv 文件存在")
    st.stop()

# 侧边栏筛选
st.sidebar.header("🔍 数据筛选")
selected_provinces = st.sidebar.multiselect(
    "选择省份",
    options=df['地区'].tolist(),
    default=df['地区'].tolist()  # 默认全选
)

# 数据筛选
if selected_provinces:
    df_filtered = df[df['地区'].isin(selected_provinces)]
else:
    df_filtered = df

# ========== 主要指标卡片 ==========
st.subheader("📈 全国人口概况")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_pop = df['人口合计'].sum()
    st.metric("总人口", f"{total_pop/100000000:.2f} 亿")

with col2:
    total_household = df['户数合计'].sum()
    st.metric("总户数", f"{total_household/10000:.0f} 万户")

with col3:
    total_male = df['男'].sum()
    total_female = df['女'].sum()
    gender_ratio = total_male / total_female * 100
    st.metric("总体性别比", f"{gender_ratio:.2f}", "100=平衡")

with col4:
    avg_family_size = (df['家庭户人口合计'].sum() / df['家庭户户数'].sum())
    st.metric("平均家庭规模", f"{avg_family_size:.2f} 人/户")

st.markdown("---")

# ========== 图表1：人口Top10 ==========
st.subheader("🏆 人口最多的10个省份")

col1, col2 = st.columns(2)

with col1:
    top10_pop = df.nlargest(10, '人口合计')[['地区', '人口合计']]
    fig = px.bar(top10_pop, x='地区', y='人口合计', 
                 title='各省人口数量排名',
                 labels={'人口合计': '人口数量（人）', '地区': '省份'},
                 color='人口合计',
                 color_continuous_scale='Viridis')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # 饼图
    fig = px.pie(top10_pop, values='人口合计', names='地区',
                 title='人口Top10省份占比',
                 hole=0.3)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ========== 图表2：性别比分析 ==========
st.subheader("⚖️ 性别比分析")

col1, col2 = st.columns(2)

with col1:
    # 家庭户性别比
    df_sorted_family = df.sort_values('家庭户性别比', ascending=True)
    fig = px.bar(df_sorted_family, x='地区', y='家庭户性别比',
                 title='家庭户性别比（<100表示女多男少）',
                 labels={'家庭户性别比': '性别比', '地区': '省份'},
                 color='家庭户性别比',
                 color_continuous_scale='RdBu',
                 range_color=[95, 105])
    fig.add_hline(y=100, line_dash="dash", line_color="red")
    fig.update_layout(height=500, xaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # 集体户性别比
    df_sorted_collective = df.sort_values('集体户性别比', ascending=False)
    fig = px.bar(df_sorted_collective.head(15), x='地区', y='集体户性别比',
                 title='集体户性别比Top15（通常远高于100）',
                 labels={'集体户性别比': '性别比', '地区': '省份'},
                 color='集体户性别比',
                 color_continuous_scale='Reds')
    fig.add_hline(y=100, line_dash="dash", line_color="green")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ========== 图表3：散点图分析 ==========
st.subheader("🔍 多维度分析：家庭户 vs 集体户 性别比关系")

fig = px.scatter(df, x='家庭户性别比', y='集体户性别比',
                 size='人口合计', color='地区',
                 hover_name='地区',
                 size_max=60,
                 title='家庭户 vs 集体户 性别比关系图',
                 labels={'家庭户性别比': '家庭户性别比', 
                        '集体户性别比': '集体户性别比'})
fig.add_hline(y=100, line_dash="dash", line_color="gray")
fig.add_vline(x=100, line_dash="dash", line_color="gray")
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

# 图表解读
with st.expander("💡 图表解读说明"):
    st.write("""
    - **横轴**：家庭户性别比（正常值一般在95-105之间）
    - **纵轴**：集体户性别比（通常远高于100，表示男性远多于女性）
    - **气泡大小**：代表该省份的总人口数
    - **红色虚线**：性别比100，代表男女平衡点
    
    **主要发现**：
    - 大多数省份家庭户性别比在正常范围内
    - 北京、上海、广东等经济发达地区集体户性别比异常高
    - 新疆集体户性别比最高（191.16），可能与建设兵团有关
    - 东北三省总体性别比偏低（<100），可能与人口流失有关
    """)

st.markdown("---")

# ========== 图表4：集体户分析 ==========
st.subheader("🏢 集体户特征分析")

col1, col2 = st.columns(2)

with col1:
    top_collective = df.nlargest(10, '集体户人口占比')[['地区', '集体户人口占比', '集体户性别比']]
    fig = px.bar(top_collective, x='地区', y='集体户人口占比',
                 title='集体户人口占比Top10',
                 labels={'集体户人口占比': '集体户人口占比 (%)', '地区': '省份'},
                 color='集体户性别比',
                 color_continuous_scale='Hot')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(df, x='集体户人口占比', y='集体户性别比',
                     text='地区', size='人口合计',
                     title='集体户占比 vs 性别比关系',
                     labels={'集体户人口占比': '集体户人口占比 (%)',
                            '集体户性别比': '集体户性别比'})
    fig.update_traces(textposition='top center')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ========== 图表5：性别比热力图 ==========
st.subheader("🌡️ 各省性别比热力图")

# 准备热力图数据
heatmap_data = df[['地区', '家庭户性别比', '集体户性别比', '性别比']].copy()
heatmap_data = heatmap_data.set_index('地区')

fig = px.imshow(heatmap_data.T,
                labels=dict(x="省份", y="指标", color="性别比"),
                title="各省性别比对比热力图",
                color_continuous_scale='RdBu',
                aspect='auto',
                height=400)
fig.update_layout(xaxis={'tickangle': 45})
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ========== 图表6：家庭户规模分析 ==========
st.subheader("📊 家庭户规模分析")

# 家庭户均人口排名
df_sorted_family_size = df.sort_values('家庭户均人口', ascending=False)
fig = px.bar(df_sorted_family_size.head(15), x='地区', y='家庭户均人口',
             title='家庭户均人口最多的15个省份',
             labels={'家庭户均人口': '家庭户均人口（人/户）', '地区': '省份'},
             color='家庭户均人口',
             color_continuous_scale='Tealgrn')
fig.add_hline(y=df['家庭户均人口'].mean(), line_dash="dash", line_color="red",
              annotation_text=f"全国平均: {df['家庭户均人口'].mean():.2f}")
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ========== 数据表格 ==========
st.subheader("📋 详细数据查询")

# 选择显示的列
display_cols = ['地区', '人口合计', '男', '女', '性别比', 
                '家庭户性别比', '集体户性别比', '家庭户均人口', '集体户人口占比']

# 格式化显示
show_df = df_filtered[display_cols].copy()
show_df['人口合计'] = show_df['人口合计'].apply(lambda x: f"{x:,.0f}")
show_df['男'] = show_df['男'].apply(lambda x: f"{x:,.0f}")
show_df['女'] = show_df['女'].apply(lambda x: f"{x:,.0f}")
show_df['家庭户均人口'] = show_df['家庭户均人口'].round(2)
show_df['集体户人口占比'] = show_df['集体户人口占比'].round(2)

st.dataframe(show_df, use_container_width=True, height=400)

st.markdown("---")

# ========== 下载功能 ==========
st.subheader("💾 数据导出")

# 准备导出数据
export_df = df_filtered.copy()
export_df['人口合计'] = export_df['人口合计'].apply(lambda x: f"{x:,.0f}")
export_df['男'] = export_df['男'].apply(lambda x: f"{x:,.0f}")
export_df['女'] = export_df['女'].apply(lambda x: f"{x:,.0f}")

csv = export_df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 下载当前筛选数据 (CSV格式)",
    data=csv,
    file_name="population_data.csv",
    mime="text/csv",
)

# ========== 关键发现总结 ==========
st.markdown("---")
st.subheader("🎯 关键发现总结")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**📍 人口分布**")
    st.write(f"- 人口最多：{df.loc[df['人口合计'].idxmax(), '地区']} ({df['人口合计'].max()/100000000:.2f}亿)")
    st.write(f"- 人口最少：{df.loc[df['人口合计'].idxmin(), '地区']} ({df['人口合计'].min()/10000:.0f}万)")

with col2:
    st.warning("**⚠️ 性别比异常**")
    # 集体户性别比最高的省份
    highest = df.loc[df['集体户性别比'].idxmax(), '地区']
    st.write(f"- 集体户性别比最高：{highest} ({df['集体户性别比'].max():.2f})")
    # 家庭户性别比最低的省份
    lowest = df.loc[df['家庭户性别比'].idxmin(), '地区']
    st.write(f"- 家庭户女多男少：{lowest} ({df['家庭户性别比'].min():.2f})")

with col3:
    st.success("**🏠 家庭规模**")
    st.write(f"- 家庭规模最大：{df.loc[df['家庭户均人口'].idxmax(), '地区']} ({df['家庭户均人口'].max():.2f}人/户)")
    st.write(f"- 家庭规模最小：{df.loc[df['家庭户均人口'].idxmin(), '地区']} ({df['家庭户均人口'].min():.2f}人/户)")

st.markdown("---")
st.caption("数据来源：中国人口普查数据 | 分析工具：Streamlit + Plotly | 最后更新：2024年")