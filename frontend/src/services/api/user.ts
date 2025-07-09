import { supabase } from "../supabase";
import axios from "axios";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function registerUser() {
    const {
        data: { session },
        error,
    } = await supabase.auth.getSession();

    if (error || !session) {
        throw new Error("User is not authenticated.");
    }

    const token = session.access_token;

    if (!token) throw new Error("No token found, please log in first.");

    try {
        const response = await axios.post(
            `${BACKEND_URL}/users/register`,
            {},
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            }
        );

        return response.data;
    } catch (err: any) {
        const message = err.response?.data?.detail || err.message || "Error registering user.";
        throw new Error(message);
    }
}
