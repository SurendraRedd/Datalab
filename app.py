"""
This application contains the code related to the
new electric car application.
"""


__author__ = 'Surendra Reddy'
__version__ = '2.0'
__maintainer__ = 'Surendra Reddy'
__email__ = 'surendraelectronics@gmail.com'
__status__ = 'Prototype'

print('# ' + '=' * 78)
print(f'Author: {__author__}')
print(f'Version: {__version__}')
print(f'Maintainer: {__maintainer__}')
print(f'Email: {__email__}')
print(f'Status: {__status__}')
print('# ' + '=' * 78)

# Required packages importing
import streamlit as st
#from annotated_text import annotated_text
#from streamlit_metrics import metric, metric_row
#from st_card import st_card
from st_aggrid import AgGrid,GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_lottie import st_lottie

import datetime
import calendar
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# Database Creation & Connection
import sqlite3
from sqlite3 import Connection
import hashlib


# Header template
html_temp = """
    <body style="background-color:red;">
    <div style="background-color:tomato;padding:10px">
    <h3 style="color:white;text-align:center;"> Your Electric Car🚗</h3>
    </div>
    </body>
"""
# Hide Styles
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
# Page Config details
st.set_page_config(
        page_title = 'CarApp',
        page_icon = "🚗",
        layout = "wide",
        initial_sidebar_state = "expanded"
    )

contact_form = """
<form action="https://formsubmit.co/surendraelectronics@outlook.com" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""

URI_SQLITE_DB = "Bookings.db"
fridayList = []

def make_hashes(password):
    """Hashes function

    Args:
        password ([type]): password information

    Returns:
        [type]: hashkey value
    """
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    return hashed_text if make_hashes(password) == hashed_text else False

# Ag-Grid Implementation
def grid_table(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_side_bar()
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True)
    gridOptions = gb.build()
    grid_response = AgGrid(df, 
                gridOptions = gridOptions, 
                enable_enterprise_modules = True,
                fit_columns_on_grid_load = False,
                width='100%',
                theme = "dark",
                update_mode = GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True)
    df = grid_response['data']
    selected_rows = grid_response["selected_rows"]
    return df,selected_rows

# """
# check_same_thread = False is added to avoid same thread issue
# """
conn = sqlite3.connect(URI_SQLITE_DB, check_same_thread=False)
c = conn.cursor()

@st.cache(hash_funcs={Connection: id})
def get_connection(path: str):
    """[summary]

    Args:
        path (str): path of the sqllite db

    Returns:
        [type]: coonection value
    """
    return sqlite3.connect(path, check_same_thread=False)

def create_usertable(conn: Connection):
    """ Table creation function

    Args:
        conn (Connection): Connection
    """
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY,password TEXT)')

def add_userdata(conn: Connection,username,password):
    """Add User Infor to table

    Args:
        conn (Connection): Connection
        username ([type]): username
        password ([type]): password
    """
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def create_cardetailstable(conn: Connection):
    """ Table creation function

    Args:
        conn (Connection): Connection
    """
    c.execute('CREATE TABLE IF NOT EXISTS cardetailstable(username TEXT PRIMARY KEY,battery TEXT, model TEXT,tyre TEXT,basecost FLOAT,\
        totalcost FLOAT,purchase DATE, purchaseday TEXT)')

def add_cardetails(conn: Connection,username,battery,model,tyre,basecost,totalcost,purchase,purchaseday):
    c.execute('INSERT OR REPLACE INTO cardetailstable(username,battery,model,tyre,basecost,totalcost,purchase,purchaseday) \
        VALUES (?,?,?,?,?,?,?,?)',(username,battery,model,tyre,basecost,totalcost,purchase,purchaseday))
    conn.commit()

def login_user(conn: Connection,username,password):
    """User Login Function

    Args:
        conn (Connection): connection
        username ([type]): username
        password ([type]): password

    Returns:
        [type]: data from tabke
    """
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    return c.fetchall()

def view_all_items(conn: Connection):
    c.execute('SELECT * FROM cardetailstable')
    return c.fetchall()


# css function
def apply_css(file_name):
    """Apply the css to contact form
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def fetchFriday():
    global fridayList
    today = date.today()
    year, month = today.year, today.month

    n_months = 12
    friday = calendar.FRIDAY

    for _ in range(n_months):
        # get last friday
        c = calendar.monthcalendar(year, month)
        day_number = c[-1][friday] or c[-2][friday]

        # display the found date
        #print(date(year, month, day_number).isoformat())        

        fridayList.append(date(year, month, day_number).isoformat())

        # refine year and month
        if month < 12:
            month += 1
        else:
            month = 1
            year += 1

def load_lottieurl(url: str):
    r = requests.get(url)
    return None if r.status_code != 200 else r.json()

# main function
def main():
    """
    This function contains the streamlit code details
    """
    st.markdown(html_temp, unsafe_allow_html=True)
    #st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.image('https://imgd.aeplcdn.com/0x0/cw/static/landing-banners/homepage-d-2021.jpg?v=07072021')
    st.sidebar.info("""
                ## Packages:
                **Streamlit, st-card, streamlit-aggrid, streamlit-lottie, requests**
                - Installation: 
                - **pip install -r requirements.txt**
                """)
    url = "https://assets7.lottiefiles.com/private_files/lf30_mn61zlcj.json"
    lottie_url = url
    lottie_json = load_lottieurl(lottie_url)
    st_cont = st.sidebar.container()
    #st.sidebar.title("📖 SciLit ")
    with st_cont:
        st_lottie(lottie_json,height =100,width =200)

    # Add a selectbox to the sidebar:
    add_selectbox = st.sidebar.selectbox(
        'Navigation👇',        
        ('👤Login','👥Signup','🅰About')
    )

    if add_selectbox == '🅰About':
        st.sidebar.info('Version 1.0')
        st.header(":mailbox: Get In Touch With Me!")
        st.markdown(contact_form,unsafe_allow_html=True)
        apply_css("style/style.css")

    # elif add_selectbox == '💿Configure':
    #     # annotated_text(
    #     #     ("🙏Welcome", "to ⚡ electric", "#8ef" ),
    #     #     ("🏎car", "application.", "#afa" ),
    #     # )
    #     st.write('')
    #     with st.expander('🚘Car Specifications', expanded=True):
    #         # Using the "with" syntax
    #         with st.form(key='car_form'):
    #             text_input = st.text_input(label='Enter User Name')
    #             cols = st.columns (3)
    #             name = ['🔋Battery', '🎡Wheel', '☸Tires']
    #             options = [['40kph','60kph','80kph'], ['model1','model2','model3'],['Eco','Performance','Racing']]
    #             for i, col in enumerate(cols):
    #                 col.selectbox(name[i] + f'', options[i], key=i)
    #             submit_button = st.form_submit_button(label='Submit')
    #     #st.subheader('Choose your favourite features.')

    elif add_selectbox == '👥Signup':
        st.subheader("Create New Account")
        new_user = st.text_input("Username","") 
        new_password = st.text_input("Password",type='password')

        if st.button("Signup"):
            create_usertable(conn)
            add_userdata(conn,new_user,make_hashes(new_password))
            st.success("Account created successfully. Please Login to application.")

    elif add_selectbox == "👤Login":
        global fridayList
        fetchFriday()
        st.sidebar.info("Hint: admin,admin")
        st.subheader("**Please Login to the page !**")
        
        username = st.sidebar.text_input("Username","")
        password = st.sidebar.text_input("Password",type='password')
        # Create card details table
        create_cardetailstable(conn)
        
        if st.sidebar.checkbox("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(conn,username,check_hashes(password,hashed_pswd))
            if result:
                st.success("Logged In as {0!s}".format(username))
                st.subheader('')
                st.subheader('')
                st.subheader('')
                
                with st.expander('Electric Car Booking'):
                    st.subheader("Please fill the below form 👇")
                    # Using the "with" syntax
                    with st.form(key='car_form',clear_on_submit=True):
                        error = False
                        today = datetime.date.today()
                        #st.write(fridayList)
                        name = ['🔋Battery', '🎡Wheel', '☸Tires']
                        textOptions=['CarBattery', 'CarModel', 'CarTyre']
                        options = [['select','40kph','60kph','80kph'], ['select','model1','model2','model3'],['select','Eco','Performance','Racing']]
                        text_input = st.text_input('👥Enter User Name',help="UserName")
                        battery_input = st.selectbox(name[0], options[0], key=1,help=textOptions[0])
                        model_input = st.selectbox(name[1], options[1], key=2,help=textOptions[1])
                        tyre_input = st.selectbox(name[2], options[2], key=3,help=textOptions[2])
                        purchase_date = st.date_input('📅Planned Purchase Date', today,help='Purchase Date')                        
                        
                        #cols = st.columns(3)
                        #choice ={}
                        
                        # for i, col in enumerate(cols):
                        #     choice = col.selectbox(name[i], options[i], key=i,help=textOptions[i])
                        #     st.write(choice[0::][0::])

                        submit_button = st.form_submit_button(label='Submit🚇')
                        if submit_button:
                            finalPrice =float(0.0)
                            basePrice = float(12.0)
                            battery60Price=float(0.0)
                            battery80Price=float(0.0)
                            model2Price=float(0.0)
                            model3Price=float(0.0)
                            tyrePPrice=float(0.0)
                            tyreRPrice=float(0.0)
                            
                            # Check all the validations
                            if text_input =='':
                                st.error('User Name should not be blank')
                                error = True
                            if battery_input =='select' or model_input =='select' or tyre_input  =='select':
                                st.error('Please select valid battery or model or tyre values')
                                error = True
                            if model_input == 'model3':
                                if battery_input =='40kph':
                                    st.error('Model 3 -  Only available with 60 and 80 kwh batteries. Please change the battery size.')
                                    error = True
                            if tyre_input == 'Performance':
                                if model_input =='model1':
                                    st.error('Performance -  Only available with wheel model2 and model3. Please change the whhel model.')
                                    error = True

                            if not error:
                                # Additional Price
                                if battery_input == '60kph':
                                    battery60Price = float(2.5)
                                if battery_input == '80kph':
                                    battery80Price = float(6.0)
                                if model_input == 'model2':
                                    model2Price = float(150)
                                if (battery_input == '60kph' or battery_input == '80kph') and model_input == 'model3':
                                    model3Price = float(350)
                                if (tyre_input == 'Performance') and (model_input == 'model3' or model_input == 'model2'):
                                    tyrePPrice = float(80)
                                if (tyre_input == 'Racing') and (model_input == 'model3'):
                                    tyreRPrice = float(150) 

                                weekday = purchase_date.strftime("%A")

                                # Convert in to time stamp values
                                year, month, day = purchase_date.year, purchase_date.month, purchase_date.day
                                
                                # Apply the Friday Discount
                                checkdate = date(year, month, day).isoformat()
                                val = any(checkdate in x  for x in fridayList)
                                if val:
                                    st.write("Last Friday Discount applied to purchase")
                                    discountedPrice = float(2)
                                    finalPrice = basePrice + battery60Price + battery80Price + model2Price + model3Price + tyrePPrice + tyreRPrice - discountedPrice
                                else:
                                    discountedPrice = float(0)
                                    finalPrice = basePrice + battery60Price + battery80Price + model2Price + model3Price + tyrePPrice + tyreRPrice + discountedPrice #st.write("no")

                                # Add final details to the database
                                add_cardetails(conn,text_input,battery_input,model_input,tyre_input,basePrice,finalPrice,checkdate,weekday)

                            # st.markdown(f""" ##### Car Specification Details 👤UserName : {text_input}, \
                            #     🔋Battery : {battery_input}, 🎡Wheel : {model_input}, ☸Tyre : {tyre_input}, \
                            #     TotalCost(Euro): {finalPrice}""")
                            # st.info("👏Congratulations!! You booking is successful.")
                            st.balloons()

                st.header('')
                with st.expander('📊Reports'):
                    st.subheader("View Booking Details")
                    #result = view_all_items(conn)
                    dat = sqlite3.connect(URI_SQLITE_DB)
                    query = dat.execute("SELECT * From cardetailstable")
                    cols = [column[0] for column in query.description]
                    results= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
                    #st.dataframe(results)

                    # fig = go.Figure(data=[go.Table(
                    #     columnwidth =[2,1,1,1,1,1,1,1],
                    #     header=dict(values=list(results.columns),
                    #                 fill_color='#FD8E72',
                    #                 align='center'),
                    #     cells=dict(values=[results.username, results.battery, results.model, results.tyre, results.basecost, results.totalcost, results.purchase,results.purchaseday],
                    #             fill_color='#E5ECF6',
                    #             align='left'))
                    # ])                  
                    # fig.update_layout(margin=dict(l=5,r=5,b=10,t=10),
                    # paper_bgcolor='#F5F5F5')

                    # st.write(fig)

                    # labels = [results.columns[2],results.columns[1],results.columns[3]]
                    # values = [results.model,results.battery, results.tyre]

                    # fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
                    # st.write(fig)

                    #AgGrid(results)
                    res,sel = grid_table(results)

                st.header('')
                with st.expander('✨Metrics'):
                    # Metric Details
                    dat = sqlite3.connect(URI_SQLITE_DB)
                    query = dat.execute("SELECT count(*) From cardetailstable")
                    data = query.fetchall()
                    #st.metric(label="Current🚗Bookings", value=data[0][0], delta=1)
                    
                    #Battery
                    query40 = dat.execute("select count(*) FROM cardetailstable where battery='40kph'")
                    data40 = query40.fetchall()
                    query60 = dat.execute("select count(*) FROM cardetailstable where battery='60kph'")
                    data60 = query60.fetchall()
                    query80 = dat.execute("select count(*) FROM cardetailstable where battery='80kph'")
                    data80 = query80.fetchall()

                    # Wheels
                    querym1 = dat.execute("select count(*) FROM cardetailstable where model='model1'")
                    datam1 = querym1.fetchall()
                    querym2 = dat.execute("select count(*) FROM cardetailstable where model='model2'")
                    datam2 = querym2.fetchall()
                    querym3 = dat.execute("select count(*) FROM cardetailstable where model='model3'")
                    datam3 = querym3.fetchall()     

                    # Tyre
                    queryt1 = dat.execute("select count(*) FROM cardetailstable where tyre='Eco'")
                    datat1 = queryt1.fetchall()
                    queryt2 = dat.execute("select count(*) FROM cardetailstable where tyre='Performance'")
                    datat2 = queryt2.fetchall()
                    queryt3 = dat.execute("select count(*) FROM cardetailstable where tyre='Racing'")
                    datat3 = queryt3.fetchall()                  

                    #st.write("## Here's a single figure")
                    #metric("🚗Bookings", data[0][0])
                    st.write("")
                    st.write("")

                    #st_card('🚗Bookings', value=data[0][0], delta=1)

                    st.markdown("## Car Specification Details")
                    st.write("")
                    st.write("")

                    first_kpi, second_kpi, third_kpi = st.columns(3)

                    with first_kpi:
                        st.markdown("**🔋Battery**")
                        st.markdown(f"<h3 style='text-align: left; color: green;'>40kph: {data40[0][0]}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: left; color: green;'>60kph: {data60[0][0]}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: left; color: green;'>80kph: {data80[0][0]}</h3>", unsafe_allow_html=True)

                    with second_kpi:
                        st.markdown("**🎡Wheel**")
                        st.markdown(f"<h3 style='text-align: left; color: blue;'>Model1: {datam1[0][0]}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: left; color: blue;'>Model2: {datam2[0][0]}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: left; color: blue;'>Model3: {datam3[0][0]}</h3>", unsafe_allow_html=True)

                    with third_kpi:
                        st.markdown("**☸Tyre**")
                        st.markdown(f"<h3 style='text-align: left; color: grey;'>Eco: {datat1[0][0]}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: left; color: grey;'>Performance: {datat2[0][0]}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align: left; color: grey;'>Racing: {datat3[0][0]}</h3>", unsafe_allow_html=True)

                    # metric_row(
                    #     {
                    #         "🔋40Battery": data40[0][0],
                    #         "🔋60Battery": data60[0][0],
                    #         "🔋80Battery": data80[0][0],
                    #         "🎡Model1": datam1[0][0],
                    #         "🎡Model2": datam2[0][0],
                    #         "🎡Model3": datam3[0][0],                
                    #     }
                    # )                               
                                    
            else:
                st.warning("Incorrect Userid/Password")

    else:
        st.write('Reporting - Cars Status.')    

# main function call
if __name__ == '__main__':
    main()
