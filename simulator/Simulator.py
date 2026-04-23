import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import io
import base64


def get_distribution_input(name):
    """Prompt user for distribution type using numbered options."""
    distributions = {
        1: "exponential",
        2: "normal",
        3: "uniform",
        4: "gamma"
    }

    print(f"\nChoose {name} distribution:")
    for key, value in distributions.items():
        print(f"{key}. {value.capitalize()}")

    choice = int(input(f"Enter the number for {name} distribution: ").strip())
    if choice not in distributions:
        raise ValueError("Invalid choice. Please select a valid number.")

    dist = distributions[choice]
    params = {}

    if dist == 'exponential':
        params['scale'] = float(input("Enter scale (mean): "))
    elif dist == 'normal':
        params['mean'] = float(input("Enter mean: "))
        params['std'] = float(input("Enter standard deviation: "))
    elif dist == 'uniform':
        params['low'] = float(input("Enter minimum value: "))
        params['high'] = float(input("Enter maximum value: "))
    elif dist == 'gamma':
        params['shape'] = float(input("Enter shape parameter: "))
        params['scale'] = float(input("Enter scale parameter: "))

    return dist, params


def generate_times(distribution, params, size):
    """Generate times based on chosen distribution."""
    if distribution == 'exponential':
        return np.random.exponential(scale=params['scale'], size=size)
    elif distribution == 'normal':
        return np.random.normal(loc=params['mean'], scale=params['std'], size=size)
    elif distribution == 'uniform':
        return np.random.uniform(low=params['low'], high=params['high'], size=size)
    elif distribution == 'gamma':
        return np.random.gamma(shape=params['shape'], scale=params['scale'], size=size)


def simulate_queue_preemptive(inter_arrival_dist, service_dist, inter_arrival_params, service_params, num_servers, num_customers, preemptive=True):
    """Simulate a preemptive queue where customers with higher priority (lower number) preempt lower priority customers."""
    inter_arrival_times = generate_times(inter_arrival_dist, inter_arrival_params, num_customers)
    inter_arrival_times[0] = 0  # Ensure the first customer arrives at time 0
    arrival_times = np.cumsum(inter_arrival_times)
    service_times = generate_times(service_dist, service_params, num_customers)

    server_end_time = np.zeros(num_servers)  # Track when servers become available
    remaining_service = service_times.copy()  # Store remaining service times for each customer
    events = []  # List of service events
    # Priority queue, higher priority (lower number) comes first
    queue = []

    for i in range(num_customers):
        priority = np.random.randint(1, 4)  # Random priority between 1 and 3 (lower is higher priority)
        queue.append((arrival_times[i], i, priority))  # Add customer with arrival time, ID, and priority

        # Process the queue based on arrival times and priority
        queue.sort(key=lambda x: (int(x[2]), float(x[0])))  # Sort by priority and arrival time

        while queue:
            current_time, cust_id, cust_priority = queue.pop(0)
            server_id = np.argmin(server_end_time)  # Find the server with the earliest available time
            start_time = max(current_time, server_end_time[server_id])  # Service start time

            # Handle preemption: if a higher priority arrives while a lower priority is being served
            service_duration = remaining_service[cust_id]
            if preemptive and len(queue) > 0 and queue[0][2] < cust_priority:
                next_arrival, _, next_priority = queue[0]
                if next_priority < cust_priority:
                    service_duration = min(service_duration, next_arrival - start_time)
                    remaining_service[cust_id] -= service_duration
                    queue.append((start_time + service_duration, cust_id, cust_priority))  # Re-queue this customer
                    queue.sort(key=lambda x: (int(x[2]), float(x[0])))  # Re-sort the queue by priority

            end_time = start_time + service_duration
            server_end_time[server_id] = end_time  # Update server availability time
            events.append((cust_id, arrival_times[cust_id], inter_arrival_times[cust_id], service_times[cust_id], start_time, end_time, cust_priority))

    columns = ["Customer", "Arrival Time", "Inter-arrival Time", "Service Time", "Service Start", "Service End", "Priority"]
    return pd.DataFrame(events, columns=columns)



def plot_gantt(df, as_base64=False):
    """Plot a preemptive Gantt chart showing service interruptions."""
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = cm.get_cmap('tab20', df['Customer'].nunique())

    for _, row in df.iterrows():
        color = colors(row['Customer'] % 20)
        ax.broken_barh([(row['Service Start'], row['Service End'] - row['Service Start'])],
                       (10 * row['Customer'], 9), facecolors=color)
        if pd.notna(row['Priority']):
            ax.text(row['Service Start'] + (row['Service End'] - row['Service Start']) / 2, 10 * row['Customer'] + 4,
                    f"P{row['Priority']}", ha='center', va='center', color='white')

    ax.set_xlabel('Time')
    ax.set_ylabel('Customer')
    ax.set_yticks([10 * i + 4.5 for i in range(df['Customer'].nunique())])
    ax.set_yticklabels([f"Customer {i + 1}" for i in range(df['Customer'].nunique())])
    ax.grid(True)
    plt.title("Gantt Chart")
    
    if as_base64:
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64
    else:
        plt.show()


if __name__ == '__main__':
    # User inputs
    print("Welcome to the General Queue Simulator")
    num_customers = int(input("Enter the number of customers: "))
    num_servers = int(input("Enter the number of servers: "))
    preemptive = input("Is the system preemptive? (yes/no): ").strip().lower() == 'yes'

    inter_arrival_dist, inter_arrival_params = get_distribution_input("inter-arrival")
    service_dist, service_params = get_distribution_input("service")

    # Run simulation
    df = simulate_queue_preemptive(inter_arrival_dist, service_dist, inter_arrival_params, service_params, num_servers, num_customers, preemptive=preemptive)

    # Show all columns in the output
    pd.set_option('display.max_columns', None)

    print("\nSimulation Results:")
    print(df)

    # Plot Gantt chart
    plot_gantt(df)
