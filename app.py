import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error
import os
from dotenv import load_dotenv
load_dotenv()

# MySQL 테마 CSS 적용
st.markdown("""
<style>
    /* MySQL 브랜드 색상 */
    :root {
        --mysql-blue: #00758F;
        --mysql-orange: #F29111;
        --mysql-light-blue: #E6F3F7;
        --mysql-dark-blue: #005571;
        --mysql-light-orange: #FFF1E0;
    }
    
    /* 전체 페이지 스타일 */
    .main {
        background-color: #F8F9FA;
    }
    
    /* 헤더 스타일 */
    h1, h2, h3 {
        color: var(--mysql-blue) !important;
        font-family: 'Arial', sans-serif;
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background-color: var(--mysql-light-blue);
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background-color: var(--mysql-blue);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: var(--mysql-dark-blue);
    }
    
    /* 코드 블록 스타일 */
    .highlight {
        background-color: var(--mysql-light-blue);
        border-left: 3px solid var(--mysql-blue);
        padding: 10px;
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        border-collapse: collapse;
        font-family: 'Courier New', monospace;
    }
    
    .dataframe th {
        background-color: var(--mysql-blue);
        color: white;
        font-weight: bold;
        text-align: left;
        padding: 8px;
    }
    
    .dataframe td {
        border: 1px solid #ddd;
        padding: 8px;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: var(--mysql-light-blue);
    }
    
    /* 문제 카드 스타일 */
    .problem-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid var(--mysql-blue);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 힌트 스타일 */
    .hint-box {
        background-color: var(--mysql-light-orange);
        border-left: 5px solid var(--mysql-orange);
        padding: 10px;
        margin: 10px 0;
    }
    
    /* MySQL 로고 스타일 */
    .mysql-logo {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .mysql-logo-text {
        font-size: 2.5rem;
        font-weight: bold;
        margin-left: 10px;
    }
    
    .mysql-blue {
        color: var(--mysql-blue);
    }
    
    .mysql-orange {
        color: var(--mysql-orange);
    }
    
    /* 쿼리 입력 영역 스타일 */
    .stTextArea>div>div>textarea {
        font-family: 'Courier New', monospace;
        background-color: #2D2D2D;
        color: #E6E6E6;
        border: 1px solid var(--mysql-blue);
    }
    
    /* 결과 영역 스타일 */
    .result-area {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# MySQL 로고 및 앱 제목
st.markdown("""
<div class="mysql-logo">
    <div class="mysql-logo-text">
        <span class="mysql-blue">MySQL</span> <span class="mysql-orange">SQL Challenge</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<p>classicmodels 데이터베이스를 사용한 SQL 문제를 풀어보세요!</p>", unsafe_allow_html=True)

# 데이터베이스 연결 정보
# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "database": os.getenv("DB_DATABASE"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD")
# }
# DB_CONFIG = {
#     "host":"centerbeam.proxy.rlwy.net",
#     "port":int(os.getenv("DB_PORT")),
#     "user":os.getenv("DB_USER"),
#     "password":os.getenv("DB_PASSWORD"),
#     "database":os.getenv("DB_NAME")
# }

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"]
}


# 데이터베이스 연결 함수
def create_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return None

# 쿼리 실행 함수
def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        # SELECT 쿼리인 경우 결과 반환
        if query.strip().upper().startswith("SELECT"):
            columns = [column[0] for column in cursor.description]
            results = cursor.fetchall()
            return pd.DataFrame(results, columns=columns)
        else:
            connection.commit()
            return f"쿼리가 성공적으로 실행되었습니다. 영향 받은 행: {cursor.rowcount}"
    except Error as e:
        return f"쿼리 실행 오류: {e}"
    finally:
        if cursor:
            cursor.close()

# 데이터베이스 스키마 정보 표시 함수
def show_schema_info():
    conn = create_connection()
    if conn:
        tables_info = """
        <div class="problem-card">
        <h3>데이터베이스 테이블 정보</h3>
        
        <p><strong>1. productlines</strong>: 제품 라인 정보</p>
        <ul>
           <li>productLine, textDescription, htmlDescription, image</li>
        </ul>
        
        <p><strong>2. products</strong>: 제품 정보</p>
        <ul>
           <li>productCode, productName, productLine, productScale, productVendor, 
             productDescription, quantityInStock, buyPrice, MSRP</li>
        </ul>
        
        <p><strong>3. offices</strong>: 사무실 정보</p>
        <ul>
           <li>officeCode, city, phone, addressLine1, addressLine2, state, country, 
             postalCode, territory</li>
        </ul>
        
        <p><strong>4. employees</strong>: 직원 정보</p>
        <ul>
           <li>employeeNumber, lastName, firstName, extension, email, officeCode, 
             reportsTo, jobTitle</li>
        </ul>
        
        <p><strong>5. customers</strong>: 고객 정보</p>
        <ul>
           <li>customerNumber, customerName, contactLastName, contactFirstName, phone, 
             addressLine1, addressLine2, city, state, postalCode, country, 
             salesRepEmployeeNumber, creditLimit</li>
        </ul>
        
        <p><strong>6. payments</strong>: 결제 정보</p>
        <ul>
           <li>customerNumber, checkNumber, paymentDate, amount</li>
        </ul>
        
        <p><strong>7. orders</strong>: 주문 정보</p>
        <ul>
           <li>orderNumber, orderDate, requiredDate, shippedDate, status, comments, 
             customerNumber</li>
        </ul>
        
        <p><strong>8. orderdetails</strong>: 주문 상세 정보</p>
        <ul>
           <li>orderNumber, productCode, quantityOrdered, priceEach, orderLineNumber</li>
        </ul>
        </div>
        """
        st.markdown(tables_info, unsafe_allow_html=True)
        conn.close()

# 문제 목록
sql_challenges = [
    {
        "id": 1,
        "title": "기본 SELECT 쿼리",
        "description": "customers 테이블에서 고객 번호, 고객 이름, 연락처 이름, 국가를 조회하세요. 결과는 국가별로 정렬하세요.",
        "hint": "SELECT, FROM, ORDER BY 구문을 사용하세요.",
        "solution": """
        SELECT 
            customerNumber, 
            customerName, 
            contactFirstName, 
            contactLastName, 
            country
        FROM 
            customers
        ORDER BY 
            country
        """
    },
    {
        "id": 2,
        "title": "필터링 쿼리",
        "description": "USA에 있는 고객 중 신용 한도(creditLimit)가 $100,000 이상인 고객의 이름과 신용 한도를 조회하세요.",
        "hint": "WHERE 절에서 AND 연산자를 사용하세요.",
        "solution": """
        SELECT 
            customerName, 
            creditLimit
        FROM 
            customers
        WHERE 
            country = 'USA' 
            AND creditLimit >= 100000
        ORDER BY 
            creditLimit DESC
        """
    },
    {
        "id": 3,
        "title": "집계 함수 사용",
        "description": "각 제품 라인별 제품 수와 평균 가격(buyPrice)을 계산하세요.",
        "hint": "GROUP BY와 집계 함수(COUNT, AVG)를 사용하세요.",
        "solution": """
        SELECT 
            productLine, 
            COUNT(*) AS productCount, 
            ROUND(AVG(buyPrice), 2) AS averagePrice
        FROM 
            products
        GROUP BY 
            productLine
        ORDER BY 
            productCount DESC
        """
    },
    {
        "id": 4,
        "title": "JOIN 쿼리",
        "description": "각 주문(orders)과 해당 주문의 총 금액을 계산하세요. 주문 번호, 주문 날짜, 고객 이름, 총 주문 금액을 포함해야 합니다.",
        "hint": "orders, orderdetails, customers 테이블을 JOIN하고 SUM 함수를 사용하세요.",
        "solution": """
        SELECT 
            o.orderNumber, 
            o.orderDate, 
            c.customerName, 
            SUM(od.quantityOrdered * od.priceEach) AS totalAmount
        FROM 
            orders o
        JOIN 
            orderdetails od ON o.orderNumber = od.orderNumber
        JOIN 
            customers c ON o.customerNumber = c.customerNumber
        GROUP BY 
            o.orderNumber, o.orderDate, c.customerName
        ORDER BY 
            totalAmount DESC
        """
    },
    {
        "id": 5,
        "title": "서브쿼리 활용",
        "description": "평균 구매 가격(buyPrice)보다 비싼 제품의 이름, 제품 라인, 구매 가격을 조회하세요.",
        "hint": "서브쿼리를 사용하여 평균 가격을 계산하고 WHERE 절에서 비교하세요.",
        "solution": """
        SELECT 
            productName, 
            productLine, 
            buyPrice
        FROM 
            products
        WHERE 
            buyPrice > (SELECT AVG(buyPrice) FROM products)
        ORDER BY 
            buyPrice
        """
    },
    {
        "id": 6,
        "title": "복합 JOIN 쿼리",
        "description": "각 영업 사원별 총 매출액을 계산하세요. 영업 사원 이름, 사무실 위치, 총 매출액을 포함해야 합니다.",
        "hint": "employees, customers, payments, offices 테이블을 JOIN하세요.",
        "solution": """
        SELECT 
            CONCAT(e.firstName, ' ', e.lastName) AS salesRepName,
            o.city AS officeCity,
            o.country AS officeCountry,
            SUM(p.amount) AS totalSales
        FROM 
            employees e
        JOIN 
            customers c ON e.employeeNumber = c.salesRepEmployeeNumber
        JOIN 
            payments p ON c.customerNumber = p.customerNumber
        JOIN 
            offices o ON e.officeCode = o.officeCode
        GROUP BY 
            e.employeeNumber, salesRepName, officeCity, officeCountry
        ORDER BY 
            totalSales DESC
        """
    },
    {
        "id": 7,
        "title": "HAVING 절 사용",
        "description": "총 주문 금액이 $50,000 이상인 고객의 이름과 총 주문 금액을 조회하세요.",
        "hint": "JOIN, GROUP BY, HAVING 절을 사용하세요.",
        "solution": """
        SELECT 
            c.customerName,
            SUM(od.quantityOrdered * od.priceEach) AS totalOrderAmount
        FROM 
            customers c
        JOIN 
            orders o ON c.customerNumber = o.customerNumber
        JOIN 
            orderdetails od ON o.orderNumber = od.orderNumber
        GROUP BY 
            c.customerNumber, c.customerName
        HAVING 
            totalOrderAmount >= 50000
        ORDER BY 
            totalOrderAmount DESC
        """
    },
    {
        "id": 8,
        "title": "날짜 함수 활용",
        "description": "2003년 각 월별 총 주문 수와 매출액을 조회하세요.",
        "hint": "YEAR(), MONTH() 함수와 GROUP BY를 사용하세요.",
        "solution": """
        SELECT 
            YEAR(o.orderDate) AS orderYear,
            MONTH(o.orderDate) AS orderMonth,
            COUNT(DISTINCT o.orderNumber) AS orderCount,
            SUM(od.quantityOrdered * od.priceEach) AS totalSales
        FROM 
            orders o
        JOIN 
            orderdetails od ON o.orderNumber = od.orderNumber
        WHERE 
            YEAR(o.orderDate) = 2003
        GROUP BY 
            orderYear, orderMonth
        ORDER BY 
            orderMonth
        """
    },
    {
        "id": 9,
        "title": "CASE 표현식 사용",
        "description": "제품의 재고 상태를 'Low Stock'(10개 미만), 'Medium Stock'(10-50개), 'High Stock'(50개 초과)으로 분류하여 각 카테고리별 제품 수를 조회하세요.",
        "hint": "CASE 표현식과 GROUP BY를 사용하세요.",
        "solution": """
        SELECT 
            CASE 
                WHEN quantityInStock < 10 THEN 'Low Stock'
                WHEN quantityInStock BETWEEN 10 AND 50 THEN 'Medium Stock'
                ELSE 'High Stock'
            END AS stockCategory,
            COUNT(*) AS productCount
        FROM 
            products
        GROUP BY 
            stockCategory
        ORDER BY 
            CASE 
                WHEN stockCategory = 'Low Stock' THEN 1
                WHEN stockCategory = 'Medium Stock' THEN 2
                ELSE 3
            END
        """
    },
    {
        "id": 10,
        "title": "고급 분석 쿼리",
        "description": "각 고객별로 가장 많이 구매한 제품 카테고리(productLine)와 해당 카테고리의 총 구매 금액을 조회하세요.",
        "hint": "서브쿼리와 JOIN을 조합하여 사용하세요.",
        "solution": """
        WITH CustomerProductLineSales AS (
            SELECT 
                c.customerNumber,
                c.customerName,
                p.productLine,
                SUM(od.quantityOrdered * od.priceEach) AS totalAmount
            FROM 
                customers c
            JOIN 
                orders o ON c.customerNumber = o.customerNumber
            JOIN 
                orderdetails od ON o.orderNumber = od.orderNumber
            JOIN 
                products p ON od.productCode = p.productCode
            GROUP BY 
                c.customerNumber, c.customerName, p.productLine
        ),
        RankedProductLines AS (
            SELECT 
                customerNumber,
                customerName,
                productLine,
                totalAmount,
                RANK() OVER (PARTITION BY customerNumber ORDER BY totalAmount DESC) AS productLineRank
            FROM 
                CustomerProductLineSales
        )
        SELECT 
            customerName,
            productLine AS favoriteProductLine,
            totalAmount
        FROM 
            RankedProductLines
        WHERE 
            productLineRank = 1
        ORDER BY 
            totalAmount DESC
        """
    }
]

# 사이드바 메뉴
st.sidebar.markdown("<h2 class='mysql-blue'>메뉴</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("선택하세요:", ["데이터베이스 정보", "SQL 문제 풀기", "자유 쿼리 실행"])

if menu == "데이터베이스 정보":
    st.markdown("<h2 class='mysql-blue'>MySQL Sample Database: classicmodels</h2>", unsafe_allow_html=True)
    st.write("이 앱은 MySQL의 classicmodels 샘플 데이터베이스를 사용합니다.")
    st.write("데이터베이스는 모델 자동차 판매 회사의 비즈니스 데이터를 담고 있습니다.")
    
    show_schema_info()
    
    # ER 다이어그램 URL
    er_diagram_url = "https://www.mysqltutorial.org/wp-content/uploads/2023/10/mysql-sample-database.png"
    st.markdown("<h3 class='mysql-blue'>데이터베이스 ER 다이어그램</h3>", unsafe_allow_html=True)
    st.image(er_diagram_url, caption="classicmodels 데이터베이스 ER 다이어그램", use_container_width=True)

elif menu == "SQL 문제 풀기":
    st.markdown("<h2 class='mysql-blue'>SQL 문제 풀기</h2>", unsafe_allow_html=True)
    
    # 문제 선택
    challenge_id = st.selectbox(
        "문제를 선택하세요:",
        options=[c["id"] for c in sql_challenges],
        format_func=lambda x: f"문제 {x}: {next((c['title'] for c in sql_challenges if c['id'] == x), '')}"
    )
    
    # 선택한 문제 표시
    selected_challenge = next((c for c in sql_challenges if c["id"] == challenge_id), None)
    if selected_challenge:
        st.markdown(f"""
        <div class="problem-card">
            <h3>문제 {selected_challenge['id']}: {selected_challenge['title']}</h3>
            <p>{selected_challenge['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("힌트 보기"):
            st.markdown(f"""
            <div class="hint-box">
                {selected_challenge['hint']}
            </div>
            """, unsafe_allow_html=True)
        
        # 사용자 쿼리 입력
        st.markdown("<h3 class='mysql-blue'>쿼리 작성</h3>", unsafe_allow_html=True)
        user_query = st.text_area("SQL 쿼리를 작성하세요:", height=150)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("쿼리 실행"):
                if user_query:
                    conn = create_connection()
                    if conn:
                        result = execute_query(conn, user_query)
                        st.markdown("<h3 class='mysql-blue'>실행 결과:</h3>", unsafe_allow_html=True)
                        st.markdown('<div class="result-area">', unsafe_allow_html=True)
                        st.write(result)
                        st.markdown('</div>', unsafe_allow_html=True)
                        conn.close()
                else:
                    st.warning("쿼리를 입력해주세요.")
        
        with col2:
            if st.button("정답 확인"):
                st.markdown("<h3 class='mysql-blue'>정답 쿼리:</h3>", unsafe_allow_html=True)
                st.code(selected_challenge["solution"], language="sql")
                
                # 정답 쿼리 실행 결과 표시
                conn = create_connection()
                if conn:
                    st.markdown("<h3 class='mysql-blue'>정답 쿼리 실행 결과:</h3>", unsafe_allow_html=True)
                    st.markdown('<div class="result-area">', unsafe_allow_html=True)
                    result = execute_query(conn, selected_challenge["solution"])
                    st.write(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    conn.close()

elif menu == "자유 쿼리 실행":
    st.markdown("<h2 class='mysql-blue'>자유 쿼리 실행</h2>", unsafe_allow_html=True)
    st.write("원하는 SQL 쿼리를 자유롭게 실행해보세요.")
    
    # 사용자 쿼리 입력
    user_query = st.text_area("SQL 쿼리를 작성하세요:", height=150)
    
    if st.button("쿼리 실행"):
        if user_query:
            conn = create_connection()
            if conn:
                result = execute_query(conn, user_query)
                st.markdown("<h3 class='mysql-blue'>실행 결과:</h3>", unsafe_allow_html=True)
                st.markdown('<div class="result-area">', unsafe_allow_html=True)
                st.write(result)
                st.markdown('</div>', unsafe_allow_html=True)
                conn.close()
        else:
            st.warning("쿼리를 입력해주세요.")

# 앱 실행 방법 안내
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 class='mysql-blue'>앱 실행 방법</h3>", unsafe_allow_html=True)
st.sidebar.code("streamlit run app.py")
st.sidebar.markdown("---")
st.sidebar.info("이 앱은 MySQL classicmodels 데이터베이스를 사용합니다. 데이터베이스가 설치되어 있어야 합니다.")

# MySQL 버전 정보 표시
st.sidebar.markdown("<div style='position: fixed; bottom: 20px; left: 20px; opacity: 0.7;'>MySQL 8.0</div>", unsafe_allow_html=True)