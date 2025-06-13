import React, { useEffect, useState, useRef } from 'react';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { KPIData } from '../types'; 

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884d8"];

const Dashboard: React.FC = () => {
  const [apiData, setApiData] = useState<KPIData | null>(null); 
  const [error, setError] = useState<string | null>(null);
  const hasFetchedData = useRef(false);

  useEffect(() => {
    const fetchDataAndShutdown = async () => {
      // Prevent multiple calls
      if (hasFetchedData.current) {
        return;
      }
      hasFetchedData.current = true;

      try {
        // Fetch KPI data from the backend
        const response = await fetch('/api/kpi_data');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: KPIData = await response.json(); 
        setApiData(data);

        // Call shutdown API after successfully fetching and setting KPI data
        try {
          const shutdownResponse = await fetch('/api/shutdown', { method: 'POST' });
          if (!shutdownResponse.ok) {
            console.error(`Shutdown API HTTP error! status: ${shutdownResponse.status}`);
          } else {
            console.log('Backend shutdown initiated.');
          }
        } catch (shutdownError) {
          console.error("Failed to call shutdown backend:", shutdownError);
        }

      } catch (e) {
        if (e instanceof Error) {
            setError(e.message);
        } else {
            setError('An unknown error occurred');
        }
        console.error("Failed to fetch KPI data:", e);
      }
    };

    fetchDataAndShutdown();
  }, []); // Empty dependency array ensures this runs only once on mount



  if (error) {
    return <div className="dashboard-container error-message">Error loading dashboard: {error}</div>;
  }

  if (!apiData) {
    return <div className="dashboard-container loading-message">Loading dashboard data...</div>;
  }

  const { 
    total_allocations,
    average_allocation_time,
    simulation_length,
    incident_distribution,
    resource_distribution,
    allocation_details 
  } = apiData;

  // Prepare chart data from apiData properties
  const resourceChartData = resource_distribution.map(item => ({ name: item.name, value: parseFloat(item.value) }));
  const incidentChartData = incident_distribution.map(item => ({ name: item.name, value: parseFloat(item.value) }));

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <span className="header-icon">📍</span>
          <h1>Resource Allocation Dashboard</h1>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="kpi-cards">
          <div className="card">
            <div className="card-header">
              <h5>Total Allocations</h5>
              <span className="card-icon">📊</span>
            </div>
            <div className="card-content">
              <div className="kpi-value">{total_allocations}</div>
              <p className="kpi-description">Resource allocations tracked</p>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h5>Average Response Time</h5>
              <span className="card-icon">⏰</span>
            </div>
            <div className="card-content">
              <div className="kpi-value">{parseFloat(average_allocation_time).toFixed(2)}s</div>
              <p className="kpi-description">Across all resource types</p>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h5>Simulation Length</h5> 
              <span className="card-icon">⚠️</span>
            </div>
            <div className="card-content">
              <div className="kpi-value">{simulation_length}</div>
              <p className="kpi-description">seconds</p>
            </div>
          </div>
        </div>

        <div className="charts-section">
          <div className="charts-grid">
            <div className="card">
              <div className="card-header">
                <h5>Resource Distribution</h5>
                <p className="card-description">Allocation by resource type</p>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={resourceChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {resourceChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h5>Incident Types</h5>
                <p className="card-description">Distribution by incident category</p>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={incidentChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {incidentChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

        <div className="card table-card">
          <div className="card-header">
            <h5>Resource Allocation Data</h5>
            <p className="card-description">Complete list of all resource allocations</p>
          </div>
          <div className="card-content">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Allocation ID</th>
                    <th>Resource Type</th>
                    <th>Incident Type</th>
                    <th>Severity</th>
                    <th>Allocation Time (s)</th>
                  </tr>
                </thead>
                <tbody>
                  {allocation_details.map((row) => (
                    <tr key={row.allocation_id}>
                      <td>{row.allocation_id}</td>
                      <td>{row.resource_type}</td>
                      <td>{row.incident_type}</td>
                      <td>{row.severity}</td>
                      <td>{parseFloat(row.allocation_time_seconds).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="back-button-container">
          <a href="http://127.0.0.1:5500/src/frontend/index.html" className="back-button">
            ← Back to Home
          </a>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;