from flask import*
from database import *
admin=Blueprint("admin",__name__)
@admin.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')

@admin.route('/view_company', methods=['get', 'post'])
def view_company():
    data = {}
    s = """
        SELECT *
        FROM `company`
        INNER JOIN `login` USING (`login_id`)
    """
    data['value'] = select(s)
    
    if request.method == 'POST':
        action = request.form['action']
        login_id = request.form['login_id']
        company_id = request.form['company_id']
        
        if action == 'accept':
            u = "UPDATE login SET usertype='company' WHERE login_id='%s'" % (login_id)
            update(u)
            flash("Company Accepted")
            
        elif action == 'reject':
            d_company = "DELETE FROM company WHERE company_id='%s'" % (company_id)
            d_login = "DELETE FROM login WHERE login_id='%s'" % (login_id)
            delete(d_company)
            delete(d_login)
            flash("Company Rejected")
        
        return redirect(url_for('admin.view_company'))
    
    return render_template('admin_view_company.html', data=data)

@admin.route('/view_user', methods=['get', 'post'])
def view_user():
    data = {}
    s = """
        SELECT *, CONCAT(`fname`, ' ', `lname`) AS `name`
        FROM `user`
        INNER JOIN `login` USING (`login_id`)
    """
    data['value'] = select(s)
    
    if request.method == 'POST':
        action = request.form['action']
        login_id = request.form['login_id']
        user_id = request.form['user_id']
        
        if action == 'accept':
            u = "UPDATE login SET usertype='user' WHERE login_id='%s'" % (login_id)
            update(u)
            flash("User Accepted")
            
        elif action == 'reject':
            d_user = "DELETE FROM user WHERE user_id='%s'" % (user_id)
            d_login = "DELETE FROM login WHERE login_id='%s'" % (login_id)
            delete(d_user)
            delete(d_login)
            flash("User Rejected")
        
        return redirect(url_for('admin.view_user'))
    
    return render_template('admin_view_user.html', data=data)

@admin.route('/manage_brand',methods=['get','post'])
def manage_brand():
    data={}
    s="select * from brand"
    data['value']=select(s)
    if 'brand' in request.form:
        bane=request.form['bname']
        a="insert into brand values(null,'%s')"%(bane)
        insert(a)
        return redirect(url_for('admin.manage_brand'))
    if 'action' in request.args:
        action=request.args['action']
        id=request.args['id']
    else:
        action=None
    if action=='delete':
        b="delete from brand where brand_id='%s'"%(id)
        delete(b)
        return redirect(url_for('admin.manage_brand'))
    if action=='update':
        n="select * from brand where brand_id='%s'"%(id)
        data['up']=select(n)
    if 'update' in request.form:
        bname=request.form['bname']
        u="update brand set brand='%s' where brand_id='%s'"%(bname,id)
        update(u)
        return redirect(url_for('admin.manage_brand'))
    return render_template('admin_manage_brand.html',data=data)

@admin.route('/view_feedback',methods=['get','post'])
def view_feedback():
    data={}
    s="SELECT *,CONCAT(`fname`,' ',`lname`)AS name FROM `feedback` INNER JOIN `user` USING(`user_id`)"
    data['value']=select(s)
    return render_template('admin_view_feedback.html',data=data)


@admin.route('/aview_vehicle',methods=['get','post'])
def aview_vehicle():
    data={}
    id=request.args['id']
    s="select * from vehicle where company_id='%s'"%(id)
    data['value']=select(s)
    return render_template('admin_view_vehicles.html',data=data)