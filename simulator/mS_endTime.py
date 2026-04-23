import math
import random
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from decimal import *
from statistics import mean
from texttable import Texttable
from rich.console import Console
import matplotlib.pyplot as plt
from rich.table import Table
from rich.panel import Panel
from rich import box
import pandas as pd
import plotly.express as px

# Initialize the console
console = Console()

class Server:
    # Server implementation remains the same
    def __init__(self, server_id):
        self.server_id = server_id
        self.current_customer = None
        self.end_time = 0
    
class customer:
    # Customer class implementation remains the same
    
    def __init__(self, customer_id, arrival_time, burst_time, priority, interarrival):
        self.customer_id = customer_id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.time_left = burst_time
        self.server_id = None
        self.is_ready = False
        self.start_time = 0
        self.end_time = 0
        self.completion_time = 0
        self.turn_around_time = 0
        self.interarrival = interarrival
        self.wait_time = 0
        self.response_time = 0
        self.utilization_time = 0
        self.response_ratio = 0
        self.start_times = []
        self.end_times = []

    def decrement_time_left(self):
        self.time_left -= 1

    def set_start_time(self, time_passed):
        self.start_time = time_passed

    def set_end_time(self, time_passed):
        self.end_time = time_passed

    def set_completion_time(self, time_passed):
        self.completion_time = time_passed

    def set_turn_around_time(self):
        self.turn_around_time = self.completion_time - self.arrival_time

    def set_wait_time(self):
        self.wait_time = self.turn_around_time - self.burst_time

    def set_response_time(self, time_passed):
        self.response_time = time_passed - self.arrival_time

    def set_utilization_time(self):
        self.utilization_time = self.burst_time / self.turn_around_time

    def append_start_times(self, time_passed):
        self.start_times.append(time_passed)

    def append_end_times(self, time_passed):
        self.end_times.append(time_passed)

    def set_response_ratio(self, time_passed):
        self.response_ratio = (
            (time_passed - self.arrival_time) + self.burst_time) / self.burst_time
        
class QueueMetricsCollector:
    def __init__(self):
        self.queue_lengths = []
        self.server_utilizations = []
        self.wait_times = []
        self.response_times = []
        self.current_time = 0
        self.customers_served = 0
        
    def collect_metrics(self, ready_queue, active_servers, time_passed, all_customers):
        # Record queue length (customers who have arrived but haven't finished)
        unfinished_customers = ready_queue
        waiting_customers = [c for c in unfinished_customers if c not in [s.current_customer for s in active_servers if s.current_customer]]
        self.queue_lengths.append({
            'time': time_passed,
            'length': len(waiting_customers)
        })
        
        # Record server utilization
        busy_servers = len(active_servers)
        utilization = busy_servers
        
        self.server_utilizations.append({
            'time': time_passed,
            'utilization': utilization
        })


    def plot_metrics(self):
        import time
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Queue Length Over Time', 'Server Utilization Over Time'),
            vertical_spacing=0.15
        )
        
        # Queue length plot
        fig.add_trace(
            go.Scatter(
                x=[d['time'] for d in self.queue_lengths],
                y=[d['length'] for d in self.queue_lengths],
                name="Queue Length",
                mode='lines+markers',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # Server utilization plot
        fig.add_trace(
            go.Scatter(
                x=[d['time'] for d in self.server_utilizations],
                y=[d['utilization'] for d in self.server_utilizations],
                name="Servers Busy",
                mode='lines+markers',
                line=dict(color='green')
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="Queue System Metrics",
            showlegend=True
        )
        
        # Update y-axes labels
        fig.update_yaxes(title_text="Customers in Queue", row=1, col=1)
        fig.update_yaxes(title_text="Servers Busy", row=2, col=1)
        
        # Update x-axes labels
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        
        fig.show()
        time.sleep(1)  # Add delay to prevent race conditions

    def increment_customers_served(self):
        self.customers_served += 1
    
    def get_visualization_data(self):
        """Returns collected metrics in a format suitable for visualization"""
        return {
            'queue_lengths': self.queue_lengths,
            'server_utilizations': self.server_utilizations,
            'customers_served': self.customers_served,
            'total_time': self.current_time
        }

def check_should_service_proceed(customer_list):
    # Unchanged
    for customer in customer_list:
        if customer.time_left > 0:
            return True
    return False
    
def sort_customers_according_to_shortest_arrival(customer_list):
    # Unchanged
    return sorted(customer_list, key=lambda customer: customer.arrival_time, reverse=False)

def sort_customers_according_to_highest_priority(customer_list):
    # Unchanged
    return sorted(customer_list, key=lambda customer: customer.priority, reverse=False)

def get_customers_of_same_highest_priority(customer_list, maximum_priority):
    customers_of_same_highest_priority = []
    for customer in customer_list:
        if customer.priority == maximum_priority:
            customers_of_same_highest_priority.append(customer)
    return customers_of_same_highest_priority

# Modify the get_distribution_parameters function to include empirical distribution
def get_distribution_parameters(distribution_type, rate_type="arrival"):
    console.print((f"Enter parameters for {rate_type} rate distribution:"), style = 'red', justify = 'center')
    
    if distribution_type == 1:  # Exponential
        param = float(input("Enter the mean (lambda) for Exponential distribution: "))
        return param
    
    elif distribution_type == 2:  # Normal
        mean = float(input("Enter the mean for Normal distribution: "))
        stddev = float(input("Enter the standard deviation for Normal distribution: "))
        return mean, stddev
    
    elif distribution_type == 3:  # Gamma
        shape = float(input("Enter the shape parameter for Gamma distribution: "))
        scale = float(input("Enter the scale parameter for Gamma distribution: "))
        return shape, scale
    
    elif distribution_type == 4:  # Uniform
        min_value = float(input("Enter the minimum value for Uniform distribution: "))
        max_value = float(input("Enter the maximum value for Uniform distribution: "))
        return min_value, max_value

def getArrivalTimes(distribution_choice, end_time):
    interArrivals = []  # Changed to empty list since we'll append the first interarrival
    arrivalTimes = [0]  # Keep first arrival at 0
    current_time = 0

    if distribution_choice == 1:  # Exponential
        meanArrivalNumber = get_distribution_parameters(distribution_choice)
        while True:
            interArrival = math.ceil(-meanArrivalNumber * math.log(random.random()))
            if current_time + interArrival > end_time:
                break
            interArrivals.append(interArrival)
            current_time += interArrival
            arrivalTimes.append(current_time)

    elif distribution_choice == 2:  # Normal
        mean, stddev = get_distribution_parameters(distribution_choice)
        while True:
            while True:
                time = random.normalvariate(mean, stddev)
                if time > 0:
                    time = math.ceil(time)
                    break
            if current_time + time > end_time:
                break
            interArrivals.append(time)
            current_time += time
            arrivalTimes.append(current_time)

    elif distribution_choice == 3:  # Gamma
        shape, scale = get_distribution_parameters(distribution_choice)
        while True:
            time = math.ceil(random.gammavariate(shape, scale))
            if current_time + time > end_time:
                break
            interArrivals.append(time)
            current_time += time
            arrivalTimes.append(current_time)

    elif distribution_choice == 4:  # Uniform
        min_value, max_value = get_distribution_parameters(distribution_choice)
        while True:
            time = math.ceil(random.uniform(min_value, max_value))
            if current_time + time > end_time:
                break
            interArrivals.append(time)
            current_time += time
            arrivalTimes.append(current_time)

    # Insert 0 at the beginning of interArrivals for the first customer
    interArrivals.insert(0, 0)
    return {
        "interArrivals": interArrivals,
        "arrivalTimes": arrivalTimes
    }

def getServiceTimes(length, distribution_choice):
    serviceTimes = []
    if distribution_choice == 1:  # Exponential
        meanServiceNumber = get_distribution_parameters(distribution_choice, "service")
        for i in range(length):
            serviceTime = -meanServiceNumber * math.log(random.random())
            serviceTimes.append(math.ceil(serviceTime))

    elif distribution_choice == 2:  # Normal
        mean, stddev = get_distribution_parameters(distribution_choice, rate_type="service")
        for i in range(length):
            while True:
                serviceTime = random.normalvariate(mean, stddev)
                if serviceTime > 0:
                    serviceTimes.append(math.ceil(serviceTime))
                    break

    elif distribution_choice == 3:  # Gamma
        shape, scale = get_distribution_parameters(distribution_choice, rate_type="service")
        for i in range(length):
            serviceTime = random.gammavariate(shape, scale)
            serviceTimes.append(math.ceil(serviceTime))

    elif distribution_choice == 4:  # Uniform
        min_value, max_value = get_distribution_parameters(distribution_choice, rate_type="service")
        for i in range(length):
            serviceTime = random.uniform(min_value, max_value)
            serviceTimes.append(math.ceil(serviceTime))

    return serviceTimes

def serve_with_metrics(customers, num_servers, scheduling_type):
    metrics_collector = QueueMetricsCollector()
    servers = [Server(server_id=i) for i in range(num_servers)]
    time_passed = 0
    
    while check_should_service_proceed(customers):
        ready_queue = [p for p in customers if p.arrival_time <= time_passed and p.time_left > 0]
        
        # Collect metrics for this time step
        metrics_collector.collect_metrics(ready_queue, servers, time_passed, customers)
        
        # Your existing scheduling logic here
        if scheduling_type == "2":  # FCFS
            ready_queue.sort(key=lambda p: p.arrival_time)
        elif scheduling_type == "1":  # Priority
            ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
        
        # Process servers and customers
        for server in servers:
            if server.current_customer is None and ready_queue:
                assigned_customers = [s.current_customer for s in servers if s.current_customer is not None]
                next_customer = None
                for customer in ready_queue:
                    if customer not in assigned_customers:
                        next_customer = customer
                        break
                
                if next_customer:
                    server.current_customer = next_customer
                    next_customer.server_id = server.server_id
                    ready_queue.remove(next_customer)
                    if not server.current_customer.is_ready:
                        server.current_customer.set_response_time(time_passed)
                        server.current_customer.set_start_time(time_passed)
                        server.current_customer.is_ready = True
                    server.current_customer.append_start_times(time_passed)
            
            if server.current_customer and server.current_customer.time_left == 0:
                metrics_collector.increment_customers_served()
                server.current_customer.set_end_time(time_passed)
                server.current_customer.set_completion_time(time_passed)
                server.current_customer.set_turn_around_time()
                server.current_customer.set_wait_time()
                server.current_customer.append_end_times(time_passed)
                server.current_customer = None
        
        time_passed += 1
    
    metrics_collector.current_time = time_passed
    return metrics_collector.get_visualization_data()

def display(arrivalTimes, serviceTimes, priorities, simulation_type):
    """Displays customer details in a rich table."""
    simulation_type = int(simulation_type)
    if simulation_type == 1:
        table = Table(title="Customer Details", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("S. No.", style="cyan", justify="center")
        table.add_column("Inter Arrivals", justify="center")
        table.add_column("Arrival Times", justify="center")
        table.add_column("Service Times", justify="center")
        table.add_column("Priorities", justify="center")

        min_length = min(
            len(arrivalTimes["interArrivals"]),
            len(arrivalTimes["arrivalTimes"]),
            len(serviceTimes),
            len(priorities),
        )

        for i in range(min_length):
            table.add_row(
                str(i + 1),
                str(arrivalTimes["interArrivals"][i]),
                str(arrivalTimes["arrivalTimes"][i]),
                str(serviceTimes[i]),
                str(priorities[i]),
            )

        console.print(table, justify='center')
    else: 
        table = Table(title="Customer Details", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("S. No.", style="cyan", justify="center")
        table.add_column("Inter Arrivals", justify="center")
        table.add_column("Arrival Times", justify="center")
        table.add_column("Service Times", justify="center")

        min_length = min(
            len(arrivalTimes["interArrivals"]),
            len(arrivalTimes["arrivalTimes"]),
            len(serviceTimes),
        )

        for i in range(min_length):
            table.add_row(
                str(i + 1),
                str(arrivalTimes["interArrivals"][i]),
                str(arrivalTimes["arrivalTimes"][i]),
                str(serviceTimes[i]),
            )

        console.print(table, justify='center')

def getPriorities(length):
    priorities = []
    A = random.randint(50, 100)
    M = 1994
    Z = 10112166
    C = 9
    a = 1
    b = 3
    for i in range(length):
        R = (A * Z + C) % M
        S = R / M
        Y = round((b - a) * S + a)
        priorities.append(Y)
        Z = R
    return priorities

def plot_distributions(arrival_times, service_times):
    import time
    # Create DataFrame for arrival times
    df_arrivals = pd.DataFrame({
        'Inter-arrival Time': arrival_times,
        'Customer ID': range(len(arrival_times))
    })
    
    # Create DataFrame for service times
    df_service = pd.DataFrame({
        'Service Time': service_times,
        'Customer ID': range(len(service_times))
    })
    
    # Create histogram for arrival times
    fig_arrivals = px.histogram(
        df_arrivals, 
        x='Inter-arrival Time',
        color='Customer ID',  # Use Customer ID for coloring
        title='Frequency of Distribution of Inter-arrival Times',
        labels={'Inter-arrival Time': 'Inter-arrival Time'},
        nbins=20
    )
    fig_arrivals.update_layout(
        title_x=0.5,
        bargap=0.1,
        showlegend=False  # Hide the legend as it's not meaningful in this context
    )
    fig_arrivals.show()
    time.sleep(1)  # Add delay between graphs

    # Create histogram for service times
    fig_service = px.histogram(
        df_service,
        x='Service Time',
        color='Customer ID',  # Use Customer ID for coloring
        title='Frequency of Distribution of Service Times',
        labels={'Service Time': 'Service Time'},
        nbins=20
    )
    fig_service.update_layout(
        title_x=0.5,
        bargap=0.1,
        showlegend=False  # Hide the legend as it's not meaningful in this context
    )
    fig_service.show()
    time.sleep(1)  # Add delay after showing

def display_server_utilizations(customers, num_servers, total_simulation_time):
    server_timelines = [set() for _ in range(num_servers)]

    for customer in customers:
        if customer.server_id is not None:
            for i in range(len(customer.start_times)):
                if i < len(customer.end_times):
                    for t in range(int(customer.start_times[i]), int(customer.end_times[i])):
                        server_timelines[customer.server_id].add(t)

    table = Table(title="Server Utilizations", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Server ID", style="cyan", justify="center")
    table.add_column("Utilization (%)", justify="center")

    for i, timeline in enumerate(server_timelines):
        if total_simulation_time > 0:
            busy_time = len(timeline)
            utilization = (busy_time / total_simulation_time) * 100
            table.add_row(f"Server {i + 1}", f"{utilization:.2f}")

    console.print(table, justify='center')

def print_customer_table(customer_list):
    table = Table(title="Final Customer Table", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Customer ID", style="cyan", justify="center")
    table.add_column("Arrival Time", justify="center")
    table.add_column("Service Time", justify="center")
    table.add_column("Priority", justify="center")
    table.add_column("Start Time", justify="center")
    table.add_column("End Time", justify="center")
    table.add_column("Turn Around Time", justify="center")
    table.add_column("Wait Time", justify="center")
    table.add_column("Response Time", justify="center")
    table.add_column("Server", justify="center")

    for customer in customer_list:
        server_display = f"Server {customer.server_id + 1}" if customer.server_id is not None else "None"
        table.add_row(
            str(customer.customer_id),
            str(customer.arrival_time),
            str(customer.burst_time),
            str(customer.priority),
            str(customer.start_time),
            str(customer.end_time),
            str(customer.turn_around_time),
            str(customer.wait_time),
            str(customer.response_time),
            server_display
        )
    console.print(table, justify='center')

def print_customer_table_FCFS(customer_list):
    table = Table(title="Final Customer Table", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Customer ID", style="cyan", justify="center")
    table.add_column("Arrival Time", justify="center")
    table.add_column("Service Time", justify="center")
    table.add_column("Start Time", justify="center")
    table.add_column("End Time", justify="center")
    table.add_column("Turn Around Time", justify="center")
    table.add_column("Wait Time", justify="center")
    table.add_column("Server", justify="center")

    for customer in customer_list:
        server_display = f"Server {customer.server_id + 1}" if customer.server_id is not None else "None"
        table.add_row(
            str(customer.customer_id),
            str(customer.arrival_time),
            str(customer.burst_time),
            str(customer.start_time),
            str(customer.end_time),
            str(customer.turn_around_time),
            str(customer.wait_time),
            server_display
        )
    console.print(table, justify='center')

def print_customer_average_table(customer_list, simulation_type):
    table = Table(title="Average Metrics", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Metric", style="cyan", justify="center")
    table.add_column("Value", justify="center")

    avg_turnaround = mean([customer.turn_around_time for customer in customer_list])
    avg_wait = mean([customer.wait_time for customer in customer_list])
    avg_response = mean([customer.response_time for customer in customer_list])
    avg_service = mean([customer.burst_time for customer in customer_list])
    
    arrivals = sorted([customer.arrival_time for customer in customer_list])
    total_interarrival_time = arrivals[-1] - arrivals[0]
    num_intervals = len(arrivals)
    avg_interarrival = total_interarrival_time / num_intervals if num_intervals > 0 else 0
    simulation_type = int(simulation_type)
    if simulation_type == 1:
        metrics = {
            "Avg InterArrival Time": avg_interarrival,
            "Avg Service Time": avg_service,
            "Avg Turn Around Time": avg_turnaround,
            "Avg Wait Time": avg_wait,
            "Avg Response Time": avg_response
        }
    else: 
        metrics = {
        "Avg InterArrival Time": avg_interarrival,
        "Avg Service Time": avg_service,
        "Avg Turn Around Time": avg_turnaround,
        "Avg Wait Time": avg_wait
    }

    for metric, value in metrics.items():
        table.add_row(metric, f"{value:.2f}")

    console.print(table, justify='center')

def print_customer_average_table_by_priority(customer_list):
    table = Table(title="Average Metrics by Priority", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Priority", style="cyan", justify="center")
    table.add_column("Avg InterArrival Time", justify="center")
    table.add_column("Avg Service Time", justify="center")
    table.add_column("Avg Turn Around Time", justify="center")
    table.add_column("Avg Wait Time", justify="center")
    table.add_column("Avg Response Time", justify="center")

    priorities = sorted(set(customer.priority for customer in customer_list))
    
    for priority in priorities:
        filtered_customers = [c for c in customer_list if c.priority == priority]
        
        avg_turnaround = mean([c.turn_around_time for c in filtered_customers])
        avg_wait = mean([c.wait_time for c in filtered_customers])
        avg_response = mean([c.response_time for c in filtered_customers])
        avg_service = mean([c.burst_time for c in filtered_customers])
        avg_interarrival = mean([c.interarrival for c in filtered_customers])

        table.add_row(
            str(priority),
            f"{avg_interarrival:.2f}",
            f"{avg_service:.2f}",
            f"{avg_turnaround:.2f}",
            f"{avg_wait:.2f}",
            f"{avg_response:.2f}"
        )

    console.print(table, justify='center')

def display_metrics_table(L, Lq, W, Wq):
    table = Table(title="Queueing System Metrics", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Metric", style="cyan", justify="center")
    table.add_column("Value", justify="center")

    metrics = {
        "Average number of customers in the system (L)": L,
        "Average number of customers in the queue (Lq)": Lq,
        "Average time a customer spends in the system (W)": W,
        "Average time a customer spends waiting in the queue (Wq)": Wq
    }

    for metric, value in metrics.items():
        table.add_row(metric, f"{value:.2f}")

    console.print(table, justify='center')

def calculate_metrics(customers, num_servers, total_simulation_time):
    total_customers = len(customers)

    # Calculate L (average number of customers in the system)
    total_time_in_system = sum(customer.turn_around_time for customer in customers)
    L = total_time_in_system / total_simulation_time if total_simulation_time > 0 else 0

    # Calculate Lq (average number of customers in the queue)
    total_time_in_queue = sum(customer.wait_time for customer in customers)
    Lq = total_time_in_queue / total_simulation_time if total_simulation_time > 0 else 0

    # Calculate W (average time a customer spends in the system)
    W = total_time_in_system / total_customers if total_customers > 0 else 0

    # Calculate Wq (average time a customer spends waiting in the queue)
    Wq = total_time_in_queue / total_customers if total_customers > 0 else 0

    display_metrics_table(L, Lq, W, Wq)

def seconds_to_timestamp(seconds):
    timestamp = datetime.fromtimestamp(seconds)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def draw_gantt_chart(customer_list):
    import time
    data_frame_list = []

    x_axis_tickvals = []
    for customer in customer_list:
        min_length = min(len(customer.start_times), len(customer.end_times))
        for i in range(min_length):
            data_frame_list.append(dict(customer=str(customer.customer_id), Start=seconds_to_timestamp(
                customer.start_times[i]), Finish=seconds_to_timestamp(customer.end_times[i])))
            x_axis_tickvals.append(seconds_to_timestamp(customer.start_times[i]))
            x_axis_tickvals.append(seconds_to_timestamp(customer.end_times[i]))
    df = pd.DataFrame(data_frame_list)

    fig = px.timeline(df, x_start="Start", x_end="Finish",
                      y="customer", color="customer")
    fig.update_layout(xaxis=dict(title='Time Passed (seconds)', tickformat='%S', tickvals=x_axis_tickvals), yaxis=dict(title='customers', tickvals=[customer.customer_id for customer in customer_list]))
    fig.show()
    time.sleep(1)  # Add delay after showing

def log_customer_timing(customer, event, time_passed):
    print(f"customer {customer.customer_id} - Event: {event}, Time: {time_passed}, Start Times: {customer.start_time}, End Times: {customer.end_time}")

def serve_highest_priority_first(customers, num_servers, preemptive=True):
    metrics_collector = QueueMetricsCollector()
    servers = [Server(server_id=i) for i in range(num_servers)]
    time_passed = 0
    
    while check_should_service_proceed(customers):
        ready_queue = [p for p in customers if p.arrival_time <= time_passed and p.time_left > 0]
        
        ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
        
        if preemptive:
            for server in servers:
                if server.current_customer and ready_queue:
                    highest_priority_waiting = ready_queue[0].priority
                    if highest_priority_waiting < server.current_customer.priority:
                        current_customer = server.current_customer
                        current_customer.append_end_times(time_passed)
                        current_customer.server_id = None
                        server.current_customer = None
                        ready_queue.append(current_customer)
                        ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
        
        for server in servers:
            if server.current_customer is None and ready_queue:
                assigned_customers = [s.current_customer for s in servers if s.current_customer is not None]
                next_customer = None
                for customer in ready_queue:
                    if customer not in assigned_customers:
                        next_customer = customer
                        break
                
                if next_customer:
                    server.current_customer = next_customer
                    next_customer.server_id = server.server_id
                    ready_queue.remove(next_customer)
                    if not server.current_customer.is_ready:
                        server.current_customer.set_response_time(time_passed)
                        server.current_customer.set_start_time(time_passed)
                        server.current_customer.is_ready = True
                    server.current_customer.append_start_times(time_passed)
        
        active_servers = [server for server in servers if server.current_customer]
        metrics_collector.collect_metrics(ready_queue, active_servers, time_passed, customers)
        if not active_servers and not ready_queue:
            time_passed += 1
            continue
            
        for server in active_servers:
            server.current_customer.decrement_time_left()
            if server.current_customer.time_left == 0:
                server.current_customer.set_end_time(time_passed + 1)
                server.current_customer.set_completion_time(time_passed + 1)
                server.current_customer.set_turn_around_time()
                server.current_customer.set_wait_time()
                server.current_customer.set_utilization_time()
                server.current_customer.append_end_times(time_passed + 1)
                server.current_customer = None

        time_passed += 1
    
    print_customer_table(customers)
    # Plot the collected metrics
    metrics_collector.plot_metrics()
    
    return time_passed

def serve_first_come_first_serve(customers, num_servers):
    metrics_collector = QueueMetricsCollector()
    servers = [Server(server_id=i) for i in range(num_servers)]
    time_passed = 0
        
    while check_should_service_proceed(customers):
        ready_queue = [p for p in customers if p.arrival_time <= time_passed and p.time_left > 0]
        
        ready_queue.sort(key=lambda p: p.arrival_time)
        
        for server in servers:
            if server.current_customer is None and ready_queue:
                assigned_customers = [s.current_customer for s in servers if s.current_customer is not None]
                next_customer = None
                for customer in ready_queue:
                    if customer not in assigned_customers:
                        next_customer = customer
                        break
                
                if next_customer:
                    server.current_customer = next_customer
                    next_customer.server_id = server.server_id
                    ready_queue.remove(next_customer)
                    if not server.current_customer.is_ready:
                        server.current_customer.set_response_time(time_passed)
                        server.current_customer.set_start_time(time_passed)
                        server.current_customer.is_ready = True
                    server.current_customer.append_start_times(time_passed)
        
        active_servers = [server for server in servers if server.current_customer]
        metrics_collector.collect_metrics(ready_queue, active_servers, time_passed, customers)
        if not active_servers and not ready_queue:
            time_passed += 1
            continue
            
        for server in active_servers:
            server.current_customer.decrement_time_left()
            if server.current_customer.time_left == 0:
                server.current_customer.set_end_time(time_passed + 1)
                server.current_customer.set_completion_time(time_passed + 1)
                server.current_customer.set_turn_around_time()
                server.current_customer.set_wait_time()
                server.current_customer.set_utilization_time()
                server.current_customer.append_end_times(time_passed + 1)
                server.current_customer = None

        time_passed += 1

    print_customer_table_FCFS(customers)
    metrics_collector.plot_metrics()
    
    return time_passed
    

if __name__ == "__main__":
    console.print("[bold green] Simulation Type:[/bold green][blue]\n1: Priority-Based\n2: FCFS[/blue]", justify='center')
    simulation_type = console.input("[cyan]Enter your choice: [/cyan]")
    
    if simulation_type == "1":
        console.print("[yellow]Simulate with preemption?[/yellow] [italic](y/n)[/italic]")
        preemption_choice = console.input("[cyan]Enter your choice: [/cyan]").strip().lower()
        preemptive = preemption_choice == "y"
    else:
        preemptive = False

    End_time = int(console.input("[cyan]Enter the time to run simulator: [/cyan]"))
    console.print("[green]Arrival Distribution Choices:[/green]")
    arrival_distribution_choice = int(
        console.input("[cyan]Enter your choice (1-Exponential, 2-Normal, 3-Gamma, 4-Uniform): [/cyan]")
    )
    arrivalTimes = getArrivalTimes(arrival_distribution_choice, End_time)

    console.print("[green]Service Distribution Choices:[/green]")
    service_distribution_choice = int(
        console.input("[cyan]Enter your choice (1-Exponential, 2-Normal, 3-Gamma, 4-Uniform): [/cyan]")
    )
    serviceTimes = getServiceTimes(len(arrivalTimes["arrivalTimes"]), service_distribution_choice)

    num_servers = int(console.input("[cyan]Enter the number of servers: [/cyan]"))

    if simulation_type == "1":
        priorities = getPriorities(len(arrivalTimes["arrivalTimes"]))
        display(arrivalTimes, serviceTimes, priorities, simulation_type)
        customers = [
            customer(
                i + 1,
                arrivalTimes["arrivalTimes"][i],
                serviceTimes[i],
                priorities[i],
                arrivalTimes["interArrivals"][i],  # Now using the correct interArrivals list
            )
            for i in range(len(arrivalTimes["arrivalTimes"]))
        ]
        end_time = serve_highest_priority_first(customers, num_servers, preemptive=preemptive)
    else:
        display(arrivalTimes, serviceTimes, [0] * len(arrivalTimes["arrivalTimes"]), simulation_type)
        customers = [
            customer(
                i + 1,
                arrivalTimes["arrivalTimes"][i],
                serviceTimes[i],
                0,
                arrivalTimes["interArrivals"][i],  # Now using the correct interArrivals list
            )
            for i in range(len(arrivalTimes["arrivalTimes"]))
        ]
        end_time = serve_first_come_first_serve(customers, num_servers)

    # Plot distributions and display metrics
    print_customer_average_table(customers, simulation_type)
    if simulation_type == "1":
        print_customer_average_table_by_priority(customers)
    plot_distributions(arrivalTimes["interArrivals"], serviceTimes)
    display_server_utilizations(customers, num_servers, end_time)
    calculate_metrics(customers, num_servers, end_time)
    draw_gantt_chart(customers)
