import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# アプリのタイトル
st.title('データ分析ダッシュボード')

# CSVファイルの読み込み
@st.cache
def load_data():
    # カレントディレクトリから相対パスでファイルを指定
    df = pd.read_csv('sales_test_data_100.csv')
    return df

df = load_data()

# サイドバーにピボットテーブルの設定を配置
st.sidebar.header('ピボットテーブル設定')

# 利用可能な列の一覧を取得
columns = df.columns.tolist()

# ピボットテーブルの設定
index_col = st.sidebar.multiselect(
    '行に表示する項目を選択:',
    options=columns,
    default=None
)

columns_col = st.sidebar.multiselect(
    '列に表示する項目を選択:',
    options=columns,
    default=None
)

values_col = st.sidebar.multiselect(
    '集計する項目を選択:',
    options=columns,
    default=None
)

# 集計方法の選択
agg_func = st.sidebar.selectbox(
    '集計方法を選択:',
    options=['count', 'sum', 'mean', 'min', 'max']
)

# グラフタイプの選択
chart_type = st.sidebar.selectbox(
    'グラフタイプを選択:',
    options=['棒グラフ', '折れ線グラフ', '散布図', 'ヒートマップ']
)

try:
    if values_col:  # 値の項目だけが必須
        # ピボットテーブルの作成
        if index_col or columns_col:  # 行または列が選択されている場合
            pivot_table = pd.pivot_table(
                df,
                index=index_col if index_col else None,
                columns=columns_col if columns_col else None,
                values=values_col,
                aggfunc=agg_func
            )
        else:  # 行も列も選択されていない場合
            # 単純な集計を実行
            if agg_func == 'count':
                pivot_table = pd.DataFrame({col: df[col].count() for col in values_col})
            elif agg_func == 'sum':
                pivot_table = pd.DataFrame({col: df[col].sum() for col in values_col})
            elif agg_func == 'mean':
                pivot_table = pd.DataFrame({col: df[col].mean() for col in values_col})
            elif agg_func == 'min':
                pivot_table = pd.DataFrame({col: df[col].min() for col in values_col})
            elif agg_func == 'max':
                pivot_table = pd.DataFrame({col: df[col].max() for col in values_col})
            
            # インデックスを追加
            pivot_table.index = ['集計結果']

        # ピボットテーブルの表示
        st.subheader('ピボットテーブル')
        st.dataframe(pivot_table)

        # グラフの作成
        st.subheader('グラフ表示')
        
        # 行も列も選択されていない場合のグラフ
        if not index_col and not columns_col:
            if chart_type == '棒グラフ':
                # 転置して棒グラフを作成
                fig = px.bar(pivot_table.T, title='集計結果')
            elif chart_type == '折れ線グラフ':
                fig = px.line(pivot_table.T, title='集計結果')
            elif chart_type == '散布図':
                fig = px.scatter(pivot_table.T, title='集計結果')
            else:  # ヒートマップ
                fig = px.imshow(pivot_table, title='集計結果')
        
        # 通常のピボットテーブルの場合
        else:
            # MultiIndexを処理するためにピボットテーブルをリセット
            plot_df = pivot_table.reset_index()
            
            if chart_type == '棒グラフ':
                if columns_col:
                    # MultiIndexがある場合はグラフオブジェクトを使用
                    fig = go.Figure()
                    for col in pivot_table.columns:
                        fig.add_trace(go.Bar(
                            x=pivot_table.index,
                            y=pivot_table[col],
                            name=str(col)
                        ))
                else:
                    # MultiIndexがない場合はそのまま表示
                    x_field = index_col[0] if index_col else pivot_table.index.name
                    fig = px.bar(plot_df, x=x_field, y=plot_df.columns[len(index_col):])
                    
            elif chart_type == '折れ線グラフ':
                if columns_col:
                    fig = go.Figure()
                    for col in pivot_table.columns:
                        fig.add_trace(go.Scatter(
                            x=pivot_table.index,
                            y=pivot_table[col],
                            mode='lines+markers',
                            name=str(col)
                        ))
                else:
                    x_field = index_col[0] if index_col else pivot_table.index.name
                    fig = px.line(plot_df, x=x_field, y=plot_df.columns[len(index_col):])
                    
            elif chart_type == '散布図':
                if columns_col:
                    fig = go.Figure()
                    for col in pivot_table.columns:
                        fig.add_trace(go.Scatter(
                            x=pivot_table.index,
                            y=pivot_table[col],
                            mode='markers',
                            name=str(col)
                        ))
                else:
                    x_field = index_col[0] if index_col else pivot_table.index.name
                    fig = px.scatter(plot_df, x=x_field, y=plot_df.columns[len(index_col):])
                    
            else:  # ヒートマップ
                fig = px.imshow(
                    pivot_table.values, 
                    x=pivot_table.columns.tolist() if isinstance(pivot_table.columns, pd.MultiIndex) else pivot_table.columns,
                    y=pivot_table.index
                )

        # グラフの表示
        st.plotly_chart(fig)

        # データの詳細情報
        st.sidebar.markdown('### データ情報')
        st.sidebar.write(f'総レコード数: {len(df)}')
        st.sidebar.write(f'集計結果の行数: {len(pivot_table)}')

    else:
        st.info('集計する項目を選択してください')

except Exception as e:
    st.error(f'エラーが発生しました: {str(e)}')
    st.write('ピボットテーブルの設定を確認してください。')
    st.write(f'エラーの詳細: {e}')

# データの基本情報の表示
st.markdown('---')
st.subheader('元データのプレビュー')
st.write(df.head())
