from flask import *
from database import*
import uuid

from blk import *

company=Blueprint("company",__name__)
@company.route('/company_home')
def company_home():
    return render_template('company_home.html')

@company.route('/view_brand',methods=['get','post'])
def view_brand():
    data={}
    a="select * from brand"
    data['value']=select(a)
    return render_template('company_view_brand.html',data=data)

@company.route('/manage_vehicle',methods=['get','post'])
def manage_vehicle():
    id=request.args['id']
    data={}
    if 'vehicle' in request.form:
        name=request.form['name']
        
        amount=request.form['amount']
       
        a="insert into vehicle values(null,'%s','%s','%s','%s')"%(session['sid'],id,name,amount)
        insert(a)
        return redirect(url_for('company.manage_vehicle',id=id))
    s="select * from vehicle where brand_id='%s' and company_id='%s'"%(id,session['sid'])   
    data['value']=select(s)
    if 'action' in request.args:
        action=request.args['action']
        vid=request.args['vid']
        id=request.args['id']
    else:
        action=None
    if action=='delete':
        r="delete from vehicle where vehicle_id='%s'"%(vid) 
        delete(r)
        return redirect(url_for('company.manage_vehicle',id=id))
    if action=='update':
        a="select * from vehicle where vehicle_id='%s'"%(vid) 
        data['up']=select(a)
    if 'update' in request.form:
        name=request.form['name']
        
        
        amount=request.form['amount']
       
        b="update vehicle set vehicles='%s',amt='%s' where vehicle_id='%s'"%(name,amount,vid) 
        update(b)
        return redirect(url_for('company.manage_vehicle',id=id))
    return render_template('company_manage_vehicle.html',data=data)

@company.route('/add_features',methods=['get','post'])
def add_features():
    data={}
    vid=request.args['vid']
    if 'submit' in request.form:
        feature=request.form['feature']
        a="insert into features values(null,'%s','%s')"%(vid,feature)
        insert(a)
    e="select * from features where vehicle_id='%s'"%(vid)
    data['value']=select(e)
    return render_template('company_add_features.html',data=data)

@company.route('/specification',methods=['get','post'])
def specification():
    data={}
    vid=request.args['vid']
    if 'submit' in request.form:
        specification=request.form['specification']
        a="insert into specification values(null,'%s','%s')"%(vid,specification)
        insert(a)
    e="select * from specification where vehicle_id='%s'"%(vid)
    data['value']=select(e)
    return render_template('company_add_specification.html',data=data)

@company.route('/view_orders', methods=['get', 'post'])
def view_orders():
    data = {}
    s = """
        SELECT *, CONCAT(`fname`, ' ', `lname`) AS `fname`
        FROM `booking`
        INNER JOIN `vehicle` USING(`vehicle_id`)
        INNER JOIN `user` USING(`user_id`)
        WHERE `company_id`='%s'
    """ % (session['sid'])
    data['value'] = select(s)
    
    if request.method == 'POST':
        action = request.form['action']
        booking_id = request.form['booking_id']
        qq="select * from booking where booking_id='%s'" %(booking_id)
        rrr=select(qq)
        if action == 'accept':
            u = "UPDATE booking SET status='Accepted' WHERE booking_id='%s'" % (booking_id)
            import datetime
            d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(compiled_contract_path) as file:
                contract_json = json.load(file)  # Load contract info as JSON
                contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
            contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
            
            id = web3.eth.get_block_number()
            message = contract.functions.add_bookings(int(id),
                int(session['uid']),
                int(rrr[0]['vehicle_id']),
            
                d,
                'Accepted'
                
            ).transact({"from":web3.eth.accounts[0]})
            
            
        elif action == 'reject':
            u = "UPDATE booking SET status='Rejected' WHERE booking_id='%s'" % (booking_id)
            import datetime
            d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(compiled_contract_path) as file:
                contract_json = json.load(file)  # Load contract info as JSON
                contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
            contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
            
            id = web3.eth.get_block_number()
            message = contract.functions.add_bookings(int(id),
                int(session['uid']),
               int(rrr[0]['vehicle_id']),
            
                d,
                'Rejected'
                
            ).transact({"from":web3.eth.accounts[0]})
        update(u)
        return redirect(url_for('company.view_orders'))
    
    return render_template('company_view_order.html', data=data)

@company.route('/view_complaint',methods=['get','post'])
def view_complaint():
    data={}
    s="SELECT * ,CONCAT(`fname`,' ',`lname`)AS `fname` FROM `complaints` INNER JOIN `user` USING(`user_id`) WHERE `company_id`='%s'"%(session['sid'])
    data['value']=select(s)
    if 'send' in request.form:
        replay=request.form['replay']
        id=request.form['id']
        a="update complaint set reply='%s' where complaint_id='%s'"%(replay,id)
        update(a)
        return redirect(url_for('company.view_complaint'))
    return render_template('company_view_complaint.html',data=data)

@company.route('/allot_vehicle', methods=['get', 'post'])
def allot_vehicle():
    booking_id = request.args['booking_id']
    if 'allot' in request.form:
        chasisnumber = request.form['chasisnumber']
        modelnumber = request.form['modelnumber']
        details = request.form['details']
        # regusternumber = request.form['regusternumber']
        regusternumber="pending"
        a = "insert into allotvehicle values(null, '%s', '%s', '%s', '%s', '%s')" % (booking_id, chasisnumber, modelnumber, details, regusternumber)
        insert(a)
        
        import datetime
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # Load contract info as JSON
            contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        id = web3.eth.get_block_number()
        message = contract.functions.add_allotvehicles(int(id),
            int(booking_id),
            chasisnumber,
            modelnumber,
            details,
            regusternumber
        ).transact({"from":web3.eth.accounts[0]})
        
        # Update booking status to "alloted"
        b = "update booking set status='alloted' where booking_id='%s'" % (booking_id)
        update(b)
        return redirect(url_for('company.view_orders'))
    return render_template('company_allot_vehicle.html')

@company.route('/view_alloted_vehicle', methods=['get', 'post'])
def view_alloted_vehicle():
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
            vehicle.company_id = '%s'
    """ % (session['sid'])
    data['value'] = select(query)
    return render_template('company_view_alloted_vehicle.html', data=data)

@company.route('/company_register_request', methods=['get', 'post'])
def company_register_request():
    data = {}
    allotvehicle_id = request.args['allotvehicle_id']
    # Fetch MVDs for the dropdown
    mvd_query = "SELECT * FROM mvd"
    data['mvds'] = select(mvd_query)
    
    if 'submit' in request.form:
        mvd_id = request.form['mvd_id']
       
        insert_query = "INSERT INTO registerrequest VALUES (null,'%s','%s',curdate(),'pending')" % (mvd_id, allotvehicle_id)
        insert(insert_query)
        
        import datetime
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # Load contract info as JSON
            contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
        id = web3.eth.get_block_number()
        message = contract.functions.add_registerrequest(int(id),
            int(mvd_id),
            int(allotvehicle_id),
            d,
            'pending'
            
        ).transact({"from":web3.eth.accounts[0]})
        
        
        return redirect(url_for('company.company_register_request', allotvehicle_id=allotvehicle_id))
    
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
    
    return render_template('company_register_request.html', data=data)

@company.route('/company_policy_request', methods=['get', 'post'])
def company_policy_request():
    data = {}
    allotvehicle_id = request.args['allotvehicle_id']
    # Fetch policies for the dropdown
    policy_query = "SELECT * FROM policy"
    data['policies'] = select(policy_query)
    
    if 'submit' in request.form:
        policy_id = request.form['policy_id']
        policynumber = request.form['policynumber']
        insert_query = "INSERT INTO policyrequest VALUES (null, '%s', '%s', '%s', curdate(), 'pending')" % (policy_id, allotvehicle_id, policynumber)
        insert(insert_query)
        
        import datetime
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # Load contract info as JSON
            contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
        id = web3.eth.get_block_number()
        message = contract.functions.add_policyrequest(int(id),
            int(policy_id),
            int(allotvehicle_id),
            policynumber,
            d,
            'none'
            
        ).transact({"from":web3.eth.accounts[0]})
        
        
        return redirect(url_for('company.company_policy_request', allotvehicle_id=allotvehicle_id))
    
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
    
    return render_template('company_policy_request.html', data=data)

@company.route('/company_request_loan', methods=['get', 'post'])
def company_request_loan():
    data = {}
    allotvehicle_id = request.args['allotvehicle_id']
    # Fetch banks for the dropdown
    bank_query = "SELECT * FROM bank"
    data['banks'] = select(bank_query)
    
    if 'submit' in request.form:
        bank_id = request.form['bank_id']
        details = request.form['details']
        insert_query = "INSERT INTO loanrequest VALUES (null, '%s', '%s', '%s', curdate(), 'pending')" % (allotvehicle_id, bank_id, details)
        insert(insert_query)
        
        import datetime
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # Load contract info as JSON
            contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
        id = web3.eth.get_block_number()
        message = contract.functions.add_loanrequest(int(id),
            int(allotvehicle_id),
            int(bank_id),
            int(bank_id),
            details,
            d,
            'pending'
            
        ).transact({"from":web3.eth.accounts[0]})
        
        
        return redirect(url_for('company.company_request_loan', allotvehicle_id=allotvehicle_id))
    
    # Fetch existing loan requests
    request_query = """
        SELECT 
            loanrequest.loanrequest_id, 
            bank.name AS bank_name, 
            loanrequest.details, 
            loanrequest.date, 
            loanrequest.status 
        FROM 
            loanrequest 
        INNER JOIN 
            bank ON loanrequest.bank_id = bank.bank_id 
        WHERE 
            loanrequest.allotvehicle_id = '%s'
    """ % (allotvehicle_id)
    data['requests'] = select(request_query)
    
    return render_template('company_request_loan.html', data=data)

@company.route('/company_view_payment', methods=['get', 'post'])
def company_view_payment():
    booking_id = request.args['booking_id']
    data = {}
    query = """
        SELECT 
            payment.payment_id, 
            payment.booking_id, 
            payment.amount, 
            payment.date,
            CONCAT(user.fname, ' ', user.lname) AS user_name
        FROM 
            payment 
        INNER JOIN 
            booking ON payment.booking_id = booking.booking_id
        INNER JOIN 
            user ON booking.user_id = user.user_id
        WHERE 
            payment.booking_id = '%s'
    """ % (booking_id)
    data['value'] = select(query)
    return render_template('company_view_payment.html', data=data)





