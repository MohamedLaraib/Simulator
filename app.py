from flask import Flask, request, jsonify, render_template
from Simulator import simulate_queue_preemptive, plot_gantt
import traceback
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_metrics_plotly(df):
    # Extract all critical time points
    times = []
    times.extend(df['Arrival Time'].tolist())
    times.extend(df['Service Start'].tolist())
    times.extend(df['Service End'].tolist())
    
    # Sort and unique
    times = sorted(list(set(times)))
    
    queue_lengths = []
    server_utils = []
    
    final_end_times = df.groupby('Customer')['Service End'].max().to_dict()
    
    for t in times:
        q_len = 0
        t_check = t + 0.000001
        
        active_serves = df[(df['Service Start'] <= t_check) & (df['Service End'] > t_check)]
        s_util = len(active_serves)
        
        active_customers = set(active_serves['Customer'])
        for customer, end_t in final_end_times.items():
            arr_t = df[df['Customer'] == customer]['Arrival Time'].iloc[0]
            if arr_t <= t_check < end_t:
                if customer not in active_customers:
                    q_len += 1
                    
        queue_lengths.append(q_len)
        server_utils.append(s_util)
        
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Queue Length Over Time', 'Server Utilization Over Time'),
        vertical_spacing=0.15
    )
    
    fig.add_trace(
        go.Scatter(
            x=times,
            y=queue_lengths,
            name="Queue Length",
            mode='lines+markers',
            line=dict(color='#a855f7', shape='hv') 
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=times,
            y=server_utils,
            name="Servers Busy",
            mode='lines+markers',
            line=dict(color='#6366f1', shape='hv')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=700,
        title_text="Queue System Metrics",
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    fig.update_yaxes(title_text="Customers in Queue", row=1, col=1, gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)')
    fig.update_yaxes(title_text="Servers Busy", row=2, col=1, gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)')
    fig.update_xaxes(title_text="Time", row=1, col=1, gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)')
    fig.update_xaxes(title_text="Time", row=2, col=1, gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.2)')
    
    return fig.to_json()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        
        num_customers = int(data.get('num_customers', 10))
        num_servers = int(data.get('num_servers', 1))
        
        inter_arrival_dist = data.get('inter_arrival_dist', 'exponential')
        inter_arrival_params = data.get('inter_arrival_params', {})
        
        service_dist = data.get('service_dist', 'exponential')
        service_params = data.get('service_params', {})
        preemptive = data.get('preemptive', True)
        
        # We need to parse inputs dynamically based on the JS frontend sending them
        # Convert all param values to floats
        ia_params = {k: float(v) for k, v in inter_arrival_params.items()}
        s_params = {k: float(v) for k, v in service_params.items()}

        df = simulate_queue_preemptive(
            inter_arrival_dist, 
            service_dist, 
            ia_params, 
            s_params, 
            num_servers, 
            num_customers,
            preemptive=preemptive
        )
        
        gantt_b64 = plot_gantt(df, as_base64=True)
        metrics_json = generate_metrics_plotly(df)
        
        # Convert df to dictionary format suitable for JSON
        df_records = df.to_dict(orient='records')
        
        return jsonify({
            'status': 'success',
            'data': df_records,
            'gantt_chart': gantt_b64,
            'metrics_json': metrics_json
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
