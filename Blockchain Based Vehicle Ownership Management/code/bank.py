from flask import *
from database import *

bank = Blueprint("bank", __name__)

@bank.route('/bank_home')
def bank_home():
    return render_template('bank_home.html')

@bank.route('/bank_view_loan_request', methods=['get', 'post'])
def bank_view_loan_request():
    data = {}
    query = """
        SELECT 
            loanrequest.loanrequest_id, 
            loanrequest.details, 
            loanrequest.user_id, 
            loanrequest.date, 
            loanrequest.status, 
            CONCAT(user.fname, ' ', user.lname) AS user_name, 
            vehicle.vehicles AS vehicle_name 
        FROM 
            loanrequest 
        INNER JOIN 
            allotvehicle ON loanrequest.allotvehicle_id = allotvehicle.allotvehicle_id 
        INNER JOIN 
            booking ON allotvehicle.booking_id = booking.booking_id 
        INNER JOIN 
            user ON booking.user_id = user.user_id 
        INNER JOIN 
            vehicle ON booking.vehicle_id = vehicle.vehicle_id 
        WHERE 
            loanrequest.bank_id = '%s'
    """ % (session['bid'])
    data['value'] = select(query)
    
    if 'action' in request.form:
        action = request.form['action']
        loanrequest_id = request.form['loanrequest_id']
        if action == 'accept':
            update_query = "UPDATE loanrequest SET status='accepted' WHERE loanrequest_id='%s'" % (loanrequest_id)
        elif action == 'reject':
            update_query = "UPDATE loanrequest SET status='rejected' WHERE loanrequest_id='%s'" % (loanrequest_id)
        update(update_query)
        return redirect(url_for('bank.bank_view_loan_request'))
    
    return render_template('bank_view_loan_request.html', data=data)




import uuid

@bank.route('/bank_provide_noc',methods=['post', 'get'])

def admin_add_image():
    data={}
    lid=request.args['lid']
    data['lid']=lid
    rt="select * from noccertificate where loanrequest_id='%s'"%(lid)
    data['view']=select(rt)  
    
    
   
    if 'sub' in request.form:
       
        photo=request.files['img']
        path="static/images"+str(uuid.uuid4())+photo.filename
        photo.save(path)
        
        u="insert into noccertificate values(null,'%s','%s',curdate())"%(lid,path)
        insert(u)
        flash("NOC Certificate Added Successfully")
        return redirect(url_for('bank.bank_view_loan_request'))  
    
    
    
    return render_template('bank_provide_noc.html',data=data)






@bank.route('/bank_view_user',methods=['get','post'])
def bank_view_user():
    data={}
    uid=request.args['uid']
    s="select *,concat(`fname`,' ',`lname`)as `name` from `user` where user_id='%s'"%(uid)
    print(s,'//////////')
    data['value']=select(s)
    return render_template('bank_view_user.html',data=data)