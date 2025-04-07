from flask import *
from database import *  
from blk import *

mvd = Blueprint("mvd", __name__)

@mvd.route('/mvd_home')
def mvd_home():
    return render_template('mvd_home.html')

@mvd.route('/mvd_view_register_request', methods=['get', 'post'])
def mvd_view_register_request():
    data = {}
    query = """
        SELECT 
            registerrequest.registerrequest_id,
            registerrequest.allotvehicle_id, 
            allotvehicle.*,
            registerrequest.date, 
            registerrequest.status, 
            CONCAT(user.fname, ' ', user.lname) AS user_name,
            user.*, 
            vehicle.vehicles AS vehicle_name 
        FROM 
            registerrequest 
        INNER JOIN 
            allotvehicle ON registerrequest.allotvehicle_id = allotvehicle.allotvehicle_id 
        INNER JOIN 
            booking ON allotvehicle.booking_id = booking.booking_id 
        INNER JOIN 
            user ON booking.user_id = user.user_id 
        INNER JOIN 
            vehicle ON booking.vehicle_id = vehicle.vehicle_id 
        WHERE 
            registerrequest.mvd_id = '%s'
    """ % (session['mid'])
    data['value'] = select(query)
    
    if 'action' in request.form:
        action = request.form['action']
        registerrequest_id = request.form['registerrequest_id']
        qq="select * from registerrequest WHERE registerrequest_id='%s'" % (registerrequest_id)
        res1=select(qq)
        if action == 'accept':
            update_query = "UPDATE registerrequest SET status='accepted' WHERE registerrequest_id='%s'" % (registerrequest_id)
            update(update_query)
            import datetime
            d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(compiled_contract_path) as file:
                contract_json = json.load(file)  # Load contract info as JSON
                contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
            contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
            
            id = web3.eth.get_block_number()
            message = contract.functions.add_registerrequest(int(id),
                int(res1[0]['mvd_id']),
                int(res1[0]['allotvehicle_id']),
                d,
                'accepted'
                
            ).transact({"from":web3.eth.accounts[0]})
        elif action == 'reject':
            update_query = "UPDATE registerrequest SET status='rejected' WHERE registerrequest_id='%s'" % (registerrequest_id)
            update(update_query)
            import datetime
            d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(compiled_contract_path) as file:
                contract_json = json.load(file)  # Load contract info as JSON
                contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
            contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
            
            id = web3.eth.get_block_number()
            message = contract.functions.add_registerrequest(int(id),
                int(res1[0]['mvd_id']),
                int(res1[0]['allotvehicle_id']),
                d,
                'rejected'
                
            ).transact({"from":web3.eth.accounts[0]})
        
        
        
        
        
        return redirect(url_for('mvd.mvd_view_register_request'))
    
    return render_template('mvd_view_register_request.html', data=data)








@mvd.route('/mvd_set_number', methods=['get', 'post'])
def mvd_set_number():
    
    aid=request.args['aid']

    if 'allot' in request.form:

        regusternumber = request.form['regusternumber']
        
        update_query = "UPDATE allotvehicle SET regusternumber='%s' WHERE allotvehicle_id='%s'" % (regusternumber,aid)
        update(update_query)
        mk="UPDATE registerrequest SET status='registered' WHERE allotvehicle_id='%s'" % (aid)
        update(mk)
      
        return redirect(url_for('mvd.mvd_view_register_request'))
    
    return render_template('mvd_set_number.html')



@mvd.route('/mvd_view_user', methods=['get', 'post'])
def mvd_view_user():
    data = {}
    
    uid=request.args['uid']
    s = """
        SELECT *, CONCAT(`fname`, ' ', `lname`) AS `name`
        FROM `user`
        INNER JOIN `login` USING (`login_id`) where user_id='%s'
    """%(uid)
    data['value'] = select(s)
    
  
    
    return render_template('mvd_view_user.html', data=data)