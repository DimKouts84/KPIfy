#----------------------- Imports -----------------------#
from flask import Flask, render_template, request
from helpers import * 
import sqlite3, json, os, csv
from datetime import datetime
from numpy import mean, median

#----------------------- App Config. -----------------------#
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "static/csv_data"
app.debug = True


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/', methods=["GET", "POST"])
#---  Provide an overview for the current year ---#
def index():
    agent_names = []
    agent_performance = []
    for person in agent_performance_overview():
        agent_names.append(person["agentname"])
        agent_performance.append(person["performance"])
    agent_names = json.dumps(agent_names)
    averagetime = json.dumps(round(mean(agent_performance), 2))
    mediantime = json.dumps(round(median(agent_performance), 2))
    agent_performance = json.dumps(agent_performance)
    per_category_list = perCategory_numberAcquired_perAgent((datetime.now().year))
    yearnow = json.dumps(datetime.now().year)
    return render_template('index.html', agent_names=agent_names, agent_performance=agent_performance, per_category_list=per_category_list, averagetime=averagetime, mediantime=mediantime, yearnow=yearnow)


@app.route('/month', methods=["GET", "POST"])
#---  Provide a monthly analysis for each category of tasks ---#
def month():
    listofMonths = get_month()
    listofYears = get_year()
    
    if request.method == "GET":
            # Get Months & Years from the database.
        return render_template("month.html", months=listofMonths, years=listofYears)   
    
    if request.method == "POST":
        agent_names = []
        agent_performance = []
        # Get the year and month from user 
        year_from_form = request.form.get("year_select")
        month_from_form = request.form.get("month_select")
        # Loop for the overview chart of the department
        for person in agent_monthlyPerformance(year_from_form, month_from_form):
            agent_names.append(person["agentname"])
            agent_performance.append(person["performance"])
        AE_list = number_of_tasks_perCategory("AE", year_from_form, month_from_form)
        AP_list = number_of_tasks_perCategory("AP", year_from_form, month_from_form)
        IN_list = number_of_tasks_perCategory("INP", year_from_form, month_from_form)
        LB_list = number_of_tasks_perCategory("LB", year_from_form, month_from_form)
        NM_list = number_of_tasks_perCategory("NM", year_from_form, month_from_form)
        OS_list = number_of_tasks_perCategory("OS", year_from_form, month_from_form)
        PD_list = number_of_tasks_perCategory("PD", year_from_form, month_from_form)
        PH_list = number_of_tasks_perCategory("PH", year_from_form, month_from_form)
        first_name_list = get_user_first_name()
        workingHours_per_Agent = workingHours_perMonth_per_Agent(year_from_form, month_from_form)
        projectHours_per_Agent = projectHours_perMonth_per_Agent(year_from_form, month_from_form)
        averagetime = round(mean(agent_performance), 2)
        mediantime = round(median(agent_performance), 2)
        agent_names = json.dumps(agent_names)
        agent_effort_points = EffortPoints_perMonth(year_from_form, month_from_form)
        return render_template("month_analysis.html", months=listofMonths, years=listofYears, agent_names=agent_names, first_name_list=first_name_list, workingHours_per_Agent=workingHours_per_Agent, projectHours_per_Agent=projectHours_per_Agent, agent_performance=agent_performance, averagetime=averagetime, mediantime=mediantime, AE_list=AE_list, AP_list=AP_list, IN_list=IN_list, LB_list=LB_list, NM_list=NM_list, OS_list=OS_list, PD_list=PD_list, PH_list=PH_list, month_from_form=month_from_form, year_from_form=year_from_form, total_AE=sum(AE_list), total_AP=sum(AP_list), total_IN=sum(IN_list), total_LB=sum(LB_list), total_NM=sum(NM_list), total_OS=sum(OS_list), total_PD=sum(PD_list), total_PH=sum(PH_list), agent_effort_points=agent_effort_points)   
    
    return render_template("month.html", months=listofMonths, years=listofYears)


@app.route('/employee', methods=["GET", "POST"])
#---  Provide a performance analysis for each employee for currect year compared to the department average ---#
def employee():
    if request.method == "GET":
        return render_template("employee.html", listof_AgentName=get_user_first_name())
    
    if request.method == "POST":
        agent_name = request.form.get("agent_select")
        yearnow = datetime.now().year
        
        # Get an overview of the performance for each month per employee
        monthly_performance = monthly_perAgent_performanceOverview(agent_name)
        month_number = json.dumps([entry["month"] for entry in monthly_performance])
        performance_number = json.dumps([entry["performance"] for entry in monthly_performance])
        
        # Pass the individual performance to the clinet for each month, for each employee separately
        categories = ["AE", "AP", "INP", "LB", "NM", "OS", "PD", "PH"]
        AE_monthly, AP_monthly, IN_monthly, LB_monthly, NM_monthly, OS_monthly, PD_monthly, PH_monthly = [json.dumps(monthly_acquired_perCategory_individually(agent_name, category)) for category in categories]
        
        # Pass the performance to the client for each month, for the department, to compare with the individual
        dep_AE_monthly, dep_AP_monthly, dep_IN_monthly, dep_LB_monthly, dep_NM_monthly, dep_OS_monthly, dep_PD_monthly, dep_PH_monthly = [json.dumps(monthly_acquired_perCategory_department(category)) for category in categories]
        avg_department_monthly_performance_list = json.dumps(monthly_department_performanceOverview())        
        
        return render_template("employee_analysis.html", yearnow=yearnow, listof_AgentName=get_user_first_name(), agent_name=agent_name, month_number=month_number, performance_number=performance_number, AE_monthly=AE_monthly, AP_monthly=AP_monthly, IN_monthly=IN_monthly, LB_monthly=LB_monthly, NM_monthly=NM_monthly, OS_monthly=OS_monthly, PD_monthly=PD_monthly, PH_monthly=PH_monthly, dep_AE_monthly=dep_AE_monthly, dep_AP_monthly=dep_AP_monthly, dep_IN_monthly=dep_IN_monthly, dep_LB_monthly=dep_LB_monthly, dep_NM_monthly=dep_NM_monthly, dep_OS_monthly=dep_OS_monthly, dep_PD_monthly=dep_PD_monthly, dep_PH_monthly=dep_PH_monthly, avg_department_monthly_performance_list=avg_department_monthly_performance_list, agent_monthly_workingHours=agent_monthly_workingHours(agent_name), agent_monthly_projectHours=agent_monthly_projectHours(agent_name))
    
    return render_template("employee.html")


@app.route('/settings', methods=["GET", "POST"])
#---  Import performance and working hours data (from CSV), a new employee into the database and deactivate/activate an employee. ---#
def settings():
    # Create a list for all active employees and one for the inactive
    listof_Active_AgentName = get_Active_AgentName()
    listof_Inactive_AgentName = get_Inactive_AgentName()
    
    if request.method == "GET":
        return render_template('settings.html', listof_Active_AgentName=listof_Active_AgentName, listof_Inactive_AgentName=listof_Inactive_AgentName)

    if request.method == "POST":
        if request.files and "userPerformanceData" in request.files and "userWorkingHours" in request.files and "month_selected" in request.form and "year_selected" in request.form:
            month_selected = request.form.get("month_selected")
            year_selected = request.form.get("year_selected")
            userPerformanceData = request.files["userPerformanceData"]
            userWorkingHours = request.files["userWorkingHours"]
            performance_data = {}

            # Save the uploaded files to a temporary location
            performance_data_path = os.path.join(app.config['UPLOAD_FOLDER'], userPerformanceData.filename)
            user_working_hours_path = os.path.join(app.config['UPLOAD_FOLDER'], userWorkingHours.filename)
            userPerformanceData.save(performance_data_path)
            userWorkingHours.save(user_working_hours_path) 

            # Read the CSV files and populate the performance_data dictionary
            with open(performance_data_path, 'r') as csv_file:
                csvdata = csv.reader(csv_file)
                next(csvdata)
                for rows in csvdata:
                    if rows[0] not in performance_data:
                        performance_data[rows[0]] = {"clmhrs": 0, "prjhrs": 0, "AE": 0, "AP": 0, "IS": 0, "LB": 0, "NM": 0, "OS": 0, "PD": 0, "PH": 0}
                    performance_data[rows[0]][rows[1]] = rows[2]

            with open(user_working_hours_path, 'r') as csv_file:
                csvdata = csv.reader(csv_file)
                next(csvdata)
                for rows in csvdata:
                    if rows[0] not in performance_data:
                        performance_data[rows[0]] = {"clmhrs": 0, "prjhrs": 0, "AE": 0, "AP": 0, "IS": 0, "LB": 0, "NM": 0, "OS": 0, "PD": 0, "PH": 0}
                    performance_data[rows[0]]["clmhrs"] = int(rows[1])
                    performance_data[rows[0]]["prjhrs"] = int(rows[2])

            # Insert the performance_data from the dictionary into the database
            insert_performance_data(performance_data, year_selected, month_selected)
        
        # Function to add a new employee to the database.
        if "first-name" in request.form and "last-name" in request.form and "email" in request.form:
            # Import a new employee into the DB
            first_name_new_employee = request.form.get("first-name")
            last_name_new_employee = request.form.get("last-name")
            email_new_employee = request.form.get("email")
            # print(email_new_employee, first_name_new_employee, last_name_new_employee)
            insert_new_employee(email_new_employee, first_name_new_employee, last_name_new_employee)
        
        # Function to deactive an employee (not working anymore) and vice versa.
        if "deactive_agent_select" in request.form:
            # Deactivate an employee
            deactive_agent_select = request.form.get("deactive_agent_select")
            deactivate_employee(deactive_agent_select)
        elif "reactive_agent_select" in request.form:    
            # Reactivate the status of an employee
            reactive_agent_select = request.form.get("reactive_agent_select")
            reactivate_employee(reactive_agent_select)
        
        return render_template('settings.html', listof_Active_AgentName=get_Active_AgentName(), listof_Inactive_AgentName=get_Inactive_AgentName())    
    
    return render_template('settings.html')



if __name__ == '__main__':
    app.run()
    