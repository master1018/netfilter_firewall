import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import json
import requests
from streamlit_lottie import st_lottie
import pydeck as pdk
from remote import *
import numpy as np
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder

def aggrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    selection_mode = 'single' # 定义单选模式，多选为'multiple'
    enable_enterprise_modules = True # 设置企业化模型，可以筛选等
    #gb.configure_default_column(editable=True) #定义允许编辑
    
    return_mode_value = DataReturnMode.FILTERED  #__members__[return_mode]
    gb.configure_selection(selection_mode, use_checkbox=False) # 定义use_checkbox
    
    gb.configure_side_bar()
    gb.configure_grid_options(domLayout='normal')
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    #gb.configure_default_column(editable=True, groupable=True)
    gridOptions = gb.build()
    
    update_mode_value = GridUpdateMode.MODEL_CHANGED
    
    grid_response = AgGrid(
                        df, 
                        gridOptions=gridOptions,
                        fit_columns_on_grid_load = True,
                        data_return_mode=return_mode_value,
                        update_mode=update_mode_value,
                        enable_enterprise_modules=enable_enterprise_modules,
                        theme='streamlit'
                        )  

def callback1():
    st.session_state.connect = 1
    print("connect")

def init():
    if "connect" not in st.session_state:
        st.session_state.connect = 0
    if "con_msg" not in st.session_state:
        st.session_state.con_msg = []
    if "rule_list" not in st.session_state:
        st.session_state.rule_list = []


#Layout
init()

st.set_page_config(
    page_title="firewall",
    layout="wide",
    initial_sidebar_state="expanded")

#Data Pull and Functions
st.markdown("""
<style>
.big-font {
    font-size:80px !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)



#Options Menu
with st.sidebar:
    selected = option_menu('NFW', ["Config", 'Log','About'], 
        icons=['play-btn','search','info-circle'],menu_icon='intersect', default_index=0)
    lottie = load_lottiefile("similo3.json")
    st_lottie(lottie,key='loc')

#Intro Page
if selected=="Config":
    #Header
    st.title('Welcome to Netfilter-FireWall')
    st.subheader('*First you should connect your firewall host with user and passwd.*')

    st.divider()
    host = port = user = passwd = None
    #Use Cases
    with st.container():
        col1,col2=st.columns(2)
        with col1:
            st.header('Connect')
            c1, c2 = col1.columns(2)
            host = c1.text_input("host")
            port = c2.text_input("port")
            user = c1.text_input("user")
            passwd = c2.text_input("passwd")
            if st.session_state.connect != 2:
                st.session_state.con_msg = [host, port, user, passwd]

        with col2:
            lottie2 = load_lottiefile("place2.json")
            st_lottie(lottie2,key='place',height=300,width=300)

        c1, c2 = st.columns(2)
        with c1:
            st.button("CONNECT", on_click=callback1)
            
            if st.session_state.connect == 1:
                ret = check_connect(host, user, port, passwd)
                if ret:
                    st.session_state.connect = 2
        print(st.session_state.connect)
        with c2:
            if st.session_state.connect != 2:
                st.write("Not connect.❌")
            else:
                st.write("Success connect.✔")

    st.divider()

    st.session_state.connect = 2
    st.session_state.con_msg = ["192.168.247.139", "22", "root", "qwert12345"]

    if st.session_state.connect == 2:
    #Tutorial Video
        st.header('Base Config')
        select_mode = "accept"
        select_mode = st.selectbox("default mode", ["accept", "drop"])
        print(select_mode)
        print(st.session_state.con_msg)
        set_default_mode(select_mode, st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])

        with st.expander("Rule List"):
            st.session_state.rule_list = []
            rule_list = quert_rule_list(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])
            print("test")
            rule_list = rule_list.split("\n")
            if len(rule_list) >= 3:
                rule_list = rule_list[3: len(rule_list)]
                for i in range(0, len(rule_list)):
                    if "|" in rule_list[i]:
                        rule_list[i] = rule_list[i].split("|")
                        for j in range(0, len(rule_list[i])):
                            rule_list[i][j] = rule_list[i][j].strip()
                        st.session_state.rule_list.append(rule_list[i][1 : len(rule_list[i]) - 1])
            else:
                st.write("No rules.")

            
            if st.session_state.rule_list != []:

                df = pd.DataFrame(np.array(st.session_state.rule_list))
                df.columns = ["index", "src ip", "dst ip", "src port", "dst port", "protocol", "action", "log"]

                aggrid(df)

        with st.expander("Nat List"):
            st.write("ha~ha~")
    
#Search Page
if selected=="Search":
    st.write("hi")
#About Page
if selected=='About':
    st.write("hi")

