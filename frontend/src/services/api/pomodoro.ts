import axios from "axios";
import { supabase } from "../supabase";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

async function getHeaders() {
    const {
        data: { session },
        error,
    } = await supabase.auth.getSession();

    if (error || !session?.access_token) {
        throw new Error("User is not authenticated.");
    }

    return {
        Authorization: `Bearer ${session.access_token}`,
        "Content-Type": "application/json",
    }
}

export async function createPomodoro({
    task_name,
    timer,
    rest_time,
    status
}: {
    task_name: string;
    timer: number;
    rest_time: number;
    status: "running";
}) {
    try {
        console.log({ task_name, timer, rest_time });
        const headers = await getHeaders();
        const response = await axios.post(
            `${BACKEND_URL}pomodoro/`,
            { task_name, timer, rest_time, status },
            { headers }
        );

        return response.data;
    } catch (err: any) {
        const message = err.response?.data?.detail || err.message || "Error creating pomodoro.";
        throw new Error(message);
    }
}

export async function updatePomodoro(id: string, updates: Partial<{
    task_name: string;
    timer: number;
    rest_time: number;
    status: string;
}>) {
    try {
        const headers = await getHeaders();
        const response = await axios.patch(
            `${BACKEND_URL}/pomodoro/${id}`,
            updates,
            { headers }            
        );
        return response.data;
    } catch (err: any) {
        const message = err.response?.data?.detail || err.message || "Error updating pomodoro.";
        throw new Error(message);
    }
}

export const pausePomodoro = async (pomodoroId: string) => {
    try {
        const headers = await getHeaders();
        const res = await axios.post(
            `${BACKEND_URL}pomodoro/${pomodoroId}/pause`,
            {},
            { headers }
        );
        return res.data;
    } catch (err: any) {
        const message = err.response?.data?.detail || err.message || "Error pausing pomodoro.";
        throw new Error(message);
    }
};

export const stopPomodoro = async (pomodoroId: string) => {
    try {
        const headers = await getHeaders();
        const res = await axios.post(
            `${BACKEND_URL}pomodoro/${pomodoroId}/stop`,
            {},
            { headers }
        );
        return res.data;
    } catch (err: any ) {
        const message = err.response?.data?.detail || err.message || "Error stopping pomodoro.";
        throw new Error(message);
    }  
};

export const resumePomodoro = async (pomodoroId: string) => {
    try {
        const headers = await getHeaders();
        const res = await axios.post(
            `${BACKEND_URL}pomodoro/${pomodoroId}/resume`,
            {},
            { headers }
        );
        return res.data;
    } catch (err: any ) {
        const message = err.response?.data?.detail || err.message || "Error stopping pomodoro.";
        throw new Error(message);
    }  
};