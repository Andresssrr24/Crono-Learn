import { useState } from "react";
import { supabase } from "../../services/supabase";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";

export function Register() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const signup = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setMessage("");

        const { error: signUpError } = await supabase.auth.signUp({
            email,  
            password       
        });

        if (signUpError) {
            setError(signUpError.message);
        } else {
            setMessage("Register done. Please check your mail for account validation.")
            toast('If doesn`t work try logging in, maybe you`re already registered', {
                icon: '😉',
            });
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen">

            <form onSubmit={signup} className="bg-stone-900 p-7 rounded-3xl shadow-md w-96">
                <h1 className="text-3xl text-center p-4 font-bold">Register</h1>
                
                {message && <p className="text-green-500 mb-4">{message}</p>}
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
                        className="w-full bg-emerald-950 border text-white p-2 rounded-xl hover:bg-emerald-800"
                    >
                        Sign Up
                    </button>
                </div>
                
            </form>
        </div>
    );
}