from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('trading_journal.db')
    c = conn.cursor()
    # Drop existing table if it exists
    c.execute('DROP TABLE IF EXISTS trades')
    # Create new table with updated schema
    c.execute('''
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            market TEXT NOT NULL,
            setup TEXT,
            entry_price REAL NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            exit_price REAL,
            position_size REAL NOT NULL,
            risk_reward REAL,
            pnl_points REAL,
            pnl_amount REAL,
            trade_duration TEXT,
            trade_type TEXT NOT NULL,  -- LONG or SHORT
            status TEXT NOT NULL,      -- OPEN or CLOSED
            execution_quality INTEGER,  -- 1-5 rating
            trade_management INTEGER,   -- 1-5 rating
            psychology INTEGER,         -- 1-5 rating
            notes TEXT,
            mistakes TEXT,
            lessons_learned TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_db():
    conn = sqlite3.connect('trading_journal.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/trades', methods=['GET', 'POST'])
def handle_trades():
    if request.method == 'POST':
        data = request.json
        conn = get_db()
        c = conn.cursor()
        
        # Calculate risk/reward if stop loss and take profit are provided
        risk_reward = None
        if data.get('stop_loss') and data.get('take_profit'):
            if data['trade_type'] == 'LONG':
                risk = float(data['entry_price']) - float(data['stop_loss'])
                reward = float(data['take_profit']) - float(data['entry_price'])
            else:
                risk = float(data['stop_loss']) - float(data['entry_price'])
                reward = float(data['entry_price']) - float(data['take_profit'])
            if risk != 0:
                risk_reward = reward / risk
        
        c.execute('''
            INSERT INTO trades (
                date, market, setup, entry_price, stop_loss, take_profit,
                position_size, risk_reward, trade_type, status,
                execution_quality, trade_management, psychology,
                notes, mistakes, lessons_learned
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            data['market'],
            data.get('setup', ''),
            float(data['entry_price']),
            float(data.get('stop_loss', 0)) or None,
            float(data.get('take_profit', 0)) or None,
            float(data['position_size']),
            risk_reward,
            data['trade_type'],
            'OPEN',
            int(data.get('execution_quality', 0)) or None,
            int(data.get('trade_management', 0)) or None,
            int(data.get('psychology', 0)) or None,
            data.get('notes', ''),
            data.get('mistakes', ''),
            data.get('lessons_learned', '')
        ))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Trade added successfully'})
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM trades ORDER BY date DESC')
    trades = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(trades)

@app.route('/api/trades/<int:trade_id>/close', methods=['POST'])
def close_trade(trade_id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    # Get the trade details
    c.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
    trade = dict(c.fetchone())
    
    exit_price = float(data['exit_price'])
    
    # Calculate P/L in points
    if trade['trade_type'] == 'LONG':
        pnl_points = exit_price - trade['entry_price']
    else:
        pnl_points = trade['entry_price'] - exit_price
    
    # Calculate P/L amount
    pnl_amount = pnl_points * trade['position_size']
    
    # Calculate trade duration
    start_date = datetime.fromisoformat(trade['date'])
    end_date = datetime.now()
    duration = end_date - start_date
    
    # Update the trade
    c.execute('''
        UPDATE trades 
        SET exit_price = ?, 
            pnl_points = ?,
            pnl_amount = ?,
            trade_duration = ?,
            status = ?,
            execution_quality = ?,
            trade_management = ?,
            psychology = ?,
            mistakes = ?,
            lessons_learned = ?
        WHERE id = ?
    ''', (
        exit_price,
        pnl_points,
        pnl_amount,
        str(duration),
        'CLOSED',
        int(data.get('execution_quality', 0)) or None,
        int(data.get('trade_management', 0)) or None,
        int(data.get('psychology', 0)) or None,
        data.get('mistakes', ''),
        data.get('lessons_learned', ''),
        trade_id
    ))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Trade closed successfully'})

@app.route('/api/stats')
def get_stats():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM trades WHERE status = ?', ('CLOSED',))
    trades = [dict(row) for row in c.fetchall()]
    
    if not trades:
        return jsonify({
            'total_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'average_pnl': 0,
            'average_risk_reward': 0,
            'average_execution': 0,
            'average_management': 0,
            'average_psychology': 0
        })
    
    winning_trades = sum(1 for t in trades if t['pnl_amount'] > 0)
    total_pnl = sum(t['pnl_amount'] for t in trades)
    
    # Calculate averages for ratings
    valid_execution = [t['execution_quality'] for t in trades if t['execution_quality']]
    valid_management = [t['trade_management'] for t in trades if t['trade_management']]
    valid_psychology = [t['psychology'] for t in trades if t['psychology']]
    valid_risk_reward = [t['risk_reward'] for t in trades if t['risk_reward']]
    
    stats = {
        'total_trades': len(trades),
        'win_rate': (winning_trades / len(trades)) * 100,
        'total_pnl': total_pnl,
        'average_pnl': total_pnl / len(trades),
        'average_risk_reward': sum(valid_risk_reward) / len(valid_risk_reward) if valid_risk_reward else 0,
        'average_execution': sum(valid_execution) / len(valid_execution) if valid_execution else 0,
        'average_management': sum(valid_management) / len(valid_management) if valid_management else 0,
        'average_psychology': sum(valid_psychology) / len(valid_psychology) if valid_psychology else 0
    }
    
    conn.close()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
