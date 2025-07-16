import axios from "axios";
import { supabase } from "../supabase";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

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
    const {
        data: { session },
        error,
    } = await supabase.auth.getSession();

    if (error || !session?.access_token) {
        throw new Error("User is not authenticated.");
    }

    try {
        console.log({ task_name, timer, rest_time });
        const response = await axios.post(
            `${BACKEND_URL}/pomodoro/`,
            { task_name, timer, rest_time, status },
            {
                headers: {
                    Authorization: `Bearer ${session.access_token}`,
                    "Content-Type": "application/json",
                },
            }
        );

        return response.data;
    } catch (err: any) {
        const message = err.response?.data?.detail || err.message || "Error creating pomodoro.";
        throw new Error(message);
    }
}

export async function updatePomodoro(id: number, updates: Partial<{
    task_name: string;
    timer: number;
    rest_time: number;
    status: string;
}>) {
    const {
        data: { session },
        error,
    } = await supabase.auth.getSession();

    if (error || !session?.access_token) {
        throw new Error("User is not authenticated");
    }

    try {
        const response = await axios.patch(
            `${BACKEND_URL}/pomodoro/${id}`,
            updates,
            {
                headers: {
                    Authorization: `Bearer ${session.access_token}`,
                    "Content-type": "application/json",
                },
            }            
        );
        return response.data;
    } catch (err: any) {
        const message = err.response?.data?.detail || err.message || "Error updating pomodoro.";
        throw new Error(message);
    }
}