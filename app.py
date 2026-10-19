import streamlit as st
import graphviz
import re
import pandas as pd

# Set up page configurations
st.set_page_config(page_title="SchemaForge", layout="wide")

# Inject Custom CSS for Sleek Developer Dark Mode
st.markdown("""
<style>
    /* Dark App Background */
    .stApp {
        background-color: #0F172A;
    }
    
    /* Dark Column Cards */
    div[data-testid="column"] {
        background-color: #1E293B;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
        border: 1px solid #334155;
    }
    
    /* Typography adjustments - Added h4, h5, h6 to fix faded text */
    h1, h2, h3, h4, h5, h6, p {
        color: #F8FAFC !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Styling Streamlit text area */
    .stTextArea textarea {
        background-color: #0F172A;
        color: #F8FAFC;
        border: 1px solid #475569;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        color: #3B82F6 !important;
        font-weight: bold;
    }
</style>

""", unsafe_allow_html=True)

st.title("📊 SchemaForge: SQL to ERD Visualizer")
st.caption("A Python-powered database schema compiler & graph analytics tool.")
st.write("---")

col1, col2 = st.columns([1, 1.4])

with col1:
    st.subheader("📝 Input SQL DDL Script")

    sample_sql = """CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(100),
    building VARCHAR(50)
);

CREATE TABLE professors (
    prof_id INT PRIMARY KEY,
    prof_name VARCHAR(100),
    email VARCHAR(100),
    dept_id INT REFERENCES departments(dept_id)
);

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100),
    enrollment_year INT,
    major_dept_id INT REFERENCES departments(dept_id)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_title VARCHAR(150),
    credits INT,
    prof_id INT REFERENCES professors(prof_id)
);

CREATE TABLE enrollments (
    enroll_id INT PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    course_id INT REFERENCES courses(course_id),
    semester VARCHAR(20),
    grade VARCHAR(2)
);"""

    sql_input = st.text_area("Paste your SQL CREATE TABLE statements here:", value=sample_sql, height=600)

# Parsing Logic
def parse_sql_to_erd(sql_text):
    statements = sql_text.split(';')
    tables = {}
    relationships = []

    for stmt in statements:
        clean_stmt = re.sub(r'\s+', ' ', stmt.strip())
        if not clean_stmt or not clean_stmt.lower().startswith('create table'):
            continue
            
        match = re.search(r'create\s+table\s+(\w+)\s*\((.*)\)', clean_stmt, re.IGNORECASE)
        if not match:
            continue
            
        table_name = match.group(1).upper()
        body = match.group(2)

        columns = []
        raw_columns = re.split(r',\s*(?![^()]*\))', body)

        for col in raw_columns:
            col = col.strip()
            if not col:
                continue

            fk_match = re.search(r'(?:foreign\s+key\s*\(\w+\)\s*)?references\s+(\w+)\s*\(', col, re.IGNORECASE)
            col_parts = col.split()

            if len(col_parts) >= 2 and col_parts[0].lower() not in ['primary', 'foreign', 'constraint', 'unique']:
                col_name = col_parts[0]
                col_type = col_parts[1]

                if 'primary key' in col.lower():
                    col_name = f"🔑 {col_name} (PK)"
                elif fk_match:
                    col_name = f"🔗 {col_name} (FK)"

                columns.append(f"{col_name} : {col_type}")

            if fk_match:
                ref_table = fk_match.group(1).upper()
                relationships.append((table_name, ref_table)) # (Child, Parent)

        tables[table_name] = columns

    return tables, relationships

with col2:
    if sql_input.strip():
        try:
            tables, relationships = parse_sql_to_erd(sql_input)
            
            # Create modern UI Tabs
            tab1, tab2, tab3 = st.tabs(["🗂️ Detailed ER Diagram", "🕸️ Macro Topology", "📈 Vertex Analytics"])

            # -----------------------------------------
            # TAB 1: DETAILED ERD (Accurate Cardinality)
            # -----------------------------------------
            with tab1:
                st.markdown("#### Entity-Relationship Diagram")
                dot = graphviz.Digraph(comment='ERD')
                dot.attr(rankdir='LR', bgcolor='transparent')
                dot.attr('node', shape='none', fontname='Helvetica', margin='0')

                for table_name, cols in tables.items():
                    label_html = f'''<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" COLOR="#475569">
                    <TR><TD BGCOLOR="#3B82F6" ALIGN="CENTER" PAD="10"><FONT COLOR="#FFFFFF"><B>{table_name}</B></FONT></TD></TR>'''
                    
                    for col in cols:
                        label_html += f'<TR><TD BGCOLOR="#1E293B" ALIGN="LEFT" PAD="8"><FONT COLOR="#F8FAFC">{col}</FONT></TD></TR>'
                    
                    label_html += '</TABLE>'
                    dot.node(table_name, label=f'<{label_html}>')

                for source, target in relationships:
                    # Mathematically accurate Crow's Foot mapping (Child -> Parent = N:1)
                    dot.edge(source, target, dir='both', arrowtail='crow', arrowhead='none', color='#3B82F6', penwidth='2.5')

                st.graphviz_chart(dot, use_container_width=True)

            # -----------------------------------------
            # TAB 2: MACRO TOPOLOGY (Network Hierarchies)
            # -----------------------------------------
            with tab2:
                st.markdown("#### Macro Dependency Network")
                st.caption("Visualizes high-level graph clustering and table dependencies without column clutter.")
                macro_dot = graphviz.Digraph(comment='Topology')
                macro_dot.attr(rankdir='TB', bgcolor='transparent', splines='ortho')
                macro_dot.attr('node', shape='box', style='rounded,filled', fillcolor='#1E293B', color='#3B82F6', fontcolor='#F8FAFC', fontname='Helvetica', penwidth='2', pad='0.5')

                for table_name in tables.keys():
                    macro_dot.node(table_name, table_name)

                for source, target in relationships:
                    # Flow from Parent to Child for structural hierarchy
                    macro_dot.edge(target, source, color='#10B981', penwidth='2')

                st.graphviz_chart(macro_dot, use_container_width=True)

            # -----------------------------------------
            # TAB 3: VERTEX DEGREE ANALYTICS
            # -----------------------------------------
            with tab3:
                st.markdown("#### Node Vertex Degrees")
                st.caption("Analyzes the In-Degree (dependencies on this table) and Out-Degree (foreign keys mapping out) of each node.")
                
                # Calculate In-Degrees and Out-Degrees
                degree_data = {table: {"In-Degree": 0, "Out-Degree": 0} for table in tables.keys()}
                for child, parent in relationships:
                    if parent in degree_data:
                        degree_data[parent]["In-Degree"] += 1
                    if child in degree_data:
                        degree_data[child]["Out-Degree"] += 1

                df = pd.DataFrame.from_dict(degree_data, orient='index')
                
                if not df.empty:
                    # Use Streamlit's native highly aesthetic bar chart
                    st.bar_chart(df, color=["#10B981", "#3B82F6"], height=400)
                else:
                    st.info("Add some FOREIGN KEY constraints to see vertex degree analytics.")

            st.success("✨ Graph engine executed successfully!")

        except Exception as e:
            st.error(f"Error parsing SQL. Please check your syntax. Details: {e}")
    else:
        st.info("Waiting for SQL input...")