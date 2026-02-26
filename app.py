from flask import Flask, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# Load CSV files
data_path = r"c:\Users\Saurabh Tripathi\Downloads\archive (10)"
patients_df = pd.read_csv(os.path.join(data_path, "patients.csv"))
services_df = pd.read_csv(os.path.join(data_path, "services_weekly.csv"))
staff_df = pd.read_csv(os.path.join(data_path, "staff.csv"))
schedule_df = pd.read_csv(os.path.join(data_path, "staff_schedule.csv"))

NAV = """
<nav class="navbar navbar-expand-lg navbar-dark" style="background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);">
    <div class="container">
        <a class="navbar-brand" href="/">🏥 Hospital Dashboard</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item"><a class="nav-link {% if page == 'home' %}active{% endif %}" href="/">Dashboard</a></li>
                <li class="nav-item"><a class="nav-link {% if page == 'patients' %}active{% endif %}" href="/patients">Patients</a></li>
                <li class="nav-item"><a class="nav-link {% if page == 'services' %}active{% endif %}" href="/services">Services</a></li>
                <li class="nav-item"><a class="nav-link {% if page == 'staff' %}active{% endif %}" href="/staff">Staff</a></li>
            </ul>
        </div>
    </div>
</nav>
"""

HEAD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hospital Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI';
        }
        .navbar { box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card { border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-radius: 12px; transition: transform 0.3s; margin-bottom: 20px; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; }
        .stat-card h3 { margin-top: 10px; font-size: 28px; font-weight: 700; }
        .page-header { background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px 0; margin-bottom: 30px; border-radius: 12px; }
        .chart-container { position: relative; height: 350px; margin-bottom: 30px; }
        .table-container { max-height: 600px; overflow-y: auto; }
        .nav-link.active { color: #3498db !important; border-bottom: 3px solid #3498db; }
    </style>
</head>
<body>
"""

FOOTER = """
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def home():
    total_patients = len(patients_df)
    total_staff = len(staff_df)
    total_beds = int(services_df['available_beds'].sum())
    avg_satisfaction = round(patients_df['satisfaction'].mean(), 1)
    
    service_counts = patients_df['service'].value_counts()
    service_labels = [s.replace('_', ' ').title() for s in service_counts.index]
    
    sat_by_service = services_df.groupby('service')['patient_satisfaction'].mean()
    sat_labels = [s.replace('_', ' ').title() for s in sat_by_service.index]
    sat_data = [round(x, 1) for x in sat_by_service.values]
    
    weekly_metrics = services_df.head(10)
    
    html = HEAD + NAV + """
    <div class="container mt-5">
        <div class="page-header">
            <h1>📊 Hospital Management Dashboard</h1>
            <p>Real-time monitoring and analytics</p>
        </div>

        <div class="row">
            <div class="col-md-3">
                <div class="stat-card">
                    <span style="font-size: 40px;">👥</span>
                    <h3>{{ total_patients }}</h3>
                    <p>Total Patients</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <span style="font-size: 40px;">👨‍⚕️</span>
                    <h3>{{ total_staff }}</h3>
                    <p>Staff Members</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <span style="font-size: 40px;">🛏️</span>
                    <h3>{{ total_beds }}</h3>
                    <p>Available Beds</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                    <span style="font-size: 40px;">😊</span>
                    <h3>{{ avg_satisfaction }}%</h3>
                    <p>Avg Satisfaction</p>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5>Patient by Service</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="serviceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5>Satisfaction by Service</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="satisfactionChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-header bg-success text-white">
                <h5>Weekly Service Metrics</h5>
            </div>
            <div class="card-body table-container">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Service</th>
                            <th>Beds</th>
                            <th>Admitted</th>
                            <th>Refused</th>
                            <th>Satisfaction</th>
                            <th>Morale</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for _, row in weekly_metrics.iterrows() %}
                        <tr>
                            <td><span class="badge bg-info">W{{ row['week'] }}</span></td>
                            <td><strong>{{ row['service'].replace('_', ' ').title() }}</strong></td>
                            <td>{{ row['available_beds'] }}</td>
                            <td><span class="badge bg-success">{{ row['patients_admitted'] }}</span></td>
                            <td><span class="badge bg-danger">{{ row['patients_refused'] }}</span></td>
                            <td>{{ row['patient_satisfaction'] }}%</td>
                            <td>{{ row['staff_morale'] }}%</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
    const serviceCtx = document.getElementById('serviceChart').getContext('2d');
    new Chart(serviceCtx, {
        type: 'doughnut',
        data: {
            labels: {{ service_labels|tojson }},
            datasets: [{
                data: {{ service_counts|tojson }},
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const satCtx = document.getElementById('satisfactionChart').getContext('2d');
    new Chart(satCtx, {
        type: 'bar',
        data: {
            labels: {{ sat_labels|tojson }},
            datasets: [{
                label: 'Satisfaction %',
                data: {{ sat_data|tojson }},
                backgroundColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { max: 100 } }
        }
    });
    </script>
    """ + FOOTER
    
    return render_template_string(html, 
        page='home',
        total_patients=total_patients,
        total_staff=total_staff,
        total_beds=total_beds,
        avg_satisfaction=avg_satisfaction,
        service_labels=service_labels,
        service_counts=service_counts.values.tolist(),
        sat_labels=sat_labels,
        sat_data=sat_data,
        weekly_metrics=weekly_metrics
    )

@app.route('/patients')
def patients():
    total = len(patients_df)
    avg_age = round(patients_df['age'].mean(), 1)
    avg_sat = round(patients_df['satisfaction'].mean(), 1)
    
    html = HEAD + NAV + """
    <div class="container mt-5">
        <div class="page-header">
            <h1>👥 Patients Management</h1>
        </div>
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="stat-card">
                    <h3>{{ total }}</h3>
                    <p>Total Patients</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <h3>{{ avg_age }}</h3>
                    <p>Avg Age</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <h3>{{ avg_sat }}%</h3>
                    <p>Avg Satisfaction</p>
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5>Patient Records</h5>
            </div>
            <div class="card-body table-container">
                <table class="table table-hover table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Age</th>
                            <th>Service</th>
                            <th>Arrival</th>
                            <th>Departure</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for _, p in patients_data.iterrows() %}
                        <tr>
                            <td><small>{{ p['patient_id'][:10] }}</small></td>
                            <td>{{ p['name'] }}</td>
                            <td>{{ p['age'] }}</td>
                            <td><span class="badge bg-info">{{ p['service'].replace('_', ' ').title() }}</span></td>
                            <td>{{ p['arrival_date'] }}</td>
                            <td>{{ p['departure_date'] }}</td>
                            <td><span class="badge bg-success">{{ p['satisfaction'] }}%</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """ + FOOTER
    
    return render_template_string(html, page='patients', total=total, avg_age=avg_age, avg_sat=avg_sat, patients_data=patients_df.head(30))

@app.route('/services')
def services():
    total_beds = int(services_df['available_beds'].sum())
    total_adm = int(services_df['patients_admitted'].sum())
    total_ref = int(services_df['patients_refused'].sum())
    
    html = HEAD + NAV + """
    <div class="container mt-5">
        <div class="page-header">
            <h1>🏥 Services Management</h1>
        </div>
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="stat-card">
                    <h3>{{ beds }}</h3>
                    <p>Total Beds</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <h3>{{ adm }}</h3>
                    <p>Total Admitted</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <h3>{{ ref }}</h3>
                    <p>Total Refused</p>
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5>Service Metrics</h5>
            </div>
            <div class="card-body table-container">
                <table class="table table-hover table-striped">
                    <thead>
                        <tr>
                            <th>Week</th>
                            <th>Service</th>
                            <th>Beds</th>
                            <th>Requests</th>
                            <th>Admitted</th>
                            <th>Refused</th>
                            <th>Satisfaction</th>
                            <th>Morale</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for _, s in services_data.iterrows() %}
                        <tr>
                            <td><span class="badge bg-info">{{ s['week'] }}</span></td>
                            <td><strong>{{ s['service'].replace('_', ' ').title() }}</strong></td>
                            <td>{{ s['available_beds'] }}</td>
                            <td>{{ s['patients_request'] }}</td>
                            <td><span class="badge bg-success">{{ s['patients_admitted'] }}</span></td>
                            <td><span class="badge bg-danger">{{ s['patients_refused'] }}</span></td>
                            <td>{{ s['patient_satisfaction'] }}%</td>
                            <td>{{ s['staff_morale'] }}%</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """ + FOOTER
    
    return render_template_string(html, page='services', beds=total_beds, adm=total_adm, ref=total_ref, services_data=services_df.head(40))

@app.route('/staff')
def staff():
    total = len(staff_df)
    docs = len(staff_df[staff_df['role'] == 'doctor'])
    nurses = len(staff_df[staff_df['role'] == 'nurse'])
    att = round((schedule_df['present'].sum() / len(schedule_df) * 100), 1)
    
    html = HEAD + NAV + """
    <div class="container mt-5">
        <div class="page-header">
            <h1>👨‍⚕️ Staff Management</h1>
        </div>
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-card">
                    <h3>{{ total }}</h3>
                    <p>Total Staff</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <h3>{{ docs }}</h3>
                    <p>Doctors</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <h3>{{ nurses }}</h3>
                    <p>Nurses</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                    <h3>{{ att }}%</h3>
                    <p>Attendance</p>
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5>Staff Records</h5>
            </div>
            <div class="card-body table-container">
                <table class="table table-hover table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Role</th>
                            <th>Service</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for _, m in staff_data.iterrows() %}
                        <tr>
                            <td><small>{{ m['staff_id'][:10] }}</small></td>
                            <td>{{ m['staff_name'] }}</td>
                            <td>
                                {% if m['role'] == 'doctor' %}
                                <span class="badge bg-primary">Doctor</span>
                                {% else %}
                                <span class="badge bg-info">Nurse</span>
                                {% endif %}
                            </td>
                            <td><span class="badge bg-warning">{{ m['service'].replace('_', ' ').title() }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """ + FOOTER
    
    return render_template_string(html, page='staff', total=total, docs=docs, nurses=nurses, att=att, staff_data=staff_df)

if __name__ == '__main__':
    print("🏥 Starting Hospital Dashboard...")
    print("📍 Open http://localhost:8000 in your browser")
    app.run(debug=True, port=8000)
