import streamlit as st
import pandas as pd

# 1. 웹 화면 설정
st.set_page_config(page_title="치킨파머스 정산 시스템", layout="wide")
st.title("🍗 치킨파머스 본사 정산 자동화 시스템")
st.markdown("---")

# 2. 파일 업로드 가이드
st.sidebar.header("사용 가이드")
st.sidebar.info("1. 매장별 발주 raw 데이터를 준비하세요.\n2. 아래 업로드 칸에 파일을 드래그하세요.\n3. 계산된 수익을 확인하고 다운로드하세요.")

# 3. 파일 업로더
uploaded_file = st.file_uploader("엑셀 파일(xlsx)을 업로드해주세요", type=['xlsx'])

if uploaded_file:
    try:
        # 데이터 읽기
        df = pd.read_excel(uploaded_file)
        
        # 4. 정산 로직 (이지은 언니가 필요로 하는 핵심 필터링)
        # 엑셀의 컬럼명에 따라 아래 이름을 수정해야 할 수도 있습니다.
        if '판매가' in df.columns and '구매가' in df.columns:
            # 판매이익 = 판매가 - 구매가
            df['판매이익'] = df['판매가'] - df['구매가']
            
            # 본사수익(수수료) = 판매가의 3% (예시 수치, 필요시 수정 가능)
            df['본사수익'] = df['판매가'] * 0.03
            
            # 물류수수료 (예시)
            df['물류수수료'] = df['판매가'] * 0.02
            
            st.success("✅ 정산 계산이 완료되었습니다!")
            
            # 결과 보여주기
            st.subheader("📊 항목별 정산 데이터")
            st.dataframe(df, use_container_width=True)
            
            # 5. 결과 다운로드
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 정산 결과 엑셀로 내보내기",
                data=csv,
                file_name="치킨파머스_정산결과.csv",
                mime="text/csv",
            )
        else:
            st.warning("⚠️ 엑셀 파일에 '판매가'와 '구매가' 컬럼이 있는지 확인해주세요.")
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

else:
    st.write("⬆️ 위 버튼을 눌러 발주 데이터를 업로드하면 분석이 시작됩니다.")
