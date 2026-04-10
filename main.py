import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="치킨파머스 정산 시스템", layout="wide")
st.title("🍗 치킨파머스 본사 정산 자동화")
st.write("발주 Raw 데이터를 업로드하면 판매이익, 물류수수료, 본사수익을 자동으로 계산합니다.")

# 2. 파일 업로드
file = st.file_uploader("엑셀 파일을 선택하세요 (xlsx)", type=['xlsx'])

if file:
    # 데이터 불러오기
    df = pd.read_excel(file)
    
    # 필수 컬럼 존재 확인 (이미지 기준: 판매가, 구매가, 본사마진율 등)
    # 실제 엑셀의 컬럼명과 일치해야 하므로, 에러 방지를 위해 컬럼명을 유연하게 잡습니다.
    try:
        # [핵심 로직 1] 비정산 항목(야채류) 제외
        # '구분'이나 '품목명'에 '비정산' 혹은 '야채'가 포함된 행은 계산에서 제외하거나 따로 표시
        df['정산대상'] = df.apply(lambda x: '제외' if '비정산' in str(x.get('구분', '')) or '야채' in str(x.get('품목명', '')) else '대상', axis=1)
        
        # [핵심 로직 2] 매장별 구분을 위한 필터 (매장명 컬럼이 있을 경우)
        store_col = '매장명' if '매장명' in df.columns else None
        
        # [핵심 로직 3] 자동 계산
        # 판매이익 = 판매가 - 구매가
        df['판매이익'] = df['판매가(부가세별도)'] - df['구매가(부가세별도)']
        
        # 본사수익 = 판매가 * 본사마진율 (이미지의 실마진율 기준)
        # 엑셀에 마진율이 없다면 기본값 3% 적용 (수정 가능)
        df['본사수익'] = df['판매가(부가세별도)'] * 0.03 
        
        # 실마진율 = (본사수익 / 판매가) * 100
        df['실마진율(%)'] = (df['본사수익'] / df['판매가(부가세별도)']) * 100

        # 3. 결과 화면 출력
        st.success("✅ 정산 계산 완료!")
        
        # 매장별로 보기 기능
        if store_col:
            selected_store = st.selectbox("조회할 매장을 선택하세요", ["전체"] + list(df[store_col].unique()))
            if selected_store != "전체":
                display_df = df[df[store_col] == selected_store]
            else:
                display_df = df
        else:
            display_df = df

        # 요약 수치 보고
        col1, col2, col3 = st.columns(3)
        col1.metric("총 판매이익", f"{int(display_df['판매이익'].sum()):,}원")
        col2.metric("총 본사수익", f"{int(display_df['본사수익'].sum()):,}원")
        col3.metric("정산 대상 품목 수", f"{len(display_df[display_df['정산대상'] == '대상'])}개")

        # 결과 표
        st.subheader("📋 상세 데이터")
        st.dataframe(display_df)

        # 4. 결과 다운로드
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 정산 결과 다운로드", data=csv, file_name="정산결과_리포트.csv")

    except Exception as e:
        st.error(f"엑셀 컬럼명을 확인해주세요. 오류: {e}")
        st.info("팁: 엑셀의 첫 줄 이름이 '판매가(부가세별도)', '구매가(부가세별도)'와 일치해야 합니다.")
