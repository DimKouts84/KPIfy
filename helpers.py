#----------------------- Imports -----------------------#
import sqlite3, csv, statistics
from datetime import datetime


#----- Database reading and handling for users and tasks -----#
kpidb = sqlite3.connect("kpidb.db") 
kpidb.row_factory = lambda cursor, row: row[0]
dbcur = kpidb.cursor()
tasks = ['AE','AP','IS','LB','NM','OS','PD','PH']
users =  dbcur.execute('SELECT email FROM agent;').fetchall()


#----- Get a list with the names of all agents -----#
def get_user_first_name():
    kpidb = sqlite3.connect("kpidb.db") 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    user_first_name =  dbcur.execute('SELECT first_name FROM agent WHERE active = 1;').fetchall()
    return (user_first_name)

def get_months_in_current_year():
    kpidb = sqlite3.connect("kpidb.db") 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    month_list =  dbcur.execute(f'SELECT DISTINCT(month) FROM performance WHERE year = {datetime.now().year};').fetchall()
    return (month_list)

#----------------------------------------------------------------------------#
# Functions for the /INDEX page which is an annual overview of the department.
#----------------------------------------------------------------------------#
def agent_performance_overview():
# Returns a list of dictionaries. 
# The dictionaries are the claims per minute performance KPI, per category for each employee.
# The analysis is for the current year
    kpidb = sqlite3.connect("kpidb.db") 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    user_overview_performance = {'agentname': '', "performance": 0}
    user_overview_performance_list = []
    for name in get_user_first_name():
        total_claims = dbcur.execute('SELECT AVG(AE + AP + INP + LB + NM + OS + PD + PH) FROM performance WHERE year = ? AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email);', (datetime.now().year, name,)).fetchall()
        claim_hours = dbcur.execute('SELECT AVG(clmhrs) FROM performance WHERE year = ? AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email);', (datetime.now().year, name,)).fetchall()
        agent_performance = (round(total_claims[0] / (claim_hours[0] * 60), 2))
        user_overview_performance["agentname"] = name
        user_overview_performance["performance"] = agent_performance
        user_overview_performance_list.append(user_overview_performance.copy())
    return(user_overview_performance_list)


def perCategory_numberAcquired_perAgent(yearnow):
# Returns a list of dictionaries. 
# The dictionaries are the number of tasks acquired per category for each employee.
# The analysis is for the current year
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    dbcur = kpidb.cursor()
    task_list = ['AE','AP','INP','LB','NM','OS','PD','PH']
    category_per_agent_overview = {"AE": 0, "AP": 0, "INP": 0, "LB": 0, "NM": 0, "OS": 0, "PD": 0, "PH": 0}
    category_overview_list = []
    per_category_list = [[] for _ in range(8)]
    for name in get_user_first_name():
        claim_num_categ = dbcur.execute(
            'SELECT  AVG(AE) , AVG(AP) , AVG(INP) , AVG(LB) , AVG(NM) , AVG(OS) , AVG(PD) , AVG(PH) FROM performance WHERE year = ? AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email);', 
            (yearnow, name,)
        ).fetchall()[0]
        category_per_agent_overview["agentname"] = name
        for i, categ in enumerate(task_list):
            category_per_agent_overview[categ] = claim_num_categ[i]
            per_category_list[i].append(claim_num_categ[i])
        category_overview_list.append(category_per_agent_overview.copy())
    return per_category_list

#----------------------------------------------------------------------------#
# Functions for the /month page which is a monthly analysis of the department.
#----------------------------------------------------------------------------#
#----- Get a list of months -----#
def get_month():
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    month = dbcur.execute('SELECT DISTINCT month FROM performance;').fetchall()
    return month

#----- Get a list of the years -----#
def get_year():
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    year = dbcur.execute('SELECT DISTINCT year FROM performance;').fetchall()
    return year

#----- Get a list of the effort points for each task category -----#
def get_effort_points():
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    dbcur = kpidb.cursor()
    points = list(dbcur.execute('SELECT AE, AP, INP, LB, NM, OS, PD, PH FROM points;').fetchall()[0])
    return points

def agent_monthlyPerformance(year_from_form, month_from_form):
# Returns a list of dictionaries. 
# The dictionaries are the claims per minute performance KPI, per category for each employee.
# The analysis is for the selected year and month by the user
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    agent_monthly_overview_performance = {'agentname': '', "performance": 0}
    agent_monthly_overview_performance_list = []
    user_first_name =  dbcur.execute('SELECT first_name FROM agent WHERE active = 1 AND first_name IN (SELECT first_name FROM performance WHERE agent.email=performance.agent_email AND year = ? AND month = ?);', (year_from_form, month_from_form)).fetchall()
    for name in user_first_name:
        total_claims = dbcur.execute('SELECT DISTINCT(AE + AP + INP + LB + NM + OS + PD + PH) FROM performance WHERE year = ? AND month = ? AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email);', (year_from_form, month_from_form, name)).fetchall()
        claim_hours = dbcur.execute('SELECT DISTINCT clmhrs FROM performance WHERE year = ? AND month = ? AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email);', (year_from_form, month_from_form, name)).fetchall()
        agent_performance = (round(total_claims[0] / (claim_hours[0] * 60), 2))
        agent_monthly_overview_performance["agentname"] = name
        agent_monthly_overview_performance["performance"] = agent_performance
        agent_monthly_overview_performance_list.append(agent_monthly_overview_performance.copy())
    return agent_monthly_overview_performance_list

def number_of_tasks_perCategory(task_name, year_from_form, month_from_form):
# Return a list with the number of acquired tasks per agent for a specific tasks
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor() 
    number_of_tasks_perCategory_list = []
    user_first_name =  dbcur.execute('SELECT first_name FROM agent WHERE active = 1 AND first_name IN (SELECT first_name FROM performance WHERE agent.email=performance.agent_email AND year = ? AND month = ?);', (year_from_form, month_from_form)).fetchall()
    for agent_name in user_first_name:
        number_of_tasks_perCategory = dbcur.execute(f'SELECT {task_name} FROM performance WHERE year = {year_from_form} AND month = {month_from_form} AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email AND active = 1);', (agent_name,)).fetchall()
        number_of_tasks_perCategory_list.append(number_of_tasks_perCategory[0])
    return number_of_tasks_perCategory_list

def EffortPoints_perMonth(year_from_form, month_from_form):
    tasks = ['AE','AP','INP','LB','NM','OS','PD','PH']
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    # 1 List with the names
    user_first_name =  dbcur.execute('SELECT first_name FROM agent WHERE active = 1 AND first_name IN (SELECT first_name FROM performance WHERE agent.email=performance.agent_email AND year = ? AND month = ?);', (year_from_form, month_from_form)).fetchall()
    # 2 List with the acquired number of tasks for each employee:
    number_of_tasks_perCategory_small_list = []
    points = get_effort_points()
    # 3 For every agent we arrange the number of tasks acquired:
    for agent_name in user_first_name:
        agent_tasks = []
        for task in tasks:
            task_count = dbcur.execute(f'SELECT {task} FROM performance JOIN agent ON agent.email=performance.agent_email WHERE active = 1 AND year = {year_from_form} AND month = {month_from_form} AND agent.first_name = ?;', (agent_name,)).fetchone()
            agent_tasks.append(task_count)
        number_of_tasks_perCategory_small_list.append(agent_tasks)
    # 4 Get the working hours for each agent:
    agent_monthly_working_hours = workingHours_perMonth_per_Agent(year_from_form, month_from_form)
    # 5 We multiply every task_number for each agent with the effort point from the list,  we sum the total effor points divided with the agent working hours:
    total_effort_points = []
    for z, agent_tasks in enumerate(number_of_tasks_perCategory_small_list):
        agent_effort_points = []
        agent_hour = agent_monthly_working_hours[z]
        for i, task_count in enumerate(agent_tasks):
            effort_point = points[i]
            agent_effort_points.append((task_count * effort_point) / agent_hour)
        total_effort_points.append(round((sum(agent_effort_points)), 2))
    return total_effort_points

def workingHours_perMonth_per_Agent(year_from_form, month_from_form):
# Returns a list with the working hours per agent for a specific time period    
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    whorking_hours_list = []
    user_first_name =  dbcur.execute('SELECT first_name FROM agent WHERE active = 1 AND first_name IN (SELECT first_name FROM performance WHERE agent.email=performance.agent_email AND year = ? AND month = ?);', (year_from_form, month_from_form)).fetchall()
    for agent_name in user_first_name:
        whorking_hours = dbcur.execute(f'SELECT clmhrs FROM performance WHERE year = {year_from_form} AND month = {month_from_form} AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email AND active = 1);', (agent_name,)).fetchall()
        whorking_hours_list.append(whorking_hours[0])
    return whorking_hours_list

def projectHours_perMonth_per_Agent(yearnow, monthnow):
# Returns a list with the working hours in other projects per agent for a specific time period    
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    project_hours_list = []
    user_first_name =  dbcur.execute('SELECT first_name FROM agent WHERE active = 1 AND first_name IN (SELECT first_name FROM performance WHERE agent.email=performance.agent_email AND year = ? AND month = ?);', (yearnow, monthnow)).fetchall()
    for agent_name in user_first_name:
        project_hours = dbcur.execute(f'SELECT prjhrs FROM performance WHERE year = {yearnow} AND month = {monthnow} AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email AND active = 1);', (agent_name,)).fetchall()
        project_hours_list.append(project_hours[0])
    return project_hours_list


#----------------------------------------------------------------------------#
# Functions for the /employee page which is a per employee analysis of the department.
#----------------------------------------------------------------------------#

def agent_monthly_workingHours(agent_name):
# Returns a list with the working hours in other projects for current year for the selected employee
    kpidb = sqlite3.connect("kpidb.db") 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    whorking_hours_list = dbcur.execute(f'SELECT clmhrs FROM performance WHERE year = {datetime.now().year} AND "{agent_name}" IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email AND active = 1);').fetchall()
    return whorking_hours_list

def agent_monthly_projectHours(agent_name):
# Returns a list with the hours worked in other projects for current year for the selected employee
    kpidb = sqlite3.connect("kpidb.db") 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    project_hours_list = dbcur.execute(f'SELECT prjhrs FROM performance WHERE year = {datetime.now().year} AND "{agent_name}" IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email AND active = 1);').fetchall()
    return project_hours_list

def monthly_perAgent_performanceOverview(agent_name):
# It returns a dictiornary for the employee performance for all month in the current year.
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    user_monthly_performance = {'month': 0, "performance": 0}
    number_of_tasks_perCategory_list = []
    for month in get_month():
        total_claims = dbcur.execute(f'SELECT DISTINCT(AE + AP + INP + LB + NM + OS + PD + PH) FROM performance WHERE month = {month} AND year = {datetime.now().year} AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email AND active = 1);', (agent_name,)).fetchall()
        claim_hours = dbcur.execute(f'SELECT DISTINCT clmhrs FROM performance WHERE year = {datetime.now().year} AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email  AND active = 1);', (agent_name,)).fetchall()
        agent_performance = (round(total_claims[0] / (claim_hours[0] * 60), 2))
        user_monthly_performance["month"] = month
        user_monthly_performance["performance"] = agent_performance
        number_of_tasks_perCategory_list.append(user_monthly_performance.copy())
    return number_of_tasks_perCategory_list

#  Returns a list of the average performance per month for the department. 
#  This is used to compare the employee / department performance
def monthly_department_performanceOverview():
    kpidb = sqlite3.connect("kpidb.db", check_same_thread=False) 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    avg_department_monthly_performance_list = []
    for month in get_month():
        total_claims = dbcur.execute(f'SELECT SUM(AE + AP + INP + LB + NM + OS + PD + PH) FROM performance WHERE year = {datetime.now().year} AND month = {month}').fetchall()
        claim_hours = dbcur.execute(f'SELECT SUM(clmhrs) FROM performance WHERE year = {datetime.now().year} AND month = {month};').fetchall()
        avg_department_monthly_performance_list.append((round(total_claims[0] / (claim_hours[0] * 60), 2)))
    return avg_department_monthly_performance_list

def monthly_acquired_perCategory_individually(agent_name, task_name):
# Returns a list of numbers for a specific task for all the months of current year.
    kpidb = sqlite3.connect("kpidb.db") 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    number_of_tasks_perCategory_perMonth_list = []
    number_of_tasks_perCategory_perMonth_list = dbcur.execute(f'SELECT {task_name} FROM performance WHERE year = {datetime.now().year} AND ? IN (SELECT first_name FROM agent WHERE agent.email=performance.agent_email AND active = 1);', (agent_name,)).fetchall()
    return number_of_tasks_perCategory_perMonth_list

def monthly_acquired_perCategory_department(task_name):
# Returns a list of numbers for a specific task for all the months of current year.
    kpidb = sqlite3.connect("kpidb.db") 
    kpidb.row_factory = lambda cursor, row: row[0]
    dbcur = kpidb.cursor()
    number_of_tasks_perCategory_perMonth_list = []
    for month in get_months_in_current_year():
        number_of_tasks_perCategory_perMonth = dbcur.execute(f'SELECT AVG({task_name}) FROM performance WHERE year = {datetime.now().year} AND month = {month};').fetchall()
        number_of_tasks_perCategory_perMonth_list.append(number_of_tasks_perCategory_perMonth[0])
    return number_of_tasks_perCategory_perMonth_list

def EffortPoints_perEmployee_forCurrentYear():
    return 

#----------------------------------------------------------------------------#
# Functions for the /settings page to import employee data into the DB and change status (active/inactive).
#----------------------------------------------------------------------------#
# Function that inserts the user data (name, hours worked and nuber of each task completed) into the database, for a specific month of year
def insert_performance_data(performance_data, year_selected, month_selected):
    with sqlite3.connect("kpidb.db", check_same_thread=False) as kpidb:
        kpidb.row_factory = lambda cursor, row: row[0]
        dbcur = kpidb.cursor()
        for user, data in performance_data.items():
            dbcur.execute("INSERT INTO performance (year, month, clmhrs, prjhrs, AE, AP, INP, LB, NM, OS, PD, PH, agent_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (year_selected, month_selected, data["clmhrs"], data["prjhrs"], data["AE"], data["AP"], data["IS"], data["LB"], data["NM"], data["OS"], data["PD"], data["PH"], user))

#  Function that inserts a new employee into the database.
def insert_new_employee(email_new_employee, first_name_new_employee, last_name_new_employee):
    with sqlite3.connect("kpidb.db", check_same_thread=False) as kpidb:
        kpidb.row_factory = lambda cursor, row: row[0]
        dbcur = kpidb.cursor()
        return dbcur.execute("INSERT INTO agent (email, first_name, last_name, active) VALUES (?, ?, ?, 1);", (email_new_employee, first_name_new_employee, last_name_new_employee))

def get_Active_AgentName():
    with sqlite3.connect("kpidb.db", check_same_thread=False) as kpidb:
        kpidb.row_factory = lambda cursor, row: row[0]
        dbcur = kpidb.cursor()
        return dbcur.execute('SELECT first_name last_name FROM agent WHERE active = 1;').fetchall()

def get_Inactive_AgentName():
    with sqlite3.connect("kpidb.db", check_same_thread=False) as kpidb:
        kpidb.row_factory = lambda cursor, row: row[0]
        dbcur = kpidb.cursor()
        return dbcur.execute('SELECT first_name, last_name FROM agent WHERE active = 0;').fetchall()
    
    
def deactivate_employee(agent_name):
    with sqlite3.connect("kpidb.db", check_same_thread=False) as kpidb:
        kpidb.row_factory = lambda cursor, row: row[0]
        dbcur = kpidb.cursor()
        return dbcur.execute(f"UPDATE agent SET active = 0 WHERE first_name = '{agent_name}';")
    
def reactivate_employee(agent_name):
    with sqlite3.connect("kpidb.db", check_same_thread=False) as kpidb:
        kpidb.row_factory = lambda cursor, row: row[0]
        dbcur = kpidb.cursor()
        return dbcur.execute(f"UPDATE agent SET active = 1 WHERE first_name = '{agent_name}';")
    

