import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../services/supabase";

export function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const login = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        if (error) {
            setError(error.message);
        } else {
            navigate("/");
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen">
            <form onSubmit={login} className="bg-stone-900 p-7 rounded-3xl shadow-md w-96">
                <h1 className="text-3xl text-center p-4 font-bold">Welcome Back!</h1>
                {error && <p className="text-red-500 mb-4">{error}</p>}
                <div className="mb-4 mt-5">
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="w-full p-2 border rounded-lg"
                        placeholder="Email"
                    />
                </div>
                <div className="mb-4">
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="text-neutral-50 w-full p-2 border rounded-lg"
                        placeholder="Password"
                    />
                </div>
                <div className="mt-10">
                    <button
                        type="submit"
                        className="w-full bg-slate-950 text-white p-2 rounded-xl hover:bg-blue-950"
                    >
                        Log in
                    </button>
                </div>
                <div className="absolute bottom-0 right-0 text-white">
                    Sign up
                </div>
            </form>
        </div>
    )
}