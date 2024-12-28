from flask import (
	render_template,
	request,
	redirect,
	url_for,
	Blueprint,
	current_app,
	session,
	abort,
	flash
	)
import datetime,uuid,functools
from passlib.hash import pbkdf2_sha256
# from collections import defaultdict
 

# with open("config.json") as conf:
# 	params=json.load(conf)["params"]
# db_conn=params["connection_string"]


# app=Flask(__name__)

pages = Blueprint('habits',__name__,template_folder='templates',static_folder='static')

# client= MongoClient(db_conn)
# app.db=client.flask_blog  #client.collection/table name


# Udemyflask

'''
tasks = [
			("getmilk",False),
			("takemedicine",True)
		]
'''
# my_habits =[ "Reduce Phone","Manage Time" ]


# completed_tasks= defaultdict(list)

users={}

def today_at_midnight():
	today= datetime.datetime.today()
	return datetime.datetime(today.year,today.month,today.day)


def login_required(route):
	@functools.wraps(route)
	def route_wrapper(*args,**kwargs):
		if not session.get("email"):
			return redirect(url_for('habits.login'))
		return route(*args,**kwargs)
	return route_wrapper


# def admin_name():
# 	return "Somesh"


def date_range(start: datetime.date):
	dates =[start + datetime.timedelta(days=diff) for diff in range(-3,4)]
	return dates

@pages.context_processor
def date_range_func():
	return dict(date_range=date_range)



@pages.route('/post-details/<int:pid>')
def post_details(pid):
	return render_template('single_post.html')


@pages.route('/todo-details/<string:todo>/')
def single_todo(todo:str):
	for text,completed in tasks:
		if text == todo:
			completed_text = "[x]" if completed else "[]"
			title = f"{completed_text} - todos"
			return render_template('about.html',text=todo,completed=completed,title=title)
	else:
		# print("gotcha")
		return render_template('about.html',text=todo,title="Not found")


@pages.route('/')
@login_required
def list_habit():
	date_str = request.args.get("date")
	if date_str:
		selected_date = datetime.datetime.fromisoformat(date_str)
	else:
		selected_date = today_at_midnight()

	habit_on_date = current_app.db.habits.find({'added':{"$lte":selected_date}})

	completed_tasks =[ 
		habit["habit"] for habit in current_app.db.completions.find({"date":selected_date})
	]
	return render_template('habit_index.html',
		all_habits=habit_on_date,
		page_title="Habitat",
		selected_date=selected_date,
		completed_tasks=completed_tasks,
		email=session.get('email')
		)

@pages.route('/add-habit/',methods=["GET","POST"])
def add_habit():
	today = today_at_midnight()
	if request.method == "POST":
		new_habit = request.form.get("habit")
		# habits.append(new_habit)
		current_app.db.habits.insert_one({'_id':uuid.uuid4().hex,'added':today,'name':new_habit})
	return render_template('add_habit.html',page_title="New Habit",
		selected_date=today)


@pages.route('/complete/',methods=["POST"])
def mark_complete_task():
	date_str=request.form.get("date")
	habit = request.form.get("habitid")
	date_mod = datetime.datetime.fromisoformat(date_str)
	# completed_tasks[date_mod].append(habit)
	# print(completed_tasks)
	current_app.db.completions.insert_one({'date':date_mod,'habit':habit})
	return redirect(url_for("habits.list_habit",date=date_mod))



@pages.route("/login/",methods=["GET","POST"])
def login():
	if request.method=="POST":
		email = request.form["email"]
		password = request.form["password"]
		if email and password and users.get(email):
			if pbkdf2_sha256.verify(password,users.get(email)):
				session['email'] = email
				flash("Login Successfull")
				return redirect(url_for('habits.list_habit'))
		flash("Incorrect email or passowrd.")
	
	return render_template('login.html')

@pages.get("/protected")
def protected():
	if not session.get("email"):
		return redirect(url_for('habits.login'))
	return render_template("protected.html")

@pages.route("/signup/",methods=["GET","POST"])
def signup():
	if request.method=="POST":
		email = request.form["email"]
		password = request.form['password']
		users[email] = pbkdf2_sha256.hash(password) 
		flash("Successfully Signed Up")
		return redirect(url_for('habits.login'))
	return render_template("signup.html")

@pages.route('/logout/')
def log_out():
	if session.get('email'):
		session.clear()
		flash("Logout Successfull")
		return redirect(url_for('habits.login'))
	else:
		return redirect(url_for('habits.index'))

# @app.route('/mypage')
# def my_page():
# 	return "mypage"

# if __name__ == '__main__':
# 	app.run(debug=True)