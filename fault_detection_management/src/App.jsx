import { useState, useEffect } from 'react'
import '@fontsource/roboto/300.css';
import Typography from '@mui/material/Typography';
import AlarmTable from './components/AlarmTable';
import FaultAlarmTable from './components/FaultAlarmTable';
import { getActiveAlarms, getActiveFaultAlarms } from './components/service';
import './App.css'

import { supabase } from './SupabaseClient';


function App() {
  const [alarms, setAlarms] = useState([]);
  const [faultAlarms, setFaultAlarms] = useState([]);

  useEffect(() => {
    async function fetchAlarms() {
      try {
        const response = await getActiveAlarms();
        const data = response.data;

        const formattedRows = data.map(alarm => ({
          room: alarm.room_no || 'N/A',
          device_type: alarm.device_type || 'Unknown',
          fault_status: alarm.fault_status || 'Unknown',
          fault_type: alarm.fault_type || '-',
          fault_time: alarm.triggered_at || '-',
        }));

        setAlarms(formattedRows);
      } catch (error) {
        console.error('Error fetching alarms:', error);
      }
    }

    fetchAlarms();
  }, []);

  useEffect(() => {
    async function fetchFaultAlarms() {
      try {
        const response = await getActiveFaultAlarms();
        const data = response.data;

        const formattedRows = data.map(alarm => ({
          room: alarm.room_no || 'N/A',
          device_type: alarm.device_type || 'Unknown',
          fault_status: alarm.fault_status || 'Unknown',
          fault_type: alarm.fault_type || '-',
          fault_time: alarm.triggered_at || '-',
        }));

        setFaultAlarms(formattedRows);
      } catch (error) {
        console.error('Error fetching fault alarms:', error);
      }
    }

    fetchFaultAlarms();

    // Subscribe to new alert inserts
    const channel = supabase
      .channel('realtime')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'faultDetection_activefaultalert',
        },
        (payload) => {
          console.log('New alert inserted:', payload.new)
          // Re-fetch from API for latest state
          fetchFaultAlarms()
        }
      )
      .subscribe()

    // Clean up on unmount
    return () => {
      supabase.removeChannel(channel)
    }
  }, []);

  return (
    <>
      <Typography
        variant="h4"
        gutterBottom
        sx={{ 'backgroundColor': '#00619a', 'color': 'white', p: 2, borderRadius: 3 }}
      >
        Fault Detection and Diagnostic (AFDD)
      </Typography>

      <AlarmTable alarms={alarms} />

      <FaultAlarmTable faultAlarms={faultAlarms} />
    </>
  )
}

export default App
