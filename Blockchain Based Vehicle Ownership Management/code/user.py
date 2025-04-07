from flask import *
from database import *
import uuid
from blk import *

user = Blueprint("user", __name__)

@user.route('/user_home')
def user_home():
    return render_template('user_home.html')


@user.route('/user_view_vehicles')
def user_view_vehicles():
    data = {}
    
    if 'action' in request.args:
        action=request.args['action']
        vid=request.args['vehicle_id']
        
    else:
        action=None
        vid=None
        
    if action=='book':
        jk="insert into booking values(null,'%s','%s',curdate(),'pending')"%(session['uid'],vid)
        insert(jk)
        import datetime
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # Load contract info as JSON
            contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
        id = web3.eth.get_block_number()
        message = contract.functions.add_bookings(int(id),
            int(session['uid']),
            int(vid),
           
            d,
            'pending'
            
        ).transact({"from":web3.eth.accounts[0]})
        
        
        return redirect(url_for('user.user_orders'))
    
    
    s = "select * from vehicle"
    data['vehicles'] = select(s)
    return render_template('user_view_vehicles.html', data=data)

@user.route('/user_view_features/<vehicle_id>')
def user_view_features(vehicle_id):
    data = {}
    s = "select * from features where vehicle_id='%s'" % (vehicle_id)
    data['features'] = select(s)
    return render_template('user_view_features.html', data=data)

@user.route('/user_view_specifications/<vehicle_id>')
def user_view_specifications(vehicle_id):
    data = {}
    s = "select * from specification where vehicle_id='%s'" % (vehicle_id)
    data['specifications'] = select(s)
    return render_template('user_view_specifications.html', data=data)

@user.route('/user_view_company_details/<vehicle_id>')
def user_view_company_details(vehicle_id):
    data = {}
    s = "select * from company where company_id=(select company_id from vehicle where vehicle_id='%s')" % (vehicle_id)
    data['companies'] = select(s)
    return render_template('user_view_company_details.html', data=data)



@user.route('/user_orders', methods=['get', 'post'])
def user_orders():
    data = {}
    user_id = session['uid']
    s = "select * from booking inner join vehicle using(vehicle_id) where user_id='%s'" % (user_id)
    data['value'] = select(s)
    return render_template('user_orders.html', data=data)


@user.route('/user_pay',methods=['post','get'])
def cust_food_pay():
    booking_id=request.args['booking_id']
    total=request.args['total']
    
    if 'btn' in request.form:
        py="insert into payment values(null,'%s','%s',curdate())"%(booking_id,total)
        insert(py)
        import datetime
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # Load contract info as JSON
            contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
        id = web3.eth.get_block_number()
        message = contract.functions.add_payment(int(id),
            int(booking_id),
            total,
            d
            
        ).transact({"from":web3.eth.accounts[0]})
        
        up="update booking set status='%s' where booking_id='%s'"%('paid',booking_id)
        update(up)
        flash("Paided")
        return redirect(url_for('user.user_orders'))
    return render_template('user_pay.html')




@user.route('/user_view_alloted_vehicle', methods=['get', 'post'])
def user_view_alloted_vehicle():
    data = {}
    query = """
        SELECT 
            booking.booking_id, 
            CONCAT(user.fname, ' ', user.lname) AS user_name, 
            vehicle.vehicles AS vehicle_name, 
            allotvehicle.allotvehicle_id,
            allotvehicle.chasisnumber, 
            allotvehicle.modelnumber, 
            allotvehicle.details, 
            allotvehicle.regusternumber 
        FROM 
            allotvehicle 
        INNER JOIN 
            booking ON allotvehicle.booking_id = booking.booking_id 
        INNER JOIN 
            user ON booking.user_id = user.user_id 
        INNER JOIN 
            vehicle ON booking.vehicle_id = vehicle.vehicle_id 
        WHERE 
            booking.user_id = '%s'
    """ % (session['uid'])
    data['value'] = select(query)
    return render_template('user_view_alloted_vehicle.html', data=data)





@user.route('/user_register_request', methods=['get', 'post'])
def user_register_request():
    data = {}
    allotvehicle_id = request.args['allotvehicle_id']
    # Fetch MVDs for the dropdown
    mvd_query = "SELECT * FROM mvd"
    data['mvds'] = select(mvd_query)
  
    
    # Fetch existing register requests
    request_query = """
        SELECT 
            registerrequest.registerrequest_id, 
            mvd.name AS mvd_name, 
            registerrequest.date, 
            registerrequest.status 
        FROM 
            registerrequest 
        INNER JOIN 
            mvd ON registerrequest.mvd_id = mvd.mvd_id 
        WHERE 
            registerrequest.allotvehicle_id = '%s'
    """ % (allotvehicle_id)
    data['requests'] = select(request_query)
    
    return render_template('user_register_request.html', data=data)



@user.route('/user_view_policy_request', methods=['get', 'post'])
def user_view_policy_request():
    data = {}
    allotvehicle_id = request.args['allotvehicle_id']
   
   
    # Fetch existing policy requests
    request_query = """
        SELECT 
            policyrequest.policyrequest_id, 
            policy.policydetails AS policy_name, 
            policyrequest.policynumber, 
            policyrequest.date, 
            policyrequest.status 
        FROM 
            policyrequest 
        INNER JOIN 
            policy ON policyrequest.policy_id = policy.policy_id 
        WHERE 
            policyrequest.allotvehicle_id = '%s'
    """ % (allotvehicle_id)
    data['requests'] = select(request_query)
    
    return render_template('user_view_policy_request.html', data=data)





# @user.route('/user_view_request_loan', methods=['get', 'post'])
# def user_view_request_loan():
#     data = {}
#     allotvehicle_id = request.args['allotvehicle_id']
#     # Fetch banks for the dropdown
   
    
    
#     # Fetch existing loan requests
#     request_query = """
#         SELECT 
#             loanrequest.loanrequest_id, 
#             bank.name AS bank_name, 
#             loanrequest.details, 
#             loanrequest.date, 
#             loanrequest.status 
#         FROM 
#             loanrequest 
#         INNER JOIN 
#             bank ON loanrequest.bank_id = bank.bank_id 
#         WHERE 
#             loanrequest.allotvehicle_id = '%s'
#     """ % (allotvehicle_id)
#     data['requests'] = select(request_query)
    
#     return render_template('user_view_request_loan.html', data=data)




# @user.route('/user_view_noc',methods=['post', 'get'])

# def user_view_noc():
#     data={}
#     lid=request.args['lid']
#     data['lid']=lid
#     rt="select * from noccertificate where loanrequest_id='%s'"%(lid)
#     data['view']=select(rt)  

#     return render_template('user_view_noc.html',data=data)





@user.route('/user_send_feedback',methods=['post', 'get'])

def user_send_feedback():
    data={}
    
    rt="select * from feedback where user_id='%s'"%(session['uid'])
    data['view']=select(rt)  
    
  
      
    if 'sub' in request.form:
        feedback=request.form['feedback']
        
        u="insert into feedback values(null,'%s','%s',curdate())"%(session['uid'],feedback)
        insert(u)
        return """<script>alert(' insertion completed');window.location='/user_send_feedback'</script>"""
    
    
    
    return render_template('user_send_feedback.html',data=data)




@user.route('/user_send_complaint',methods=['post', 'get'])

def user_send_complaint():
    data={}
    company_id=request.args['company_id']
    rt="select * from complaint where user_id='%s' and company_id='%s'"%(session['uid'],company_id)
    data['view']=select(rt)  
    
  
      
    if 'sub' in request.form:
        complaint=request.form['complaint']
        
        u="insert into complaint values(null,'%s','%s','%s','%s',curdate())"%(session['uid'],company_id,complaint,'pending')
        insert(u)
        return """<script>alert(' insertion completed');window.location='/user_view_vehicles'</script>"""
    
    
    
    return render_template('user_send_complaint.html',data=data)







# @user.route('/user_request_loan', methods=['get', 'post'])
# def user_request_loan():
#     data = {}
#     allotvehicle_id = request.args['allotvehicle_id']
#     # Fetch banks for the dropdown
#     bank_query = "SELECT * FROM bank"
#     data['banks'] = select(bank_query)
    
#     if 'submit' in request.form:
#         bank_id = request.form['bank_id']
#         details = request.form['details']
#         insert_query = "INSERT INTO loanrequest VALUES (null, '%s','%s', '%s', '%s', curdate(), 'pending')" % (allotvehicle_id,session['uid'],bank_id, details)
#         insert(insert_query)
        
#         import datetime
#         d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         with open(compiled_contract_path) as file:
#             contract_json = json.load(file)  # Load contract info as JSON
#             contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
#         contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
#         id = web3.eth.get_block_number()
#         message = contract.functions.add_loanrequest(int(id),
#             int(allotvehicle_id),
#             int(session['uid']),
#             int(bank_id),
#             details,
#             d,
#             'pending'
            
#         ).transact({"from":web3.eth.accounts[0]})
        
        
        
#         return redirect(url_for('user.user_request_loan', allotvehicle_id=allotvehicle_id))
    
#     # Fetch existing loan requests
#     request_query = """
#         SELECT 
#             loanrequest.loanrequest_id, 
#             bank.name AS bank_name, 
#             loanrequest.details, 
#             loanrequest.date, 
#             loanrequest.status 
#         FROM 
#             loanrequest 
#         INNER JOIN 
#             bank ON loanrequest.bank_id = bank.bank_id 
#         WHERE 
#             loanrequest.allotvehicle_id = '%s'
#     """ % (allotvehicle_id)
#     data['requests'] = select(request_query)
    
#     return render_template('user_request_loan.html', data=data)




@user.route('/generate_rc_book', methods=['GET'])
def generate_rc_book():
    allotvehicle_id = request.args.get('allotvehicle_id')
    
    # Get vehicle and user details
    query = """
        SELECT 
            allotvehicle.allotvehicle_id,
            allotvehicle.chasisnumber,
            allotvehicle.modelnumber,
            allotvehicle.details,
            allotvehicle.regusternumber,
            CONCAT(user.fname, ' ', user.lname) AS owner_name,
            user.phone,
            user.email,
            vehicle.vehicles AS vehicle_name,
            booking.date
        FROM
            allotvehicle
        INNER JOIN
            booking ON allotvehicle.booking_id = booking.booking_id
        INNER JOIN
            user ON booking.user_id = user.user_id
        INNER JOIN
            vehicle ON booking.vehicle_id = vehicle.vehicle_id
        WHERE
            allotvehicle.allotvehicle_id = '%s'
    """ % (allotvehicle_id)
    
    result = select(query)
    
    if not result:
        flash("Vehicle not found")
        return redirect(url_for('user.user_view_alloted_vehicle'))
    
    vehicle_data = result[0]
    
    # Check if registration number is pending
    if vehicle_data['regusternumber'] == 'pending':
        flash("Registration number is pending. Cannot generate RC Book.")
        return redirect(url_for('user.user_view_alloted_vehicle'))
    
    # Pass the data to the template
    return render_template('generate_rc_book.html', vehicle=vehicle_data)