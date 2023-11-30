from cProfile import label
from cmath import log
from distutils.command.config import config
from distutils.command.upload import upload
from turtle import color, shape, width
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import json
import requests
from streamlit_lottie import st_lottie
import pydeck as pdk
from remote import *
import numpy as np
import copy
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder
from streamlit_agraph import agraph, Node, Edge, Config

def build_node_graph(src_list, dst_list, edge_label, w=800, h=950 / 4):
    nodes = []
    edges = []
    new_list1 = copy.deepcopy(src_list)
    new_list2 = copy.deepcopy(dst_list)

    new_list1.extend(new_list2)
    new_list1 = list(set(new_list1))

    for i in range(0, len(new_list1)):
        node = Node(id = new_list1[i],
                    label = new_list1[i],
                    size=15,
                    shape="cirularImage",
                    color = "blue"
                )
        nodes.append(node)

    for i in range(0, len(edge_label)):
        edges.append(Edge(source=src_list[i], label=edge_label[i], target=dst_list[i]))

    config = Config(
                        width=w,
                        height=h,
                        directed=True,
                        physics=True,
                        hierarchical=False
    )

    return_value = agraph(nodes=nodes, edges=edges, config=config)

    return return_value    

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
    st.session_state.connect = 2
    print("connect")

def callback_add():
    add_rule_list(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])

def callback_del():
    if st.session_state.del_index != -1:
        del_rule_list(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3], st.session_state.del_index)
        st.session_state.del_index = -1

def callback_del_nat():
    if st.session_state.del_index_nat != -1:
        del_nat_list(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3], st.session_state.del_index_nat)
        st.session_state.del_index_nat = -1

def callback_add_nat():
    add_nat_list(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])

    

def init():
    if "connect" not in st.session_state:
        st.session_state.connect = 0
    if "con_msg" not in st.session_state:
        st.session_state.con_msg = []
    if "rule_list" not in st.session_state:
        st.session_state.rule_list = []
    if "del_index" not in st.session_state:
        st.session_state.del_index = -1
    if "del_index_nat" not in st.session_state:
        st.session_state.del_index_nat = -1
    if "nat_list" not in st.session_state:
         st.session_state.nat_list = []
    if "log" not in st.session_state:
        st.session_state.log = []
    if "connect_log" not in st.session_state:
         st.session_state.connect_record = []
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
            
           # if st.session_state.connect == 1:
           #     ret = check_connect(host, user, port, passwd)
           #     if ret:
           #         st.session_state.connect = 2
        with c2:
            if st.session_state.connect != 2:
                st.write("Not connect.❌")
            else:
                st.write("Success connect.✔")
                st.session_state.con_msg = ["192.168.247.139", "22", "root", "qwert12345"]

    st.divider()


    if st.session_state.connect == 2:
    #Tutorial Video
        st.header('Base Config')
        select_mode = "accept"
        select_mode = st.selectbox("default mode", ["accept", "drop"])
        set_default_mode(select_mode, st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])

        with st.expander("Rule List"):
            st.session_state.rule_list = []
            rule_list = quert_rule_list(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])
            #print("test")
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

            st.text("Add new Rule by File upload:")
            upload_file = st.file_uploader("upload rule list", type="json")
            if upload_file is not None:
                f = open('tmp', "w")
                print(upload_file.read().decode('utf-8'), file=f)
                f.close()
                upload_file = None
            st.button("add rule", on_click=callback_add)
            st.json({
                'index':1,
                'src ip':'1.2.3.4',
                'src port':'1234',
                'dst ip':'3.4.5.6',
                'dst port':'5678',
                'protocol':'TCP',
                'action':'drop',
                'log':1
            }
            )
            c1, c2 = st.columns(2)
            st.session_state.del_index = c1.text_input("Delete rule Index")
            c2.write(" ")
            c2.write(" ")
            c2.button("Delete rule", on_click=callback_del)

        with st.expander("Nat List"):
            st.session_state.nat_list = []
            nat_list_str = query_nat_list(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])
            nat_list = nat_list_str.split('\n')
            if len(nat_list) > 3:
                nat_list = nat_list[3: len(nat_list)]
                for i in range(0, len(nat_list)):
                    if "|" in nat_list[i]:
                        tmp = nat_list[i].split('|')
                        for j in range(0, len(tmp)):
                            tmp[j] = tmp[j].strip()
                            if "~" in tmp[j]:
                                tmp[j] = tmp[j][0: tmp[j].find("~")]
                        del tmp[3]
                        st.session_state.nat_list.append(tmp[1: len(tmp) - 1])
            if st.session_state.nat_list != []:
                df = pd.DataFrame(np.array(st.session_state.nat_list))
                df.columns = ["index", "src ip", "nat ip", "nat port"]
                aggrid(df)
            
            st.text("Add new Nat by File upload:")
            upload_file = st.file_uploader("upload nat list", type="json")
            if upload_file is not None:
                f = open('tmp', "w")
                print(upload_file.read().decode('utf-8'), file=f)
                f.close()
                upload_file = None
            st.button("add nat", on_click=callback_add_nat)

            c1, c2 = st.columns(2)
            st.session_state.del_index_nat = c1.text_input("Delete nat Index")
            c2.write(" ")
            c2.write(" ")
            c2.button("Delete nat", on_click=callback_del_nat)

#Search Page
if selected=="Log":
    with st.expander("filter log"):
        st.session_state.log = []
        log_msg = query_log(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])
        log_msg = log_msg.split('\n')
        new_log = ""
        for i in range(1, len(log_msg) - 1):
            idx = log_msg[i].find("len=")
            if "DROP" in log_msg[i]:
                new_log += "❌" + log_msg[i][0: idx - 1] + "\n"
            else:
                new_log += "✅" + log_msg[i][0: idx - 1] + "\n"
        new_log_list = new_log.split('\n')
        for i in range(0, len(new_log_list) - 1):
            tmp = []
            tmp.append(new_log_list[i][0])
            s_idx = new_log_list[i].find("[")
            e_idx = new_log_list[i].find("]")
            tmp.append(new_log_list[i][s_idx + 1: e_idx])
            try:
                tmp.append((new_log_list[i].split(" "))[6])
            except:
                tmp.append((new_log_list[i].split(" "))[4])
            try:
                tmp_protocol = (new_log_list[i].split(" "))[7]
            except:
                tmp_protocol = (new_log_list[i].split(" "))[5]
            tmp.append(tmp_protocol[tmp_protocol.find("=") + 1 : len(tmp_protocol)])
            st.session_state.log.append(tmp)
        
        if st.session_state.log != []:
            df = pd.DataFrame(np.array(st.session_state.log))
            df.columns = ["action", "time", "flow", "protocol"]
            aggrid(df)

        else:
            new_log = "No log record."
    with st.expander("connect record"):
        st.session_state.connect_record = []
        connect_record_str = query_connect_record(st.session_state.con_msg[0], st.session_state.con_msg[1], st.session_state.con_msg[2], st.session_state.con_msg[3])
        connect_list = connect_record_str.split('\n')
        for i in range(0, len(connect_list)):
            tmp = connect_list[i]
            if "ICMP" in tmp:
                continue
            if "|" in tmp:
                tmp = tmp.split("|")
                tmp = tmp[1 : len(tmp) - 1]
                for j in range(0, len(tmp)):
                    tmp[j] = tmp[j].strip()
                st.session_state.connect_record.append(tmp)
        if st.session_state.connect_record != []:
            #print(st.session_state.connect_record)
            src_list = []
            dst_list = []
            edge_label = []

            for i in range(0, len(st.session_state.connect_record)):
                tmp = st.session_state.connect_record[i]
                src_list.append(tmp[1])
                dst_list.append(tmp[3])
                edge_label.append(tmp[0])

            build_node_graph(src_list, dst_list, edge_label, 1200, 950)

#About Page
if selected=='About':
    st.write("hi")

