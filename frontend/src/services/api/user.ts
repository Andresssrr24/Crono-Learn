import { supabase } from "../supabase";
import axios from "axios";

const BACKEND_URL = "http://localhost:8000/api/v1";

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

    const res = await fetch(`${BACKEND_URL}/users/`, {
        method: "POST",
         headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
         },
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Error registering user, try again later.");
    }

    return res.json();
}