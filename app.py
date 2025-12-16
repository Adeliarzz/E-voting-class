import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3
from dotenv import load_dotenv

# Load Env
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'supersecretkey'  # Change for production

# --- CONFIGURATION ---
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Blockchain
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:7545")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Admin Private Key (MUST BE SET IN .ENV)
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")
if not ADMIN_PRIVATE_KEY:
    print("WARNING: ADMIN_PRIVATE_KEY not set in .env")

# Context Processor to make 'user' available in layout.html
@app.context_processor
def inject_user():
    context = {
        'ganache_connected': web3.is_connected(),
        'user': None
    }
    
    if 'user_id' in session and session['user_id'] != 'ADMIN':
        context['user'] = User.query.get(session['user_id'])
        
    return context

# Load Contract
def load_contract():
    try:
        with open('build/contracts/Evoting.json') as f:
            artifact = json.load(f)
        net_id = str(web3.net.version)
        if net_id in artifact['networks']:
            address = artifact['networks'][net_id]['address']
            abi = artifact['abi']
            return web3.eth.contract(address=address, abi=abi)
        else:
            print("Current network ID not found in artifact.")
            return None
    except FileNotFoundError:
        print("Contract artifact not found. Compile/Deploy first.")
        return None

contract = load_contract()

# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.String(20), primary_key=True) # NIM
    name = db.Column(db.String(100), nullable=False)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)
    private_key = db.Column(db.String(100), nullable=False) # Storing PK for UX (Security Trade-off)
    password = db.Column(db.String(100), nullable=False)
    has_voted = db.Column(db.Boolean, default=False)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)      # Calon Ketua
    vice_name = db.Column(db.String(100), nullable=True)  # Calon Wakil (Optional)
    description = db.Column(db.String(200))               # Short Tagline
    vision = db.Column(db.Text, nullable=True)            # Visi
    mission = db.Column(db.Text, nullable=True)           # Misi
    image_file = db.Column(db.String(100), nullable=True, default='default.jpg') # Foto Ketua
    image_vice = db.Column(db.String(100), nullable=True, default='default.jpg') # Foto Wakil

# --- ROUTES ---

@app.route('/')
def index():
    # Public Access: Fetch candidates regardless of login status
    candidates_db = Candidate.query.all()
    
    user = None
    if 'user_id' in session:
        if session['user_id'] == 'ADMIN':
            # Create a dummy user object for Admin on frontend
            class AdminUser:
                id = 'ADMIN'
                name = 'Administrator'
                has_voted = False
            user = AdminUser()
        else:
            user = User.query.get(session['user_id'])
        
    return render_template('index.html', candidates=candidates_db, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Fetch Ganache Accounts
    all_accounts = web3.eth.accounts
    
    # Fetch Used Accounts from DB
    used_wallets = [u.wallet_address for u in User.query.all()]
    
    # Filter Available
    available_wallets = [acc for acc in all_accounts if acc not in used_wallets]

    if request.method == 'POST':
        name = request.form['name']
        user_id = request.form['user_id']
        wallet_address = request.form['wallet_address']
        private_key = request.form['private_key']
        password = request.form['password']
        
        if User.query.get(user_id):
            flash("User ID (NIM) already exists! Please login.", "error")
            return redirect(url_for('register'))
            
        if User.query.filter_by(wallet_address=wallet_address).first():
            flash("Wallet Address already registered!", "error")
            return redirect(url_for('register'))
            
        new_user = User(
            id=user_id, 
            name=name, 
            wallet_address=wallet_address,
            private_key=private_key,
            password=password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration Successful! Please Login.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html', wallets=available_wallets)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        # Hardcoded Admin Check
        if user_id == 'admin@evoting.com' and password == 'admin123':
            session['user_id'] = 'ADMIN'
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        
        user = User.query.get(user_id)
        if user and user.password == password:
            session['user_id'] = user.id
            session['is_admin'] = False
            flash("Welcome back!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid ID or Password. Please try again.", "error")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/vote', methods=['POST'])
def vote():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    candidate_id = int(request.json['candidate_id'])
    
    user = User.query.get(user_id)
    
    if user.has_voted:
        return jsonify({'error': 'You have already voted (DB Check)'}), 400

    # Blockchain Transaction
    if not contract:
        return jsonify({'error': 'Contract not loaded'}), 500

    try:
        # Prepare Transaction
        admin_account = web3.eth.account.from_key(ADMIN_PRIVATE_KEY)
        nonce = web3.eth.get_transaction_count(admin_account.address)
        chain_id = web3.eth.chain_id
        
        # Call vote(voter_address, candidate_id)
        # Note: In Solidity we used 'vote(address _voter, uint _candidateId)'
        tx = contract.functions.vote(user.wallet_address, candidate_id).build_transaction({
            'chainId': chain_id,
            'gas': 2000000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })
        
        # Sign & Send
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=ADMIN_PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Update DB
        user.has_voted = True
        db.session.commit()
        
        return jsonify({'success': True, 'tx_hash': web3.to_hex(tx_hash)})
        
    except Exception as e:
        print(f"Error voting: {e}")
        # Simplistic error handling
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin_dashboard():
    # Protect this route
    if session.get('user_id') != 'ADMIN':
        return redirect(url_for('login'))
        
    # 1. Fetch Registered Users Count
    total_users = User.query.count()
    
    # 2. Fetch Live Blockchain Data (Just stats)
    total_votes = 0
    try:
        count = contract.functions.candidatesCount().call()
        for i in range(1, count + 1):
            c = contract.functions.getCandidate(i).call()
            total_votes += c[2]
            
    except Exception as e:
        print(f"Error fetching admin stats: {e}")
        
    return render_template('admin.html', 
                         total_users=total_users, 
                         total_votes=total_votes,
                         active_page='dashboard')

@app.route('/admin/users')
def admin_users():
    if session.get('user_id') != 'ADMIN':
        return redirect(url_for('login'))
        
    all_users = User.query.all()
    return render_template('admin_users.html', users=all_users, active_page='users')

@app.route('/admin/delete_user/<id>', methods=['POST'])
def delete_user(id):
    if session.get('user_id') != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 401
        
    user = User.query.get(id)
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'User not found'}), 404

@app.route('/admin/candidates')
def admin_candidates():
    if session.get('user_id') != 'ADMIN':
        return redirect(url_for('login'))
        
    candidates_data = []
    try:
        count = contract.functions.candidatesCount().call()
        for i in range(1, count + 1):
            c = contract.functions.getCandidate(i).call()
            # Solidity: (id, name, voteCount)
            # Fetch extra details from DB
            db_cand = Candidate.query.get(c[0])
            
            # ONLY show candidates that exist in the Database (Active)
            if db_cand:
                candidates_data.append({
                    'id': c[0],
                    'name': c[1],
                    'voteCount': c[2],
                    'vice_name': db_cand.vice_name,
                    'image_file': db_cand.image_file,
                    'image_vice': db_cand.image_vice,
                    'description': db_cand.description
                })
    except Exception as e:
        print(f"Error fetching candidates: {e}")

    return render_template('admin_candidates.html', candidates=candidates_data, active_page='candidates')

from werkzeug.utils import secure_filename

@app.route('/admin/add-candidate-page')
def admin_add_candidate_page():
    if session.get('user_id') != 'ADMIN':
        return redirect(url_for('login'))
    return render_template('admin_add_candidate.html', active_page='candidates')

@app.route('/admin/add', methods=['POST'])
def add_candidate():
    if session.get('user_id') != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 401
    
    name = request.form['name']
    vice_name = request.form.get('vice_name', '')
    description = request.form['description']
    vision = request.form.get('vision', '')
    mission = request.form.get('mission', '')
    
    # Image Upload (Ketua)
    image_file = 'default.jpg'
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_file = filename
            
    # Image Upload (Wakil)
    image_vice = 'default.jpg'
    if 'image_vice' in request.files:
        file = request.files['image_vice']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_vice = filename
    
    # 1. Add to Blockchain (Only Name is stored on-chain for simplicity & gas cost)
    try:
        admin_account = web3.eth.account.from_key(ADMIN_PRIVATE_KEY)
        nonce = web3.eth.get_transaction_count(admin_account.address)
        chain_id = web3.eth.chain_id
        
        tx = contract.functions.addCandidate(name).build_transaction({
            'chainId': chain_id,
            'gas': 2000000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })
        
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=ADMIN_PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # 2. Add to Database
        count = contract.functions.candidatesCount().call()
        
        new_candidate = Candidate(
            id=count, 
            name=name, 
            vice_name=vice_name,
            description=description,
            vision=vision,
            mission=mission,
            image_file=image_file,
            image_vice=image_vice
        )
        db.session.add(new_candidate)
        db.session.commit()
        
        return jsonify({'success': True, 'id': count})
        
    except Exception as e:
        print("Error adding candidate:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete_candidate/<int:candidate_id>', methods=['POST'])
def delete_candidate(candidate_id):
    if session.get('user_id') != 'ADMIN':
        return redirect(url_for('login'))
    
    candidate = Candidate.query.get(candidate_id)
    if candidate:
        # Optional: Delete image file to save space
        try:
            if candidate.image_file != 'default.jpg':
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], candidate.image_file))
        except:
            pass
            
        db.session.delete(candidate)
        db.session.commit()
        flash('Candidate deleted from database successfully!', 'success')
    else:
        flash('Candidate not found', 'error')
        
    return redirect(url_for('admin_candidates'))

@app.route('/results')
def results():
    if not contract:
        return "Contract not loaded"
    
    try:
        candidates_data = []
        count = contract.functions.candidatesCount().call()
        
        for i in range(1, count + 1):
            c = contract.functions.getCandidate(i).call()
            # Check DB existence (Active check)
            db_cand = Candidate.query.get(c[0])
            if db_cand:
                # Solidity Return: (id, name, voteCount)
                candidates_data.append({
                    'id': c[0],
                    'name': c[1],
                    'voteCount': c[2],
                    'vice_name': db_cand.vice_name
                })
            
        return render_template('results.html', candidates=candidates_data)
    except Exception as e:
        return f"Error fetching results from blockchain: {e}"

@app.route('/ledger')
def ledger():
    if not contract:
        return "Contract not loaded."
        
    try:
        # Fetch All Vote Events
        events = contract.events.VoteCast.create_filter(fromBlock=0).get_all_entries()
        
        ledger_data = []
        import datetime
        
        for e in events:
            tx_hash = web3.to_hex(e['transactionHash'])
            block_num = e['blockNumber']
            
            # 1. Get Block (for Timestamp)
            block = web3.eth.get_block(block_num)
            timestamp = block['timestamp']
            time_obj = datetime.datetime.fromtimestamp(timestamp)
            time_str = time_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate Age (e.g., "5 mins ago")
            now = datetime.datetime.now()
            diff = now - time_obj
            if diff.days > 0:
                age = f"{diff.days} days ago"
            elif diff.seconds > 3600:
                age = f"{diff.seconds // 3600} hrs ago"
            elif diff.seconds > 60:
                age = f"{diff.seconds // 60} mins ago"
            else:
                age = "Just now"
            
            # 2. Get Transaction (for Gas Price)
            tx = web3.eth.get_transaction(e['transactionHash'])
            gas_price = tx['gasPrice'] # in Wei
            
            # 3. Get Receipt (for Gas Used)
            receipt = web3.eth.get_transaction_receipt(e['transactionHash'])
            gas_used = receipt['gasUsed']
            
            # 4. Calculate Fee
            fee_wei = gas_used * gas_price
            fee_eth = web3.from_wei(fee_wei, 'ether')
            # Format to 6 decimals
            fee_fmt = "{:.6f}".format(float(fee_eth))

            # Candidate Name
            c_id = e['args']['candidateId']
            # Try to get simplified name from DB if possible, else generic
            cand_name = "Unknown"
            db_cand = Candidate.query.get(c_id)
            if db_cand:
                cand_name = db_cand.name
            
            ledger_data.append({
                'tx_hash': tx_hash,
                'block_num': block_num,
                'age': age,
                'timestamp': time_str,
                'from': e['args']['voter'],
                'to': contract.address,
                'value': '0 ETH', # Voting usually sends 0 ETH
                'fee': fee_fmt,
                'gas_used': gas_used,
                'candidate': cand_name
            })
            
        # --- NEW: FETCH ALL BLOCKS (0 to Latest) ---
        latest_block = web3.eth.block_number
        blocks_data = []
        
        # Loop backwards from latest to 0
        for i in range(latest_block, -1, -1):
            blk = web3.eth.get_block(i)
            
            # Timestamp & Age
            b_time = datetime.datetime.fromtimestamp(blk['timestamp'])
            b_diff = datetime.datetime.now() - b_time
            
            if b_diff.days > 0:
                b_age = f"{b_diff.days} days ago"
            elif b_diff.seconds > 3600:
                b_age = f"{b_diff.seconds // 3600} hrs ago"
            elif b_diff.seconds > 60:
                b_age = f"{b_diff.seconds // 60} mins ago"
            else:
                b_age = "Just now"
                
            blocks_data.append({
                'number': blk['number'],
                'hash': web3.to_hex(blk['hash']),
                'miner': blk['miner'],
                'tx_count': len(blk['transactions']),
                'gas_used': blk['gasUsed'],
                'gas_limit': blk['gasLimit'],
                'age': b_age,
                'timestamp': b_time.strftime('%Y-%m-%d %H:%M:%S')
            })

        return render_template('ledger.html', votes=ledger_data, blocks=blocks_data)
        
    except Exception as e:
        print(f"Error fetching ledger: {e}")
        return f"Error loading ledger: {e}"

# Init DB for Demo
def init_db():
    with app.app_context():
        db.create_all()
        # Demo Data
        # Demo Data Logic - Sync DB with Blockchain
        try:
            # Check Blockchain Count
            chain_count = contract.functions.candidatesCount().call()
            
            # If Blockchain is empty (was reset), but we want demo data:
            if chain_count == 0:
                print(">>> Seeding Blockchain with Demo Candidates...")
                admin_account = web3.eth.account.from_key(ADMIN_PRIVATE_KEY)
                
                demos = [
                    {"name": "Alice", "desc": "Visionary Leader"},
                    {"name": "Bob", "desc": "Practical Solver"}
                ]
                
                for d in demos:
                    # Add to Chain
                    nonce = web3.eth.get_transaction_count(admin_account.address)
                    chain_id = web3.eth.chain_id
                    tx = contract.functions.addCandidate(d['name']).build_transaction({
                        'chainId': chain_id,
                        'gas': 2000000,
                        'gasPrice': web3.to_wei('20', 'gwei'),
                        'nonce': nonce,
                    })
                    signed = web3.eth.account.sign_transaction(tx, private_key=ADMIN_PRIVATE_KEY)
                    web3.eth.send_raw_transaction(signed.raw_transaction)
                    # We rely on sequential execution here roughly, or we could wait for receipt.
                    print(f"   Added {d['name']} to Chain.")
                    
                # Re-check count or just assume 1, 2...
                # Clear DB to ensure sync
                Candidate.query.delete()
                
                # Add to DB
                db.session.add(Candidate(id=1, name="Alice", description="Visionary Leader"))
                db.session.add(Candidate(id=2, name="Bob", description="Practical Solver"))
                
                # Also reset users voting status if chain was reset
                User.query.update({User.has_voted: False})
                
                db.session.commit()
                print(">>> Database Synced with Blockchain.")

        except Exception as e:
            print(f">>> Warning: Could not seed blockchain: {e}")

        # Ensure User exists
        if not User.query.first():
            u1 = User(
                id="101", 
                name="John Doe", 
                wallet_address="0x0000000000000000000000000000000000000001", 
                private_key="0x0000000000000000000000000000000000000001", 
                password="password"
            ) 
            db.session.add(u1)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
