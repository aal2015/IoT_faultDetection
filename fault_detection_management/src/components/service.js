import axios from "axios";

const baseURL = 'http://localhost:8000/fault-detection/';

export async function getActiveAlarms() {
    const response = await axios.get(
        // `${baseURL}active-alarms/`,
        `${baseURL}active-alarms/`,
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return response;
}

export async function getActiveFaultAlarms() {
    const response = await axios.get(
        // `${baseURL}active-alarms/`,
        `${baseURL}active-fault-alarms/`,
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return response;
}